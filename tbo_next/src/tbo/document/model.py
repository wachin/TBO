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

