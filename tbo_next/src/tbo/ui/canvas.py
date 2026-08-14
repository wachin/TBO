from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QPixmap, QTransform
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
)

from tbo.document.model import Comic, GraphicObject, ImageObject, SvgObject, TextObject


class ComicCanvas(QGraphicsView):
    def __init__(self, asset_root: Path | None = None) -> None:
        self.scene = QGraphicsScene()
        super().__init__(self.scene)
        self._asset_root = asset_root
        self._comic: Comic | None = None
        self._page_index = 0
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setBackgroundBrush(QColor("#707070"))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    @property
    def comic(self) -> Comic | None:
        return self._comic

    def set_comic(self, comic: Comic) -> None:
        self._comic = comic
        self._page_index = 0
        self.show_page(0)

    def show_page(self, index: int) -> None:
        if self._comic is None:
            return
        if not 0 <= index < len(self._comic.pages):
            raise IndexError("page index out of range")

        self._page_index = index
        self.scene.clear()
        page_rect = QRectF(0, 0, self._comic.width, self._comic.height)
        self.scene.setSceneRect(page_rect)
        self.scene.addRect(page_rect, QPen(Qt.PenStyle.NoPen), QBrush(QColor("white")))

        for frame in self._comic.pages[index].frames:
            pen = QPen(QColor("black"), 2) if frame.border else QPen(Qt.PenStyle.NoPen)
            color = QColor.fromRgbF(frame.color.red, frame.color.green, frame.color.blue)
            frame_item = QGraphicsRectItem(0, 0, frame.width, frame.height)
            frame_item.setPos(frame.x, frame.y)
            frame_item.setPen(pen)
            frame_item.setBrush(color)
            frame_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape)
            self.scene.addItem(frame_item)
            for graphic_object in frame.objects:
                self._add_object(graphic_object, frame_item)

    def fit_page(self) -> None:
        if self._comic is not None:
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _add_object(self, obj: GraphicObject, parent: QGraphicsRectItem) -> None:
        item: QGraphicsItem
        if isinstance(obj, TextObject):
            text_item = QGraphicsTextItem(obj.text, parent)
            text_item.setDefaultTextColor(
                QColor.fromRgbF(obj.color.red, obj.color.green, obj.color.blue)
            )
            text_item.setFont(_font_from_legacy_string(obj.font))
            text_item.setTextWidth(obj.width)
            item = text_item
        elif isinstance(obj, SvgObject):
            resolved = self._resolve_asset(obj.path)
            if resolved is not None:
                svg_item = QGraphicsSvgItem(str(resolved), parent)
                bounds = svg_item.boundingRect()
                if bounds.width() and bounds.height():
                    svg_item.setTransform(
                        QTransform.fromScale(obj.width / bounds.width(), obj.height / bounds.height())
                    )
                item = svg_item
            else:
                item = _missing_asset_item(obj, parent)
        elif isinstance(obj, ImageObject):
            resolved = self._resolve_asset(obj.path)
            pixmap = QPixmap(str(resolved)) if resolved is not None else QPixmap()
            if pixmap.isNull():
                item = _missing_asset_item(obj, parent)
            else:
                item = QGraphicsPixmapItem(
                    pixmap.scaled(
                        obj.width,
                        obj.height,
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    ),
                    parent,
                )
        else:
            return

        item.setPos(obj.x, obj.y)
        item.setTransformOriginPoint(obj.width / 2, obj.height / 2)
        item.setRotation(obj.angle * 180.0 / 3.141592653589793)
        transform = item.transform()
        transform.scale(-1.0 if obj.flip_horizontal else 1.0, -1.0 if obj.flip_vertical else 1.0)
        item.setTransform(transform)

    def _resolve_asset(self, asset_path: Path) -> Path | None:
        if asset_path.is_absolute() and asset_path.is_file():
            return asset_path
        if self._asset_root is not None:
            candidate = self._asset_root / asset_path
            if candidate.is_file():
                return candidate
        return None


def _font_from_legacy_string(description: str) -> QFont:
    parts = description.rsplit(maxsplit=1)
    if len(parts) == 2 and parts[1].isdigit():
        return QFont(parts[0], int(parts[1]))
    return QFont(description)


def _missing_asset_item(obj: GraphicObject, parent: QGraphicsRectItem) -> QGraphicsRectItem:
    item = QGraphicsRectItem(0, 0, obj.width, obj.height, parent)
    item.setPen(QPen(QColor("#b00020"), 2, Qt.PenStyle.DashLine))
    item.setBrush(QColor(255, 220, 220, 100))
    return item

