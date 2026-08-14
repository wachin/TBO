from pathlib import Path

from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMessageBox

from tbo.formats.tbo_v1 import load
from tbo.ui.main_window import MainWindow


REPOSITORY_ROOT = Path(__file__).parents[3]


def test_window_opens_historical_tutorial(qtbot) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)

    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    assert window.canvas.comic is not None
    assert len(window.canvas.scene.items()) > 1
    assert window.windowTitle() == "tut — TBO 2"
    assert window.statusBar().currentMessage() == "Página 1 de 11"
    assert not window.previous_page_action.isEnabled()
    assert window.next_page_action.isEnabled()


def test_window_navigates_and_saves_copy(qtbot, tmp_path: Path) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")

    window.next_page()
    assert window.canvas.page_index == 1
    assert window.statusBar().currentMessage() == "Página 2 de 11"
    window.previous_page()
    assert window.canvas.page_index == 0

    target = tmp_path / "copy.tbo"
    assert window._save_to(target)
    assert target.is_file()
    assert window.windowTitle() == "copy — TBO 2"


def test_frame_edits_are_undoable_and_mark_document_modified(qtbot, tmp_path: Path) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    page = window.canvas.current_page
    assert page is not None
    original_count = len(page.frames)

    added = window.canvas.add_frame()
    assert added is not None
    assert len(page.frames) == original_count + 1
    assert window.windowTitle() == "tut * — TBO 2"

    old_position = (added.x, added.y)
    assert window.canvas.move_frame(added, (added.x + 25, added.y + 15))
    assert (added.x, added.y) == (old_position[0] + 25, old_position[1] + 15)

    window.canvas.undo_stack.undo()
    assert (added.x, added.y) == old_position
    window.canvas.undo_stack.undo()
    assert len(page.frames) == original_count
    assert window.windowTitle() == "tut — TBO 2"

    window.canvas.undo_stack.redo()
    assert len(page.frames) == original_count + 1
    assert window.canvas.select_frame(added)
    assert window.canvas.delete_selected_frame()
    assert len(page.frames) == original_count
    window.canvas.undo_stack.undo()
    assert len(page.frames) == original_count + 1

    saved_position = (added.x + 12, added.y + 8)
    assert window.canvas.move_frame(added, saved_position)
    target = tmp_path / "edited.tbo"
    assert window._save_to(target)
    restored = load(target)
    assert len(restored.pages[0].frames) == original_count + 1
    assert (restored.pages[0].frames[-1].x, restored.pages[0].frames[-1].y) == saved_position
    assert window.windowTitle() == "edited — TBO 2"


def test_frame_clone_resize_and_nudge_are_undoable(qtbot) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    page = window.canvas.current_page
    assert page is not None
    source = page.frames[0]
    assert window.canvas.select_frame(source)

    clone = window.canvas.clone_selected_frame()
    assert clone is not None
    assert clone is not source
    assert clone.objects is not source.objects
    assert (clone.x, clone.y) == (source.x + 10, source.y + 10)

    original_size = (clone.width, clone.height)
    assert window.canvas.resize_frame(clone, (clone.width + 50, clone.height + 25))
    assert (clone.width, clone.height) == (original_size[0] + 50, original_size[1] + 25)

    assert window.canvas.select_frame(clone)
    old_position = (clone.x, clone.y)
    assert window.canvas.nudge_selected_frame(5, -5)
    assert (clone.x, clone.y) == (old_position[0] + 5, old_position[1] - 5)

    window.canvas.undo_stack.undo()
    assert (clone.x, clone.y) == old_position
    window.canvas.undo_stack.undo()
    assert (clone.width, clone.height) == original_size
    window.canvas.undo_stack.undo()
    assert all(frame is not clone for frame in page.frames)


def test_zoom_controls_change_and_reset_view(qtbot) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    window.canvas.reset_zoom()

    window.canvas.zoom_in()
    assert window.canvas.transform().m11() == 1.2
    window.canvas.zoom_out()
    assert round(window.canvas.transform().m11(), 7) == 1.0

    window.canvas.zoom_in()
    window.canvas.reset_zoom()
    assert window.canvas.transform().m11() == 1.0


def test_page_management_is_undoable_and_updates_navigation(qtbot, tmp_path: Path) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    comic = window.canvas.comic
    assert comic is not None
    original_pages = list(comic.pages)

    added = window.canvas.add_page()
    assert added is not None
    assert len(comic.pages) == 12
    assert window.canvas.page_index == 1
    assert window.statusBar().currentMessage() == "Página 2 de 12"

    assert window.canvas.move_current_page(1)
    assert comic.pages[2] is added
    assert window.canvas.page_index == 2
    window.canvas.undo_stack.undo()
    assert comic.pages[1] is added

    assert window.canvas.delete_current_page()
    assert all(page is not added for page in comic.pages)
    window.canvas.undo_stack.undo()
    assert comic.pages[1] is added

    window.canvas.undo_stack.undo()
    assert all(current is original for current, original in zip(comic.pages, original_pages))
    assert window.canvas.page_index == 0
    assert window.statusBar().currentMessage() == "Página 1 de 11"

    window.canvas.undo_stack.redo()
    target = tmp_path / "pages.tbo"
    assert window._save_to(target)
    assert len(load(target).pages) == 12


def test_new_document_starts_clean_with_one_page(qtbot) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)

    window.new_document("Mi cómic", 1024, 768)

    comic = window.canvas.comic
    assert comic is not None
    assert comic.title == "Mi cómic"
    assert (comic.width, comic.height) == (1024, 768)
    assert len(comic.pages) == 1
    assert window.canvas.undo_stack.isClean()
    assert window.windowTitle() == "Mi cómic — TBO 2"
    assert window.statusBar().currentMessage() == "Página 1 de 1"


def test_cancel_keeps_modified_document_and_rejects_close(qtbot, monkeypatch) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    window.new_document("Importante", 800, 450)
    original = window.canvas.comic
    window.canvas.add_frame()
    assert not window.canvas.undo_stack.isClean()
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )

    assert not window._confirm_replacing_modified_document()
    assert window.canvas.comic is original
    assert not window.canvas.undo_stack.isClean()

    event = QCloseEvent()
    window.closeEvent(event)
    assert not event.isAccepted()


def test_discard_allows_replacing_modified_document(qtbot, monkeypatch) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    window.new_document("Anterior", 800, 450)
    window.canvas.add_frame()
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard,
    )

    assert window._confirm_replacing_modified_document()
    window.new_document("Nuevo", 640, 480)
    assert window.canvas.comic is not None
    assert window.canvas.comic.title == "Nuevo"
    assert window.canvas.undo_stack.isClean()


def test_save_choice_must_succeed_before_replacing(qtbot, monkeypatch) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    window.new_document("Sin guardar", 800, 450)
    window.canvas.add_frame()
    monkeypatch.setattr(
        QMessageBox,
        "warning",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(window, "save_document", lambda: False)

    assert not window._confirm_replacing_modified_document()


def test_object_edit_mode_mutates_model_and_is_undoable(qtbot, tmp_path: Path) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    assert window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    page = window.canvas.current_page
    assert page is not None
    frame = page.frames[0]
    original_count = len(frame.objects)
    graphic_object = frame.objects[0]

    assert window.canvas.enter_frame(frame)
    assert window.canvas.editing_frame is frame
    assert "Editando viñeta" in window.statusBar().currentMessage()
    assert window.canvas.select_object(graphic_object)

    clone = window.canvas.clone_selected_object()
    assert clone is not None
    assert clone is not graphic_object
    assert len(frame.objects) == original_count + 1
    original_position = (clone.x, clone.y)
    assert window.canvas.move_object(clone, (clone.x + 20, clone.y - 10))
    moved_position = (clone.x, clone.y)
    assert moved_position == (original_position[0] + 20, original_position[1] - 10)

    window.canvas.undo_stack.undo()
    assert (clone.x, clone.y) == original_position
    window.canvas.undo_stack.redo()
    assert (clone.x, clone.y) == moved_position
    assert window.canvas.select_object(clone)
    assert window.canvas.delete_selected_object()
    assert len(frame.objects) == original_count
    window.canvas.undo_stack.undo()
    assert len(frame.objects) == original_count + 1

    target = tmp_path / "objects.tbo"
    assert window._save_to(target)
    restored = load(target)
    restored_clone = restored.pages[0].frames[0].objects[1]
    assert (restored_clone.x, restored_clone.y) == moved_position

    assert window.canvas.leave_frame()
    assert window.canvas.editing_frame is None
    assert window.statusBar().currentMessage() == "Página 1 de 11"
