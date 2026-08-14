from pathlib import Path

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
