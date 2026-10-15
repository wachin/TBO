"""Pure geometry helpers for interactive object transformation.

The canvas uses these functions to compute resize operations with
Inkscape-style behaviour: eight resize handles (four corners and four
edges), optional aspect-ratio locking and optional resize from the
centre.  Keeping the maths free of Qt makes it easy to unit test.
"""

from __future__ import annotations

from dataclasses import dataclass

# Handle names and their anchor/handle positions as fractions of the
# starting rectangle.  The anchor is the point that stays fixed while
# the handle is dragged.
HANDLES: dict[str, tuple[tuple[float, float], tuple[float, float]]] = {
    "nw": ((1.0, 1.0), (0.0, 0.0)),
    "n": ((0.5, 1.0), (0.5, 0.0)),
    "ne": ((0.0, 1.0), (1.0, 0.0)),
    "e": ((0.0, 0.5), (1.0, 0.5)),
    "se": ((0.0, 0.0), (1.0, 1.0)),
    "s": ((0.5, 0.0), (0.5, 1.0)),
    "sw": ((1.0, 0.0), (0.0, 1.0)),
    "w": ((1.0, 0.5), (0.0, 0.5)),
}


@dataclass(frozen=True, slots=True)
class Rect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float


def handle_positions(rect: Rect) -> dict[str, Point]:
    """Scene-free positions of every resize handle for a rectangle."""
    return {
        name: Point(rect.x + handle[0] * rect.width, rect.y + handle[1] * rect.height)
        for name, (_anchor, handle) in HANDLES.items()
    }


def handle_at(rect: Rect, position: Point, tolerance: float) -> str | None:
    """Return the handle under ``position`` within ``tolerance``, if any."""
    for name, point in handle_positions(rect).items():
        if abs(point.x - position.x) <= tolerance and abs(point.y - position.y) <= tolerance:
            return name
    return None


def resize_rect(
    start: Rect,
    handle: str,
    delta: Point,
    *,
    keep_aspect: bool = False,
    from_center: bool = False,
    min_size: float = 1.0,
) -> Rect:
    """Compute the new rectangle for a resize drag.

    ``start`` is the rectangle at drag start expressed in the item's
    local (unrotated) coordinate system with its origin at the rect's
    top-left, i.e. ``Rect(0, 0, w, h)``.  ``delta`` must already be
    expressed in that same local system so the result is correct even
    when the item is rotated or flipped.

    The returned rectangle is expressed in the starting rectangle's
    local frame: its ``(x, y)`` is the offset of the new top-left
    corner relative to the old one.
    """
    try:
        anchor_fraction, handle_fraction = HANDLES[handle]
    except KeyError as error:
        raise ValueError(f"unknown handle {handle!r}") from error

    width = start.width
    height = start.height
    if from_center:
        anchor = Point(width / 2, height / 2)
    else:
        anchor = Point(anchor_fraction[0] * width, anchor_fraction[1] * height)
    moving = Point(
        handle_fraction[0] * width + delta.x,
        handle_fraction[1] * height + delta.y,
    )

    horizontal_active = handle_fraction[0] != 0.5
    vertical_active = handle_fraction[1] != 0.5

    if horizontal_active:
        extent_x = _axis_extent(anchor.x, moving.x, handle_fraction[0], from_center)
    else:
        extent_x = width
    if vertical_active:
        extent_y = _axis_extent(anchor.y, moving.y, handle_fraction[1], from_center)
    else:
        extent_y = height

    if keep_aspect and width > 0 and height > 0:
        if horizontal_active and vertical_active:
            ratio_x = extent_x / width
            ratio_y = extent_y / height
            if ratio_x >= ratio_y:
                extent_y = extent_x * height / width
            else:
                extent_x = extent_y * width / height
        elif horizontal_active:
            extent_y = extent_x * height / width
        elif vertical_active:
            extent_x = extent_y * width / height

    extent_x = max(min_size, extent_x)
    extent_y = max(min_size, extent_y)

    if from_center:
        origin_x = width / 2 - extent_x / 2
        origin_y = height / 2 - extent_y / 2
    else:
        origin_x = _axis_origin(anchor.x, extent_x, handle_fraction[0], horizontal_active)
        origin_y = _axis_origin(anchor.y, extent_y, handle_fraction[1], vertical_active)

    return Rect(origin_x, origin_y, extent_x, extent_y)


def _axis_extent(anchor: float, moving: float, handle_fraction: float, from_center: bool) -> float:
    if from_center:
        return 2.0 * abs(moving - anchor)
    if handle_fraction >= 0.5:
        return moving - anchor
    return anchor - moving


def _axis_origin(anchor: float, extent: float, handle_fraction: float, active: bool) -> float:
    if not active:
        # Inactive axis: the anchor is the midpoint of the starting
        # extent, so keeping it centred preserves the original origin.
        return anchor - extent / 2
    if handle_fraction >= 0.5:
        return anchor
    return anchor - extent


def normalized_points(points: list[tuple[float, float]], bounds: Rect) -> list[tuple[float, float]]:
    """Express absolute points inside ``bounds`` as 0..1 fractions."""
    if bounds.width <= 0 or bounds.height <= 0:
        raise ValueError("bounds must have positive size")
    return [
        ((x - bounds.x) / bounds.width, (y - bounds.y) / bounds.height)
        for x, y in points
    ]
