from tbo.document.model import Color, DocumentValidationError, ShapeObject
from tbo.formats.tbo_v1 import dumps, loads

import pytest


def test_shape_round_trip_preserves_geometry_and_style() -> None:
    shape = ShapeObject(
        x=5,
        y=10,
        width=100,
        height=60,
        kind="rect",
        fill=Color(1.0, 0.5, 0.0),
        stroke=Color(0.0, 0.0, 0.0),
        stroke_width=3,
    )
    from tbo.document.model import Comic, Frame, Page

    comic = Comic("Shapes", 800, 600, [Page(frames=[Frame(x=0, y=0, width=400, height=300)])])
    comic.pages[0].frames[0].objects.append(shape)

    restored = loads(dumps(comic), title="Shapes").pages[0].frames[0].objects[0]
    assert isinstance(restored, ShapeObject)
    assert restored.kind == "rect"
    assert (restored.x, restored.y, restored.width, restored.height) == (5, 10, 100, 60)
    assert restored.stroke_width == 3
    assert (restored.fill.red, restored.fill.green, restored.fill.blue) == (1.0, 0.5, 0.0)
    assert restored.fill is not None


def test_freehand_shape_round_trip_preserves_points() -> None:
    freehand = ShapeObject(
        x=0,
        y=0,
        width=50,
        height=50,
        kind="freehand",
        fill=None,
        stroke=Color(0.2, 0.2, 0.2),
        stroke_width=5,
        points=[(0.0, 0.0), (0.5, 1.0), (1.0, 0.25)],
    )
    from tbo.document.model import Comic, Frame, Page

    comic = Comic("Free", 800, 600, [Page(frames=[Frame(x=0, y=0, width=400, height=300)])])
    comic.pages[0].frames[0].objects.append(freehand)

    data = dumps(comic)
    assert b'fill="none"' in data
    restored = loads(data, title="Free").pages[0].frames[0].objects[0]
    assert isinstance(restored, ShapeObject)
    assert restored.kind == "freehand"
    assert restored.fill is None
    assert restored.stroke_width == 5
    assert len(restored.points) == 3
    assert restored.points[0] == (0.0, 0.0)
    assert restored.points[1][0] == 0.5


def test_invalid_shape_kind_is_rejected() -> None:
    with pytest.raises(DocumentValidationError):
        ShapeObject(x=0, y=0, width=10, height=10, kind="triangle")


def test_line_shape_requires_two_points() -> None:
    with pytest.raises(DocumentValidationError):
        ShapeObject(x=0, y=0, width=10, height=10, kind="line", points=[(0.0, 0.0)])


def test_shape_points_must_be_normalized() -> None:
    with pytest.raises(DocumentValidationError):
        ShapeObject(
            x=0,
            y=0,
            width=10,
            height=10,
            kind="freehand",
            points=[(0.0, 0.0), (1.5, 0.5)],
        )
