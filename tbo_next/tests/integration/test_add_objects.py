from pathlib import Path

from PyQt6.QtGui import QColor, QImage

from tbo.document.model import ImageObject, SvgObject, TextObject
from tbo.formats.tbo_v1 import load
from tbo.ui.main_window import MainWindow


def _window_in_panel_mode(qtbot) -> tuple[MainWindow, object]:
    window = MainWindow()
    qtbot.addWidget(window)
    window.new_document("Objects", 800, 450)
    frame = window.canvas.add_frame()
    assert frame is not None
    assert not window.add_text_action.isEnabled()
    assert window.canvas.enter_frame(frame)
    assert window.add_text_action.isEnabled()
    assert window.add_image_action.isEnabled()
    assert window.add_svg_action.isEnabled()
    return window, frame


def test_add_text_object_is_undoable_and_persistent(qtbot, tmp_path: Path) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    text = TextObject(x=10, y=20, width=200, height=80, text="Hello", font="Sans 14")

    assert window.canvas.add_graphic_object(text)
    assert frame.objects[0] is text
    assert window.canvas.selected_object() is text
    window.canvas.undo_stack.undo()
    assert not frame.objects
    window.canvas.undo_stack.redo()
    assert frame.objects[0] is text

    target = tmp_path / "text.tbo"
    assert window._save_to(target)
    restored = load(target).pages[0].frames[0].objects[0]
    assert isinstance(restored, TextObject)
    assert restored.text == "Hello"
    assert restored.font == "Sans 14"


def test_import_image_and_svg_uses_natural_aspect_ratio(qtbot, tmp_path: Path) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    image_path = tmp_path / "image.png"
    image = QImage(80, 40, QImage.Format.Format_ARGB32)
    image.fill(QColor("red"))
    assert image.save(str(image_path))
    svg_path = tmp_path / "shape.svg"
    svg_path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="60">'
        '<rect width="120" height="60" fill="blue"/></svg>',
        encoding="utf-8",
    )

    assert window.add_image_from_path(image_path)
    assert window.add_svg_from_path(svg_path)

    raster, vector = frame.objects
    assert isinstance(raster, ImageObject)
    assert isinstance(vector, SvgObject)
    assert (raster.width, raster.height) == (80, 40)
    assert (vector.width, vector.height) == (120, 60)
    assert raster.path == image_path.resolve()
    assert vector.path == svg_path.resolve()
    window.canvas.undo_stack.setClean()


def test_rejects_invalid_graphic_files(qtbot, tmp_path: Path) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    invalid = tmp_path / "invalid.dat"
    invalid.write_text("not an image", encoding="utf-8")

    assert not window.add_image_from_path(invalid)
    assert not window.add_svg_from_path(invalid)
    assert not frame.objects
    window.canvas.undo_stack.setClean()
