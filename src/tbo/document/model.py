from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from pathlib import Path


class DocumentValidationError(ValueError):
    """Raised when a document violates a model invariant."""


def _positive_dimension(name: str, value: int) -> None:
    if value <= 0:
        raise DocumentValidationError(f"{name} must be greater than zero")


@dataclass(slots=True)
class Color:
    red: float = 1.0
    green: float = 1.0
    blue: float = 1.0

    def __post_init__(self) -> None:
        for name, value in (
            ("red", self.red),
            ("green", self.green),
            ("blue", self.blue),
        ):
            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise DocumentValidationError(f"{name} must be between 0 and 1")


@dataclass(slots=True, kw_only=True)
class GraphicObject:
    x: int
    y: int
    width: int
    height: int
    angle: float = 0.0
    flip_vertical: bool = False
    flip_horizontal: bool = False

    def __post_init__(self) -> None:
        _positive_dimension("object width", self.width)
        _positive_dimension("object height", self.height)
        if not isfinite(self.angle):
            raise DocumentValidationError("object angle must be finite")


@dataclass(slots=True, kw_only=True)
class SvgObject(GraphicObject):
    path: Path


@dataclass(slots=True, kw_only=True)
class ImageObject(GraphicObject):
    path: Path


@dataclass(slots=True, kw_only=True)
class TextObject(GraphicObject):
    text: str
    font: str = "Sans 12"
    color: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))
    bold: bool = False
    italic: bool = False
    underline: bool = False


SHAPE_KINDS = ("rect", "ellipse", "line", "freehand")
MAX_SHAPE_POINTS = 5_000


@dataclass(slots=True, kw_only=True)
class ShapeObject(GraphicObject):
    """A simple vector drawing: rectangle, ellipse, line or freehand stroke.

    ``points`` stores normalized (0..1) coordinates relative to the
    object's bounding box and is used by the ``line`` (two points) and
    ``freehand`` (polyline) kinds.  ``fill`` of ``None`` means no fill.
    """

    kind: str = "rect"
    fill: Color | None = None
    stroke: Color = field(default_factory=lambda: Color(0.0, 0.0, 0.0))
    stroke_width: int = 2
    points: list[tuple[float, float]] = field(default_factory=list)

    def __post_init__(self) -> None:
        # ``@dataclass(slots=True)`` rebuilds the class, which breaks the
        # zero-argument ``super()``; call the base hook explicitly.
        GraphicObject.__post_init__(self)
        if self.kind not in SHAPE_KINDS:
            raise DocumentValidationError(f"shape kind must be one of {SHAPE_KINDS}")
        if not isinstance(self.stroke_width, int) or not 0 <= self.stroke_width <= 1_000:
            raise DocumentValidationError("stroke width must be an integer between 0 and 1000")
        if len(self.points) > MAX_SHAPE_POINTS:
            raise DocumentValidationError(f"shape has more than {MAX_SHAPE_POINTS} points")
        for point in self.points:
            if len(point) != 2:
                raise DocumentValidationError("shape points must be pairs")
            px, py = point
            for value in (px, py):
                if not isfinite(value) or not 0.0 <= value <= 1.0:
                    raise DocumentValidationError(
                        "shape point components must be between 0 and 1"
                    )
        if self.kind == "line" and len(self.points) != 2:
            raise DocumentValidationError("line shapes need exactly two points")
        if self.kind == "freehand" and len(self.points) < 2:
            raise DocumentValidationError("freehand shapes need at least two points")


@dataclass(slots=True)
class Frame:
    x: int
    y: int
    width: int
    height: int
    border: bool = True
    color: Color = field(default_factory=Color)
    objects: list[GraphicObject] = field(default_factory=list)

    def __post_init__(self) -> None:
        _positive_dimension("frame width", self.width)
        _positive_dimension("frame height", self.height)


@dataclass(slots=True)
class Page:
    frames: list[Frame] = field(default_factory=list)


@dataclass(slots=True)
class Comic:
    title: str
    width: int
    height: int
    pages: list[Page] = field(default_factory=list)

    def __post_init__(self) -> None:
        _positive_dimension("comic width", self.width)
        _positive_dimension("comic height", self.height)
        if not self.title:
            raise DocumentValidationError("comic title must not be empty")


