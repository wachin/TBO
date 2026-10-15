"""Shared painting for :class:`~tbo.document.model.ShapeObject`.

Both the interactive canvas and the exporters use this module so a
shape looks identical on screen and in exported PNG/PDF/SVG files.
"""

from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF

from tbo.document.model import Color, ShapeObject


def qcolor(color: Color) -> QColor:
    return QColor.fromRgbF(color.red, color.green, color.blue)


def paint_shape_object(painter: QPainter, shape: ShapeObject, rect: QRectF) -> None:
    """Paint ``shape`` inside ``rect`` (the object's bounding box)."""
    stroke = qcolor(shape.stroke)
    pen = QPen(stroke, max(1, shape.stroke_width))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    fill = qcolor(shape.fill) if shape.fill is not None else None

    painter.save()
    painter.setPen(pen)
    if fill is None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
    else:
        painter.setBrush(fill)

    if shape.kind == "rect":
        painter.drawRect(rect)
    elif shape.kind == "ellipse":
        painter.drawEllipse(rect)
    elif shape.kind in {"line", "freehand"}:
        painter.drawPolyline(_polygon_for_points(shape, rect))
    painter.restore()


def _polygon_for_points(shape: ShapeObject, rect: QRectF) -> QPolygonF:
    polygon = QPolygonF()
    for x, y in shape.points:
        polygon.append(QPointF(rect.left() + x * rect.width(), rect.top() + y * rect.height()))
    return polygon


def shape_preview_path(points: list[QPointF]) -> QPainterPath:
    path = QPainterPath()
    if not points:
        return path
    path.moveTo(points[0])
    for point in points[1:]:
        path.lineTo(point)
    return path
