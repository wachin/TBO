from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtSvg import QSvgRenderer

from tbo.document.model import Comic, Frame, GraphicObject, ImageObject, Page, SvgObject, TextObject


def _font_from_legacy_string(description: str) -> QFont:
    parts = description.rsplit(maxsplit=1)
    if len(parts) == 2 and parts[1].isdigit():
        return QFont(parts[0], int(parts[1]))
    return QFont(description)


class ComicRenderer:
    """Paint a :class:`Comic` onto any ``QPainter`` target.

    The renderer is the single source of truth for how a document is drawn.
    The interactive canvas and the file exporters both rely on it so that the
    on-screen representation and the exported file never diverge.
    """

    def __init__(self, asset_root: Path | None = None) -> None:
        self._asset_root = asset_root

    def resolve_asset(self, asset_path: Path) -> Path | None:
        if asset_path.is_absolute() and asset_path.is_file():
            return asset_path
        if self._asset_root is not None:
            candidate = self._asset_root / asset_path
            if candidate.is_file():
                return candidate
        return None

    def paint_page(self, painter: QPainter, page: Page, comic: Comic) -> None:
        page_rect = QRectF(0, 0, comic.width, comic.height)
        painter.fillRect(page_rect, QColor("white"))
        for frame in page.frames:
            self._paint_frame(painter, frame)

    def _paint_frame(self, painter: QPainter, frame: Frame) -> None:
        frame_rect = QRectF(frame.x, frame.y, frame.width, frame.height)
        color = QColor.fromRgbF(frame.color.red, frame.color.green, frame.color.blue)
        painter.fillRect(frame_rect, color)
        pen = QPen(QColor("black"), 2) if frame.border else QPen(Qt.PenStyle.NoPen)
        painter.setPen(pen)
        painter.drawRect(frame_rect)
        for graphic_object in frame.objects:
            self._paint_object(painter, graphic_object)

    def _paint_object(self, painter: QPainter, obj: GraphicObject) -> None:
        painter.save()
        origin = QPointF(obj.x + obj.width / 2, obj.y + obj.height / 2)
        painter.translate(origin)
        painter.rotate(obj.angle * 180.0 / 3.141592653589793)
        painter.scale(-1.0 if obj.flip_horizontal else 1.0, -1.0 if obj.flip_vertical else 1.0)
        painter.translate(-obj.width / 2, -obj.height / 2)

        if isinstance(obj, TextObject):
            self._paint_text(painter, obj)
        elif isinstance(obj, SvgObject):
            self._paint_svg(painter, obj)
        elif isinstance(obj, ImageObject):
            self._paint_image(painter, obj)

        painter.restore()

    def _paint_text(self, painter: QPainter, obj: TextObject) -> None:
        painter.setPen(QColor.fromRgbF(obj.color.red, obj.color.green, obj.color.blue))
        painter.setFont(_font_from_legacy_string(obj.font))
        painter.drawText(QRectF(0, 0, obj.width, obj.height), Qt.TextFlag.TextWordWrap, obj.text)

    def _paint_svg(self, painter: QPainter, obj: SvgObject) -> None:
        resolved = self.resolve_asset(obj.path)
        if resolved is None:
            self._paint_missing(painter, obj)
            return
        renderer = QSvgRenderer(str(resolved))
        if not renderer.isValid():
            self._paint_missing(painter, obj)
            return
        renderer.render(painter, QRectF(0, 0, obj.width, obj.height))

    def _paint_image(self, painter: QPainter, obj: ImageObject) -> None:
        resolved = self.resolve_asset(obj.path)
        pixmap = QPixmap(str(resolved)) if resolved is not None else QPixmap()
        if pixmap.isNull():
            self._paint_missing(painter, obj)
            return
        painter.drawPixmap(
            QRectF(0, 0, obj.width, obj.height).toRect(),
            pixmap,
            QRectF(0, 0, pixmap.width(), pixmap.height()).toRect(),
        )

    def _paint_missing(self, painter: QPainter, obj: GraphicObject) -> None:
        rect = QRectF(0, 0, obj.width, obj.height)
        painter.setPen(QPen(QColor("#b00020"), 2, Qt.PenStyle.DashLine))
        painter.setBrush(QColor(255, 220, 220, 100))
        painter.drawRect(rect)
