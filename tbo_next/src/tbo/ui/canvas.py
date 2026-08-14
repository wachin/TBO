from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
    QPixmap,
    QTransform,
    QUndoStack,
)
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
    QGraphicsView,
)

from tbo.document.model import Comic, Frame, GraphicObject, ImageObject, Page, SvgObject, TextObject
from tbo.ui.commands import (
    AddFrameCommand,
    AddObjectCommand,
    AddPageCommand,
    DeleteFrameCommand,
    DeleteObjectCommand,
    DeletePageCommand,
    MoveFrameCommand,
    MoveObjectCommand,
    MovePageCommand,
    ResizeFrameCommand,
)

RESIZE_HANDLE_SIZE = 12.0
MIN_FRAME_SIZE = 20


class FrameGraphicsItem(QGraphicsRectItem):
    def __init__(self, frame: Frame, canvas: ComicCanvas) -> None:
        super().__init__(0, 0, frame.width, frame.height)
        self.frame = frame
        self._canvas = canvas
        self._drag_start = (frame.x, frame.y)
        self._resizing = False
        self._resize_start = (frame.width, frame.height)
        self._resize_scene_start = QPointF()
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape
        )
        self.setAcceptHoverEvents(True)

    def _resize_handle(self) -> QRectF:
        rectangle = self.rect()
        return QRectF(
            rectangle.right() - RESIZE_HANDLE_SIZE,
            rectangle.bottom() - RESIZE_HANDLE_SIZE,
            RESIZE_HANDLE_SIZE,
            RESIZE_HANDLE_SIZE,
        )

    def paint(self, painter, option, widget=None) -> None:
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.fillRect(self._resize_handle(), QColor("#f4c430"))
            painter.setPen(QPen(QColor("#6b5600"), 1))
            painter.drawRect(self._resize_handle())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if (
            self._canvas.editing_frame is None
            and event.button() == Qt.MouseButton.LeftButton
            and self._resize_handle().contains(event.pos())
        ):
            self.setSelected(True)
            self._resizing = True
            self._resize_start = (self.frame.width, self.frame.height)
            self._resize_scene_start = event.scenePos()
            event.accept()
            return
        self._drag_start = (self.frame.x, self.frame.y)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._canvas.editing_frame is None:
            self._canvas.enter_frame(self.frame)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._resizing:
            delta = event.scenePos() - self._resize_scene_start
            width = max(MIN_FRAME_SIZE, round(self._resize_start[0] + delta.x()))
            height = max(MIN_FRAME_SIZE, round(self._resize_start[1] + delta.y()))
            self.setRect(0, 0, width, height)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._resizing:
            self._resizing = False
            destination = (round(self.rect().width()), round(self.rect().height()))
            self._canvas.resize_frame(self.frame, destination, old_size=self._resize_start)
            event.accept()
            return
        super().mouseReleaseEvent(event)
        destination = (round(self.pos().x()), round(self.pos().y()))
        if destination == self._drag_start:
            self.setPos(*self._drag_start)
            return
        self._canvas.move_frame(self.frame, destination, old_position=self._drag_start)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        cursor = (
            Qt.CursorShape.SizeFDiagCursor
            if self._resize_handle().contains(event.pos())
            else Qt.CursorShape.ArrowCursor
        )
        self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.unsetCursor()
        super().hoverLeaveEvent(event)


class ObjectGraphicsItem(QGraphicsRectItem):
    def __init__(
        self,
        graphic_object: GraphicObject,
        canvas: ComicCanvas,
        parent: FrameGraphicsItem,
        *,
        editable: bool,
    ) -> None:
        super().__init__(0, 0, graphic_object.width, graphic_object.height, parent)
        self.graphic_object = graphic_object
        self._canvas = canvas
        self._drag_start = (graphic_object.x, graphic_object.y)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            if editable
            else QGraphicsItem.GraphicsItemFlag(0)
        )
        self.setAcceptedMouseButtons(
            Qt.MouseButton.LeftButton if editable else Qt.MouseButton.NoButton
        )

    def paint(self, painter, option, widget=None) -> None:
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(QPen(QColor("#1677ff"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.rect())

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._drag_start = (self.graphic_object.x, self.graphic_object.y)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseReleaseEvent(event)
        destination = (round(self.pos().x()), round(self.pos().y()))
        if destination == self._drag_start:
            self.setPos(*self._drag_start)
            return
        self._canvas.move_object(
            self.graphic_object,
            destination,
            old_position=self._drag_start,
        )


class ComicCanvas(QGraphicsView):
    pageChanged = pyqtSignal(int, int)
    modeChanged = pyqtSignal(bool)

    def __init__(self, asset_root: Path | None = None) -> None:
        self.scene = QGraphicsScene()
        super().__init__(self.scene)
        self._asset_root = asset_root
        self._comic: Comic | None = None
        self._page_index = 0
        self._frame_items: dict[int, FrameGraphicsItem] = {}
        self._object_items: dict[int, ObjectGraphicsItem] = {}
        self._editing_frame: Frame | None = None
        self.undo_stack = QUndoStack(self)
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

    @property
    def page_index(self) -> int:
        return self._page_index

    @property
    def page_count(self) -> int:
        return len(self._comic.pages) if self._comic is not None else 0

    @property
    def current_page(self) -> Page | None:
        if self._comic is None or not self._comic.pages:
            return None
        return self._comic.pages[self._page_index]

    @property
    def editing_frame(self) -> Frame | None:
        return self._editing_frame

    def set_comic(self, comic: Comic) -> None:
        self._comic = comic
        self._page_index = 0
        self._editing_frame = None
        self.undo_stack.clear()
        self._frame_items.clear()
        self._object_items.clear()
        self.scene.clear()
        if comic.pages:
            self.show_page(0)
        else:
            self.pageChanged.emit(0, 0)

    def show_page(self, index: int) -> None:
        if self._comic is None:
            return
        if not 0 <= index < len(self._comic.pages):
            raise IndexError("page index out of range")

        self._page_index = index
        page = self._comic.pages[index]
        if self._editing_frame is not None and not any(
            frame is self._editing_frame for frame in page.frames
        ):
            self._editing_frame = None
            self.modeChanged.emit(False)
        self._frame_items.clear()
        self._object_items.clear()
        self.scene.clear()
        page_rect = QRectF(0, 0, self._comic.width, self._comic.height)
        self.scene.setSceneRect(page_rect)
        self.scene.addRect(page_rect, QPen(Qt.PenStyle.NoPen), QBrush(QColor("white")))

        for frame in page.frames:
            pen = QPen(QColor("black"), 2) if frame.border else QPen(Qt.PenStyle.NoPen)
            color = QColor.fromRgbF(frame.color.red, frame.color.green, frame.color.blue)
            frame_item = FrameGraphicsItem(frame, self)
            frame_item.setPos(frame.x, frame.y)
            frame_item.setPen(pen)
            frame_item.setBrush(color)
            page_mode = self._editing_frame is None
            frame_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, page_mode)
            frame_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, page_mode)
            if not page_mode and frame is not self._editing_frame:
                frame_item.setOpacity(0.3)
            self.scene.addItem(frame_item)
            self._frame_items[id(frame)] = frame_item
            for graphic_object in frame.objects:
                self._add_object(
                    graphic_object,
                    frame_item,
                    editable=frame is self._editing_frame,
                )
        self.pageChanged.emit(index, len(self._comic.pages))

    def previous_page(self) -> bool:
        if self._page_index == 0:
            return False
        self.show_page(self._page_index - 1)
        return True

    def next_page(self) -> bool:
        if self._comic is None or self._page_index + 1 >= len(self._comic.pages):
            return False
        self.show_page(self._page_index + 1)
        return True

    def add_page(self) -> Page | None:
        if self._comic is None:
            return None
        page = Page()
        destination = self._page_index + 1 if self._comic.pages else 0
        self.undo_stack.push(
            AddPageCommand(self._comic, page, destination, self._show_page_from_command)
        )
        return page

    def delete_current_page(self) -> bool:
        if self._comic is None or len(self._comic.pages) <= 1:
            return False
        page = self.current_page
        if page is None:
            return False
        self.undo_stack.push(
            DeletePageCommand(self._comic, page, self._show_page_from_command)
        )
        return True

    def move_current_page(self, offset: int) -> bool:
        if self._comic is None or self.current_page is None:
            return False
        destination = self._page_index + offset
        if not 0 <= destination < len(self._comic.pages):
            return False
        self.undo_stack.push(
            MovePageCommand(
                self._comic,
                self.current_page,
                destination,
                self._show_page_from_command,
            )
        )
        return True

    def _show_page_from_command(self, index: int) -> None:
        if self._comic is not None and self._comic.pages:
            self.show_page(index)
            return
        self._page_index = 0
        self._frame_items.clear()
        self.scene.clear()
        self.pageChanged.emit(0, 0)

    def enter_frame(self, frame: Frame) -> bool:
        page = self.current_page
        if page is None or not any(candidate is frame for candidate in page.frames):
            return False
        self._editing_frame = frame
        self.show_page(self._page_index)
        self.fitInView(
            QRectF(frame.x, frame.y, frame.width, frame.height),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self.modeChanged.emit(True)
        return True

    def leave_frame(self) -> bool:
        if self._editing_frame is None:
            return False
        self._editing_frame = None
        self.show_page(self._page_index)
        self.fit_page()
        self.modeChanged.emit(False)
        return True

    def add_frame(self) -> Frame | None:
        page = self.current_page
        if page is None or self._comic is None:
            return None
        width = min(400, max(1, self._comic.width - 40))
        height = min(250, max(1, self._comic.height - 40))
        frame = Frame(
            x=(self._comic.width - width) // 2,
            y=(self._comic.height - height) // 2,
            width=width,
            height=height,
        )
        self.undo_stack.push(AddFrameCommand(page, frame, self._refresh_current_page))
        self.select_frame(frame)
        return frame

    def delete_selected_frame(self) -> bool:
        page = self.current_page
        frame = self.selected_frame()
        if page is None or frame is None:
            return False
        self.undo_stack.push(DeleteFrameCommand(page, frame, self._refresh_current_page))
        return True

    def clone_selected_frame(self) -> Frame | None:
        page = self.current_page
        source = self.selected_frame()
        if page is None or source is None:
            return None
        clone = deepcopy(source)
        clone.x += 10
        clone.y += 10
        source_index = next(index for index, frame in enumerate(page.frames) if frame is source)
        self.undo_stack.push(
            AddFrameCommand(
                page,
                clone,
                self._refresh_current_page,
                index=source_index + 1,
                text="Clonar viñeta",
            )
        )
        self.select_frame(clone)
        return clone

    def selected_object(self) -> GraphicObject | None:
        for item in self.scene.selectedItems():
            if isinstance(item, ObjectGraphicsItem):
                return item.graphic_object
        return None

    def select_object(self, graphic_object: GraphicObject) -> bool:
        item = self._object_items.get(id(graphic_object))
        if item is None:
            return False
        self.scene.clearSelection()
        item.setSelected(True)
        return True

    def clone_selected_object(self) -> GraphicObject | None:
        frame = self._editing_frame
        source = self.selected_object()
        if frame is None or source is None:
            return None
        clone = deepcopy(source)
        clone.x += 10
        clone.y += 10
        source_index = next(
            index for index, graphic_object in enumerate(frame.objects) if graphic_object is source
        )
        self.undo_stack.push(
            AddObjectCommand(
                frame,
                clone,
                self._refresh_current_page,
                index=source_index + 1,
                text="Clonar objeto",
            )
        )
        self.select_object(clone)
        return clone

    def delete_selected_object(self) -> bool:
        frame = self._editing_frame
        graphic_object = self.selected_object()
        if frame is None or graphic_object is None:
            return False
        self.undo_stack.push(
            DeleteObjectCommand(frame, graphic_object, self._refresh_current_page)
        )
        return True

    def move_object(
        self,
        graphic_object: GraphicObject,
        new_position: tuple[int, int],
        *,
        old_position: tuple[int, int] | None = None,
    ) -> bool:
        origin = old_position if old_position is not None else (
            graphic_object.x,
            graphic_object.y,
        )
        if origin == new_position:
            self._sync_object_position(graphic_object)
            return False
        self.undo_stack.push(
            MoveObjectCommand(
                graphic_object,
                origin,
                new_position,
                self._sync_object_position,
            )
        )
        return True

    def nudge_selected_object(self, dx: int, dy: int) -> bool:
        graphic_object = self.selected_object()
        if graphic_object is None:
            return False
        return self.move_object(
            graphic_object,
            (graphic_object.x + dx, graphic_object.y + dy),
        )

    def selected_frame(self) -> Frame | None:
        for item in self.scene.selectedItems():
            if isinstance(item, FrameGraphicsItem):
                return item.frame
        return None

    def select_frame(self, frame: Frame) -> bool:
        item = self._frame_items.get(id(frame))
        if item is None:
            return False
        self.scene.clearSelection()
        item.setSelected(True)
        return True

    def move_frame(
        self,
        frame: Frame,
        new_position: tuple[int, int],
        *,
        old_position: tuple[int, int] | None = None,
    ) -> bool:
        origin = old_position if old_position is not None else (frame.x, frame.y)
        if origin == new_position:
            self._sync_frame_position(frame)
            return False
        self.undo_stack.push(
            MoveFrameCommand(frame, origin, new_position, self._sync_frame_position)
        )
        return True

    def nudge_selected_frame(self, dx: int, dy: int) -> bool:
        frame = self.selected_frame()
        if frame is None:
            return False
        return self.move_frame(frame, (frame.x + dx, frame.y + dy))

    def resize_frame(
        self,
        frame: Frame,
        new_size: tuple[int, int],
        *,
        old_size: tuple[int, int] | None = None,
    ) -> bool:
        destination = (
            max(MIN_FRAME_SIZE, new_size[0]),
            max(MIN_FRAME_SIZE, new_size[1]),
        )
        origin = old_size if old_size is not None else (frame.width, frame.height)
        if origin == destination:
            self._sync_frame_geometry(frame)
            return False
        self.undo_stack.push(
            ResizeFrameCommand(frame, origin, destination, self._sync_frame_geometry)
        )
        return True

    def _refresh_current_page(self) -> None:
        if self.current_page is not None:
            self.show_page(self._page_index)

    def _sync_frame_position(self, frame: Frame) -> None:
        item = self._frame_items.get(id(frame))
        if item is not None:
            item.setPos(frame.x, frame.y)

    def _sync_frame_geometry(self, frame: Frame) -> None:
        item = self._frame_items.get(id(frame))
        if item is not None:
            item.setRect(0, 0, frame.width, frame.height)

    def _sync_object_position(self, graphic_object: GraphicObject) -> None:
        item = self._object_items.get(id(graphic_object))
        if item is not None:
            item.setPos(graphic_object.x, graphic_object.y)

    def zoom_in(self) -> None:
        self.scale(1.2, 1.2)

    def zoom_out(self) -> None:
        self.scale(1 / 1.2, 1 / 1.2)

    def reset_zoom(self) -> None:
        self.resetTransform()

    def fit_page(self) -> None:
        if self._comic is not None:
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _add_object(
        self,
        obj: GraphicObject,
        parent: FrameGraphicsItem,
        *,
        editable: bool,
    ) -> None:
        container = ObjectGraphicsItem(obj, self, parent, editable=editable)
        self._object_items[id(obj)] = container
        item: QGraphicsItem
        if isinstance(obj, TextObject):
            text_item = QGraphicsTextItem(obj.text, container)
            text_item.setDefaultTextColor(
                QColor.fromRgbF(obj.color.red, obj.color.green, obj.color.blue)
            )
            text_item.setFont(_font_from_legacy_string(obj.font))
            text_item.setTextWidth(obj.width)
            item = text_item
        elif isinstance(obj, SvgObject):
            resolved = self._resolve_asset(obj.path)
            if resolved is not None:
                svg_item = QGraphicsSvgItem(str(resolved), container)
                bounds = svg_item.boundingRect()
                if bounds.width() and bounds.height():
                    svg_item.setTransform(
                        QTransform.fromScale(
                            obj.width / bounds.width(), obj.height / bounds.height()
                        )
                    )
                item = svg_item
            else:
                item = _missing_asset_item(obj, container)
        elif isinstance(obj, ImageObject):
            resolved = self._resolve_asset(obj.path)
            pixmap = QPixmap(str(resolved)) if resolved is not None else QPixmap()
            if pixmap.isNull():
                item = _missing_asset_item(obj, container)
            else:
                item = QGraphicsPixmapItem(
                    pixmap.scaled(
                        obj.width,
                        obj.height,
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    ),
                    container,
                )
        else:
            return

        container.setPos(obj.x, obj.y)
        container.setTransformOriginPoint(obj.width / 2, obj.height / 2)
        container.setRotation(obj.angle * 180.0 / 3.141592653589793)
        transform = container.transform()
        transform.scale(-1.0 if obj.flip_horizontal else 1.0, -1.0 if obj.flip_vertical else 1.0)
        container.setTransform(transform)
        item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

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


def _missing_asset_item(obj: GraphicObject, parent: QGraphicsItem) -> QGraphicsRectItem:
    item = QGraphicsRectItem(0, 0, obj.width, obj.height, parent)
    item.setPen(QPen(QColor("#b00020"), 2, Qt.PenStyle.DashLine))
    item.setBrush(QColor(255, 220, 220, 100))
    return item
