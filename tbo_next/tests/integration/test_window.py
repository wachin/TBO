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
