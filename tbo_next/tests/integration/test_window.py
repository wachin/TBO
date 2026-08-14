from pathlib import Path

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
