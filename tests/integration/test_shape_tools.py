from pathlib import Path

from PyQt6.QtCore import QPointF

from tbo.document.model import Color, ShapeObject
from tbo.formats.tbo_v1 import load
from tbo.ui.main_window import MainWindow


def _window_in_panel_mode(qtbot) -> tuple[MainWindow, object]:
    window = MainWindow()
    qtbot.addWidget(window)
    window.new_document("Shapes", 800, 450)
    frame = window.canvas.add_frame()
    assert frame is not None
    assert window.canvas.enter_frame(frame)
    return window, frame


def test_rectangle_tool_creates_shape_and_is_undoable(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    canvas.set_tool("rect")
    assert canvas.tool == "rect"
    frame_item = canvas._frame_items[id(frame)]

    canvas.begin_creation(frame_item, QPointF(10, 20))
    canvas.update_creation(QPointF(110, 120))
    canvas.finish_creation()

    assert len(frame.objects) == 1
    shape = frame.objects[0]
    assert isinstance(shape, ShapeObject)
    assert shape.kind == "rect"
    assert (shape.x, shape.y) == (10, 20)
    assert (shape.width, shape.height) == (100, 100)
    assert canvas.selected_object() is shape

    canvas.undo_stack.undo()
    assert not frame.objects
    canvas.undo_stack.redo()
    assert len(frame.objects) == 1


def test_line_and_freehand_tools_create_strokes(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas

    canvas.set_tool("line")
    frame_item = canvas._frame_items[id(frame)]
    canvas.begin_creation(frame_item, QPointF(0, 0))
    canvas.update_creation(QPointF(40, 20))
    canvas.finish_creation()

    canvas.set_tool("freehand")
    # Creating an object refreshes the scene; grab the fresh item.
    frame_item = canvas._frame_items[id(frame)]
    canvas.begin_creation(frame_item, QPointF(0, 50))
    canvas.update_creation(QPointF(10, 60))
    canvas.update_creation(QPointF(25, 75))
    canvas.finish_creation()

    line, freehand = frame.objects
    assert line.kind == "line"
    assert line.fill is None
    assert len(line.points) == 2
    assert freehand.kind == "freehand"
    assert len(freehand.points) == 3
    assert all(0.0 <= value <= 1.0 for point in freehand.points for value in point)


def test_creation_tiny_drag_is_ignored(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    canvas.set_tool("ellipse")
    frame_item = canvas._frame_items[id(frame)]
    canvas.begin_creation(frame_item, QPointF(5, 5))
    canvas.update_creation(QPointF(6, 6))
    canvas.finish_creation()
    assert not frame.objects


def test_cancel_active_tool_returns_to_select(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    canvas.set_tool("rect")
    frame_item = canvas._frame_items[id(frame)]
    canvas.begin_creation(frame_item, QPointF(0, 0))
    canvas.update_creation(QPointF(30, 30))

    assert canvas.cancel_active_tool()  # cancels the in-progress creation
    assert canvas._creation_preview is None
    assert canvas.tool == "rect"
    assert canvas.cancel_active_tool()  # back to select
    assert canvas.tool == "select"
    assert not canvas.cancel_active_tool()


def test_transform_object_updates_position_and_size_together(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    shape = ShapeObject(x=50, y=50, width=100, height=100, kind="rect")
    assert canvas.add_graphic_object(shape)

    # Anchored resize from the top-left: x, y and size all change.
    assert canvas.transform_object(shape, (20, 30, 130, 140))
    assert (shape.x, shape.y, shape.width, shape.height) == (20, 30, 130, 140)
    canvas.undo_stack.undo()
    assert (shape.x, shape.y, shape.width, shape.height) == (50, 50, 100, 100)


def test_reorder_object_changes_stacking_and_is_undoable(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    first = ShapeObject(x=0, y=0, width=10, height=10, kind="rect")
    second = ShapeObject(x=0, y=0, width=10, height=10, kind="ellipse")
    third = ShapeObject(x=0, y=0, width=10, height=10, kind="rect")
    for obj in (first, second, third):
        assert canvas.add_graphic_object(obj)

    assert canvas.select_object(second)
    assert canvas.reorder_selected_object("front")
    assert frame.objects == [first, third, second]
    assert canvas.reorder_selected_object("back")
    assert frame.objects == [second, first, third]
    canvas.undo_stack.undo()
    assert frame.objects == [first, third, second]


def test_shape_style_change_is_undoable(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    shape = ShapeObject(x=0, y=0, width=10, height=10, kind="rect", fill=Color(1.0, 1.0, 1.0))
    assert canvas.add_graphic_object(shape)

    assert canvas.set_shape_style(None, Color(1.0, 0.0, 0.0), 6)
    assert shape.fill is None
    assert shape.stroke_width == 6
    canvas.undo_stack.undo()
    assert shape.fill is not None
    assert shape.stroke_width == 2


def test_frame_style_change_is_undoable(qtbot) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    assert canvas.leave_frame()
    assert canvas.select_frame(frame)

    assert canvas.set_frame_style(Color(0.5, 0.5, 0.5), border=False)
    assert frame.border is False
    canvas.undo_stack.undo()
    assert frame.border is True


def test_shapes_are_saved_and_reloaded(qtbot, tmp_path: Path) -> None:
    window, frame = _window_in_panel_mode(qtbot)
    canvas = window.canvas
    frame_item = canvas._frame_items[id(frame)]
    canvas.set_tool("rect")
    canvas.begin_creation(frame_item, QPointF(10, 10))
    canvas.update_creation(QPointF(60, 60))
    canvas.finish_creation()
    canvas.undo_stack.setClean()

    target = tmp_path / "shapes.tbo"
    assert window._save_to(target)
    restored = load(target).pages[0].frames[0].objects[0]
    assert isinstance(restored, ShapeObject)
    assert restored.kind == "rect"
    assert (restored.width, restored.height) == (50, 50)
