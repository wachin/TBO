from pathlib import Path

from tbo.document.model import SvgObject
from tbo.ui.main_window import MainWindow

REPOSITORY_ROOT = Path(__file__).parents[2]
DOODLE_ROOT = REPOSITORY_ROOT / "data" / "doodle"


def test_assets_dock_inserts_svg_into_editing_frame(qtbot) -> None:
    window = MainWindow(asset_root=DOODLE_ROOT)
    qtbot.addWidget(window)
    assert window.assets_dock is not None
    assert window.assets_dock.windowTitle() == "Asset Library"

    window.new_document("Library", 800, 450)
    frame = window.canvas.add_frame()
    assert frame is not None
    assert not window.assets_dock.isEnabled()
    assert window.canvas.enter_frame(frame)
    assert window.assets_dock.isEnabled()

    target = DOODLE_ROOT / "bubble" / "ellipse" / "horizontal.svg"
    window.assets_dock.assetActivated.emit(target)

    assert len(frame.objects) == 1
    inserted = frame.objects[0]
    assert isinstance(inserted, SvgObject)
    assert inserted.path == target.resolve()
    assert inserted.width > 0 and inserted.height > 0

    window.canvas.undo_stack.undo()
    assert not frame.objects
    window.canvas.undo_stack.redo()
    assert len(frame.objects) == 1


def test_assets_dock_search_filters_library_items(qtbot) -> None:
    window = MainWindow(asset_root=DOODLE_ROOT)
    qtbot.addWidget(window)
    assert window.assets_dock is not None
    tab = window.assets_dock.tabs.widget(0)
    total = sum(page.count() for page in tab._pages)
    assert total > 0
    tab.search_input.setText("nonexistent-asset")
    filtered = sum(page.count() for page in tab._pages)
    assert filtered == 0
    tab.search_input.setText("")
    assert sum(page.count() for page in tab._pages) == total
