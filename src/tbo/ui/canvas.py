from __future__ import annotations

from copy import deepcopy
from math import atan2, degrees, radians
from pathlib import Path

from PyQt6.QtCore import QLineF, QPointF, QRectF, QSizeF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QTextCharFormat,
    QTransform,
    QUndoStack,
)
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsPixmapItem,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
    QGraphicsView,
    QPlainTextEdit,
)

from tbo.document.model import (
    Color,
    Comic,
    Frame,
    GraphicObject,
    ImageObject,
    Page,
    ShapeObject,
    SvgObject,
    TextObject,
)
from tbo.geometry import Point as GeoPoint
from tbo.geometry import Rect as GeoRect
from tbo.geometry import normalized_points, resize_rect
from tbo.rendering.shapes import paint_shape_object
from tbo.ui.commands import (
    AddFrameCommand,
    AddObjectCommand,
    AddPageCommand,
    AlignFramesCommand,
    AlignObjectsCommand,
    DeleteFrameCommand,
    DeleteObjectCommand,
    DeletePageCommand,
    EditTextObjectCommand,
    FlipObjectCommand,
    MoveFrameCommand,
    MoveObjectCommand,
    MovePageCommand,
    ReorderObjectCommand,
    ResizeFrameCommand,
    ResizeObjectCommand,
    RotateObjectCommand,
    SetFrameStyleCommand,
    SetShapeStyleCommand,
    TransformFrameCommand,
    TransformObjectCommand,
)

RESIZE_HANDLE_SIZE = 12.0
MIN_FRAME_SIZE = 20
MIN_OBJECT_SIZE = 8
ROTATE_HANDLE_OFFSET = 30.0

TOOL_SELECT = "select"
TOOL_RECT = "rect"
TOOL_ELLIPSE = "ellipse"
TOOL_LINE = "line"
TOOL_FREEHAND = "freehand"
CREATION_TOOLS = (TOOL_RECT, TOOL_ELLIPSE, TOOL_LINE, TOOL_FREEHAND)

HANDLE_CURSORS = {
    "n": Qt.CursorShape.SizeVerCursor,
    "s": Qt.CursorShape.SizeVerCursor,
    "e": Qt.CursorShape.SizeHorCursor,
    "w": Qt.CursorShape.SizeHorCursor,
    "ne": Qt.CursorShape.SizeBDiagCursor,
    "sw": Qt.CursorShape.SizeBDiagCursor,
    "nw": Qt.CursorShape.SizeFDiagCursor,
    "se": Qt.CursorShape.SizeFDiagCursor,
}


def _visual_transform(
    width: int, height: int, angle: float, flip_horizontal: bool, flip_vertical: bool
) -> QTransform:
    center_x = width / 2
    center_y = height / 2
    transform = QTransform()
    transform.translate(center_x, center_y)
    transform.rotate(degrees(angle))
    transform.scale(-1.0 if flip_horizontal else 1.0, -1.0 if flip_vertical else 1.0)
    transform.translate(-center_x, -center_y)
    return transform


def _handle_rects(rect: QRectF) -> dict[str, QRectF]:
    size = RESIZE_HANDLE_SIZE
    half = size / 2
    center = rect.center()
    positions = {
        "nw": QPointF(rect.left(), rect.top()),
        "n": QPointF(center.x() - half, rect.top()),
        "ne": QPointF(rect.right() - size, rect.top()),
        "e": QPointF(rect.right() - size, center.y() - half),
        "se": QPointF(rect.right() - size, rect.bottom() - size),
        "s": QPointF(center.x() - half, rect.bottom() - size),
        "sw": QPointF(rect.left(), rect.bottom() - size),
        "w": QPointF(rect.left(), center.y() - half),
    }
    return {name: QRectF(position, QSizeF(size, size)) for name, position in positions.items()}


def _rotate_handle_rect(rect: QRectF) -> QRectF:
    size = RESIZE_HANDLE_SIZE + 2
    center_x = rect.center().x()
    return QRectF(center_x - size / 2, rect.top() - ROTATE_HANDLE_OFFSET - size / 2, size, size)


def _paint_transform_handles(painter: QPainter, rect: QRectF, *, with_rotate: bool) -> None:
    for handle in _handle_rects(rect).values():
        painter.fillRect(handle, QColor("#f4c430"))
        painter.setPen(QPen(QColor("#6b5600"), 1))
        painter.drawRect(handle)
    if with_rotate:
        handle = _rotate_handle_rect(rect)
        painter.setPen(QPen(QColor("#1677ff"), 1))
        painter.drawLine(QLineF(rect.center().x(), rect.top(), handle.center().x(), handle.bottom()))
        painter.setBrush(QColor("#1677ff"))
        painter.drawEllipse(handle)


def _hit_handle(rect: QRectF, position: QPointF) -> str | None:
    for name, handle in _handle_rects(rect).items():
        if handle.adjusted(-2, -2, 2, 2).contains(position):
            return name
    return None


class _TransformMixin:
    """Resize-handle behaviour shared by panels and objects.

    Expects ``self._canvas``, ``self.rect()``, ``self.setRect()`` and
    the ``_apply_live_geometry``/``_commit_geometry`` hooks.
    """

    _active_handle: str | None
    _rotating: bool
    _transform_scene_start: QPointF
    _transform_pos_start: QPointF
    _transform_size_start: tuple[int, int]
    _transform_angle_start: float
    _rotate_scene_start_angle: float

    def _begin_transform(self, event: QGraphicsSceneMouseEvent, handle: str) -> None:
        self._active_handle = handle
        self._transform_scene_start = QPointF(event.scenePos())
        self._transform_pos_start = QPointF(self.pos())
        self._transform_size_start = (round(self.rect().width()), round(self.rect().height()))
        self.setSelected(True)

    def _begin_rotation(self, event: QGraphicsSceneMouseEvent) -> None:
        self._rotating = True
        self._transform_angle_start = self._model_angle()
        scene_center = self.mapToScene(self.rect().center())
        self._rotate_scene_start_angle = atan2(
            event.scenePos().y() - scene_center.y(), event.scenePos().x() - scene_center.x()
        )
        self.setSelected(True)

    def _model_angle(self) -> float:
        return 0.0

    def _update_transform(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._rotating:
            scene_center = self.mapToScene(self.rect().center())
            angle = atan2(
                event.scenePos().y() - scene_center.y(), event.scenePos().x() - scene_center.x()
            )
            delta = angle - self._rotate_scene_start_angle
            new_angle = self._transform_angle_start + delta
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                step = radians(15.0)
                new_angle = round(new_angle / step) * step
            self._apply_live_rotation(new_angle)
            return
        if self._active_handle is None:
            return
        local_now = self.mapFromScene(event.scenePos())
        local_start = self.mapFromScene(self._transform_scene_start)
        delta = GeoPoint(local_now.x() - local_start.x(), local_now.y() - local_start.y())
        start_width, start_height = self._transform_size_start
        result = resize_rect(
            GeoRect(0.0, 0.0, float(start_width), float(start_height)),
            self._active_handle,
            delta,
            keep_aspect=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier),
            from_center=bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier),
            min_size=float(self._min_size()),
        )
        offset_x = result.x + result.width / 2 - start_width / 2
        offset_y = result.y + result.height / 2 - start_height / 2
        mapped = self._map_vector(offset_x, offset_y)
        new_pos = QPointF(
            self._transform_pos_start.x() + mapped.x(),
            self._transform_pos_start.y() + mapped.y(),
        )
        self._apply_live_geometry(new_pos, result.width, result.height)

    def _finish_transform(self) -> None:
        if self._rotating:
            self._rotating = False
            new_angle = self._model_angle()
            self._commit_rotation(self._transform_angle_start, new_angle)
            return
        if self._active_handle is None:
            return
        self._active_handle = None
        self._commit_geometry(
            (round(self.pos().x()), round(self.pos().y())),
            (
                max(self._min_size(), round(self.rect().width())),
                max(self._min_size(), round(self.rect().height())),
            ),
            (round(self._transform_pos_start.x()), round(self._transform_pos_start.y())),
            self._transform_size_start,
        )

    def _map_vector(self, dx: float, dy: float) -> QPointF:
        transform = self.transform()
        origin = transform.map(QPointF(0.0, 0.0))
        mapped = transform.map(QPointF(dx, dy))
        return QPointF(mapped.x() - origin.x(), mapped.y() - origin.y())

    def _min_size(self) -> int:
        return MIN_OBJECT_SIZE

    # Hooks overridden by the concrete item classes.
    def _apply_live_geometry(self, position: QPointF, width: float, height: float) -> None:
        raise NotImplementedError

    def _apply_live_rotation(self, angle: float) -> None:
        raise NotImplementedError

    def _commit_geometry(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        old_position: tuple[int, int],
        old_size: tuple[int, int],
    ) -> None:
        raise NotImplementedError

    def _commit_rotation(self, old_angle: float, new_angle: float) -> None:
        raise NotImplementedError


class FrameGraphicsItem(_TransformMixin, QGraphicsRectItem):
    def __init__(self, frame: Frame, canvas: ComicCanvas) -> None:
        super().__init__(0, 0, frame.width, frame.height)
        self.frame = frame
        self._canvas = canvas
        self._drag_start = (frame.x, frame.y)
        self._active_handle: str | None = None
        self._rotating = False
        self._transform_scene_start = QPointF()
        self._transform_pos_start = QPointF()
        self._transform_size_start = (frame.width, frame.height)
        self._transform_angle_start = 0.0
        self._rotate_scene_start_angle = 0.0
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemClipsChildrenToShape
        )
        self.setAcceptHoverEvents(True)

    def paint(self, painter, option, widget=None) -> None:
        super().paint(painter, option, widget)
        if self.isSelected():
            _paint_transform_handles(painter, self.rect(), with_rotate=False)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        tool = self._canvas.tool
        if tool != TOOL_SELECT:
            if self._canvas.editing_frame is self.frame:
                self._canvas.begin_creation(self, event.pos())
                event.accept()
            return
        if (
            self._canvas.editing_frame is None
            and event.button() == Qt.MouseButton.LeftButton
        ):
            handle = _hit_handle(self.rect(), event.pos())
            if handle is not None:
                self._begin_transform(event, handle)
                event.accept()
                return
        self._drag_start = (self.frame.x, self.frame.y)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._canvas.tool != TOOL_SELECT:
            return
        if self._canvas.editing_frame is None:
            self._canvas.enter_frame(self.frame)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if (
            self._canvas._creation_tool is not None
            and self._canvas._creation_frame_item is self
        ):
            self._canvas.update_creation(event.pos())
            event.accept()
            return
        if self._active_handle is not None:
            self._update_transform(event)
            event.accept()
            return
        super().mouseMoveEvent(event)
        if self._canvas._snap_to_grid:
            grid = self._canvas._grid_size
            self.setPos(
                round(self.pos().x() / grid) * grid,
                round(self.pos().y() / grid) * grid,
            )

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if (
            self._canvas._creation_tool is not None
            and self._canvas._creation_frame_item is self
        ):
            self._canvas.update_creation(event.pos())
            self._canvas.finish_creation()
            event.accept()
            return
        if self._active_handle is not None:
            self._finish_transform()
            event.accept()
            return
        super().mouseReleaseEvent(event)
        destination = (round(self.pos().x()), round(self.pos().y()))
        if destination == self._drag_start:
            self.setPos(*self._drag_start)
            return
        self._canvas.move_frame(self.frame, destination, old_position=self._drag_start)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self._canvas.tool != TOOL_SELECT:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            handle = _hit_handle(self.rect(), event.pos())
            self.setCursor(HANDLE_CURSORS.get(handle, Qt.CursorShape.ArrowCursor))
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def _min_size(self) -> int:
        return MIN_FRAME_SIZE

    def _apply_live_geometry(self, position: QPointF, width: float, height: float) -> None:
        self.setRect(0, 0, width, height)
        self.setPos(position)

    def _apply_live_rotation(self, angle: float) -> None:  # pragma: no cover - panels never rotate
        pass

    def _commit_geometry(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        old_position: tuple[int, int],
        old_size: tuple[int, int],
    ) -> None:
        self._canvas.transform_frame(
            self.frame,
            (position[0], position[1], size[0], size[1]),
            old_geometry=(old_position[0], old_position[1], old_size[0], old_size[1]),
        )

    def _commit_rotation(self, old_angle: float, new_angle: float) -> None:  # pragma: no cover
        pass


class ObjectGraphicsItem(_TransformMixin, QGraphicsRectItem):
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
        self._content: QGraphicsItem | None = None
        self._natural_size: tuple[int, int] | None = None
        self._drag_start = (graphic_object.x, graphic_object.y)
        self._active_handle: str | None = None
        self._rotating = False
        self._transform_scene_start = QPointF()
        self._transform_pos_start = QPointF()
        self._transform_size_start = (graphic_object.width, graphic_object.height)
        self._transform_angle_start = 0.0
        self._rotate_scene_start_angle = 0.0
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

    def set_content(
        self, content: QGraphicsItem, *, natural_size: tuple[int, int] | None = None
    ) -> None:
        self._content = content
        self._natural_size = natural_size

    def _content_item(self) -> QGraphicsItem | None:
        children = self.childItems()
        return children[0] if children else None

    def paint(self, painter, option, widget=None) -> None:
        if isinstance(self.graphic_object, ShapeObject):
            paint_shape_object(painter, self.graphic_object, self.rect())
        super().paint(painter, option, widget)
        if self.isSelected():
            painter.setPen(QPen(QColor("#1677ff"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            painter.drawRect(self.rect())
            if self.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
                _paint_transform_handles(painter, self.rect(), with_rotate=True)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._canvas.tool != TOOL_SELECT:
            event.ignore()
            return
        if (
            self._canvas.editing_frame is not None
            and event.button() == Qt.MouseButton.LeftButton
        ):
            if self.isSelected() and _rotate_handle_rect(self.rect()).contains(event.pos()):
                self._begin_rotation(event)
                event.accept()
                return
            handle = _hit_handle(self.rect(), event.pos())
            if handle is not None:
                self._begin_transform(event, handle)
                event.accept()
                return
        self._drag_start = (self.graphic_object.x, self.graphic_object.y)
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._canvas.tool != TOOL_SELECT:
            return
        if isinstance(self.graphic_object, TextObject):
            self._canvas.start_inline_text_edit(self)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._active_handle is not None or self._rotating:
            self._update_transform(event)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._active_handle is not None or self._rotating:
            self._finish_transform()
            event.accept()
            return
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

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if self._canvas.tool != TOOL_SELECT:
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif self.isSelected() and _rotate_handle_rect(self.rect()).contains(event.pos()):
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            handle = _hit_handle(self.rect(), event.pos())
            self.setCursor(HANDLE_CURSORS.get(handle, Qt.CursorShape.ArrowCursor))
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def _min_size(self) -> int:
        return MIN_OBJECT_SIZE

    def _model_angle(self) -> float:
        return self.graphic_object.angle

    def _apply_live_geometry(self, position: QPointF, width: float, height: float) -> None:
        self.setRect(0, 0, width, height)
        self.setPos(position)
        self._update_content_scale(width, height)

    def _apply_live_rotation(self, angle: float) -> None:
        obj = self.graphic_object
        self.setTransform(
            _visual_transform(
                obj.width,
                obj.height,
                angle,
                obj.flip_horizontal,
                obj.flip_vertical,
            )
        )

    def _commit_geometry(
        self,
        position: tuple[int, int],
        size: tuple[int, int],
        old_position: tuple[int, int],
        old_size: tuple[int, int],
    ) -> None:
        self._canvas.transform_object(
            self.graphic_object,
            (position[0], position[1], size[0], size[1]),
            old_geometry=(old_position[0], old_position[1], old_size[0], old_size[1]),
        )

    def _commit_rotation(self, old_angle: float, new_angle: float) -> None:
        self._canvas.rotate_object(self.graphic_object, old_angle, new_angle)

    def _update_content_scale(self, width: float, height: float) -> None:
        content = self._content_item()
        if content is None:
            return
        if isinstance(content, QGraphicsTextItem):
            content.setTextWidth(width)
            return
        if self._natural_size is None:
            return
        natural_width, natural_height = self._natural_size
        if natural_width <= 0 or natural_height <= 0:
            return
        content.setTransform(QTransform.fromScale(width / natural_width, height / natural_height))


class ComicCanvas(QGraphicsView):
    pageChanged = pyqtSignal(int, int)
    modeChanged = pyqtSignal(bool)
    zoomChanged = pyqtSignal(int)
    assetDropped = pyqtSignal(Path)
    toolChanged = pyqtSignal(str)

    def __init__(self, asset_root: Path | None = None) -> None:
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self._asset_root = asset_root
        self._comic: Comic | None = None
        self._page_index = 0
        self._frame_items: dict[int, FrameGraphicsItem] = {}
        self._object_items: dict[int, ObjectGraphicsItem] = {}
        self._editing_frame: Frame | None = None
        self._snap_to_grid = False
        self._grid_size = 10
        self._inline_proxy: QGraphicsProxyWidget | None = None
        self._inline_editor: InlineTextEditor | None = None
        self._inline_object: TextObject | None = None
        self._tool = TOOL_SELECT
        self._creation_frame_item: FrameGraphicsItem | None = None
        self._creation_tool: str | None = None
        self._creation_start = QPointF()
        self._creation_current = QPointF()
        self._creation_points: list[QPointF] = []
        self._creation_preview: QGraphicsItem | None = None
        self.default_shape_style: tuple[Color | None, Color, int] = (
            Color(1.0, 1.0, 1.0),
            Color(0.0, 0.0, 0.0),
            2,
        )
        self.undo_stack = QUndoStack(self)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setBackgroundBrush(QColor("#707070"))
        self._base_drag_mode = QGraphicsView.DragMode.RubberBandDrag
        self.setDragMode(self._base_drag_mode)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setAcceptDrops(True)

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

    @property
    def tool(self) -> str:
        return self._tool

    def set_tool(self, tool: str) -> None:
        if tool not in (TOOL_SELECT, *CREATION_TOOLS):
            raise ValueError(f"unknown tool {tool!r}")
        self.cancel_creation()
        self._tool = tool
        if tool == TOOL_SELECT:
            self.setDragMode(self._base_drag_mode)
            self.viewport().unsetCursor()
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.viewport().setCursor(Qt.CursorShape.CrossCursor)
        self.toolChanged.emit(tool)

    def cancel_active_tool(self) -> bool:
        """Cancel an in-progress creation or leave creation mode.

        Returns ``True`` when something was cancelled.  Wired to the
        Escape shortcut so Esc backs out step by step.
        """
        if self._creation_tool is not None:
            self.cancel_creation()
            return True
        if self._tool != TOOL_SELECT:
            self.set_tool(TOOL_SELECT)
            return True
        return False

    def set_snap_to_grid(self, enabled: bool) -> None:
        self._snap_to_grid = enabled
        self.viewport().update()

    def _snap_value(self, value: int) -> int:
        if not self._snap_to_grid:
            return value
        return round(value / self._grid_size) * self._grid_size

    def drawBackground(self, painter, rect) -> None:
        super().drawBackground(painter, rect)
        if not self._snap_to_grid or self._grid_size <= 0:
            return
        left = int(rect.left() // self._grid_size) * self._grid_size
        top = int(rect.top() // self._grid_size) * self._grid_size
        right = int(rect.right())
        bottom = int(rect.bottom())
        pen = QPen(QColor(0, 0, 0, 40), 1)
        painter.setPen(pen)
        x = left
        while x <= right:
            painter.drawLine(x, int(rect.top()), x, bottom)
            x += self._grid_size
        y = top
        while y <= bottom:
            painter.drawLine(int(rect.left()), y, right, y)
            y += self._grid_size

    def set_comic(self, comic: Comic) -> None:
        self._comic = comic
        self._page_index = 0
        self._editing_frame = None
        self.cancel_creation()
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
        self.cancel_creation()
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
        self.undo_stack.push(DeletePageCommand(self._comic, page, self._show_page_from_command))
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
        self.zoomChanged.emit(self.zoom_percent())
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

    def selected_frames(self) -> list[Frame]:
        return [
            item.frame for item in self.scene.selectedItems() if isinstance(item, FrameGraphicsItem)
        ]

    def select_all(self) -> bool:
        count = 0
        for item in self.scene.items():
            if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
                item.setSelected(True)
                count += 1
        return count > 0

    def add_frames(self, frames: list[Frame]) -> bool:
        page = self.current_page
        if page is None or not frames:
            return False
        self.undo_stack.beginMacro(self.tr("Paste panels"))
        for frame in frames:
            self.undo_stack.push(AddFrameCommand(page, frame, self._refresh_current_page))
        self.undo_stack.endMacro()
        return True

    def add_objects(self, objects: list[GraphicObject]) -> bool:
        frame = self._editing_frame
        if frame is None or not objects:
            return False
        self.undo_stack.beginMacro(self.tr("Paste objects"))
        for graphic_object in objects:
            self.undo_stack.push(
                AddObjectCommand(frame, graphic_object, self._refresh_current_page)
            )
        self.undo_stack.endMacro()
        return True

    def delete_selected_frame(self) -> bool:
        page = self.current_page
        frames = self.selected_frames()
        if page is None or not frames:
            return False
        self.undo_stack.beginMacro(self.tr("Delete panels"))
        for frame in frames:
            self.undo_stack.push(DeleteFrameCommand(page, frame, self._refresh_current_page))
        self.undo_stack.endMacro()
        return True

    def align_selected_frames(self, mode: str) -> bool:
        frames = self.selected_frames()
        if len(frames) < 2:
            return False
        target = _alignment_target(frames, mode)
        old_positions = [(frame.x, frame.y) for frame in frames]
        new_positions = [target(frame) for frame in frames]
        self.undo_stack.push(
            AlignFramesCommand(frames, old_positions, new_positions, self._refresh_current_page)
        )
        return True

    def distribute_selected_frames(self, axis: str) -> bool:
        frames = self.selected_frames()
        if len(frames) < 3:
            return False
        old_positions = [(frame.x, frame.y) for frame in frames]
        new_positions = _distribution_positions(frames, axis)
        self.undo_stack.push(
            AlignFramesCommand(frames, old_positions, new_positions, self._refresh_current_page)
        )
        return True

    def align_selected_objects(self, mode: str) -> bool:
        objects = self.selected_objects()
        if len(objects) < 2:
            return False
        target = _alignment_target(objects, mode)
        old_positions = [(obj.x, obj.y) for obj in objects]
        new_positions = [target(obj) for obj in objects]
        self.undo_stack.push(
            AlignObjectsCommand(objects, old_positions, new_positions, self._refresh_current_page)
        )
        return True

    def distribute_selected_objects(self, axis: str) -> bool:
        objects = self.selected_objects()
        if len(objects) < 3:
            return False
        old_positions = [(obj.x, obj.y) for obj in objects]
        new_positions = _distribution_positions(objects, axis)
        self.undo_stack.push(
            AlignObjectsCommand(objects, old_positions, new_positions, self._refresh_current_page)
        )
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
                text=self.tr("Clone panel"),
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
                text=self.tr("Clone object"),
            )
        )
        self.select_object(clone)
        return clone

    def add_graphic_object(self, graphic_object: GraphicObject) -> bool:
        frame = self._editing_frame
        if frame is None:
            return False
        self.undo_stack.push(AddObjectCommand(frame, graphic_object, self._refresh_current_page))
        self.select_object(graphic_object)
        return True

    def selected_objects(self) -> list[GraphicObject]:
        return [
            item.graphic_object
            for item in self.scene.selectedItems()
            if isinstance(item, ObjectGraphicsItem)
        ]

    def delete_selected_object(self) -> bool:
        frame = self._editing_frame
        objects = self.selected_objects()
        if frame is None or not objects:
            return False
        self.undo_stack.beginMacro(self.tr("Delete objects"))
        for graphic_object in objects:
            self.undo_stack.push(
                DeleteObjectCommand(frame, graphic_object, self._refresh_current_page)
            )
        self.undo_stack.endMacro()
        return True

    def rotate_selected_object(self, delta_degrees: float) -> bool:
        graphic_object = self.selected_object()
        if graphic_object is None:
            return False
        old_angle = graphic_object.angle
        new_angle = old_angle + radians(delta_degrees)
        return self.rotate_object(graphic_object, old_angle, new_angle)

    def rotate_object(
        self, graphic_object: GraphicObject, old_angle: float, new_angle: float
    ) -> bool:
        if old_angle == new_angle:
            self._sync_object_transform(graphic_object)
            return False
        self.undo_stack.push(
            RotateObjectCommand(
                graphic_object,
                old_angle,
                new_angle,
                self._sync_object_transform,
            )
        )
        return True

    def flip_selected_object(self, axis: str) -> bool:
        graphic_object = self.selected_object()
        if graphic_object is None:
            return False
        self.undo_stack.push(FlipObjectCommand(graphic_object, axis, self._sync_object_transform))
        return True

    def resize_object(
        self,
        graphic_object: GraphicObject,
        new_size: tuple[int, int],
        *,
        old_size: tuple[int, int] | None = None,
    ) -> bool:
        origin = old_size if old_size is not None else (graphic_object.width, graphic_object.height)
        destination = (max(1, new_size[0]), max(1, new_size[1]))
        return self.transform_object(
            graphic_object,
            (graphic_object.x, graphic_object.y, destination[0], destination[1]),
            old_geometry=(graphic_object.x, graphic_object.y, origin[0], origin[1]),
        )

    def transform_object(
        self,
        graphic_object: GraphicObject,
        new_geometry: tuple[int, int, int, int],
        *,
        old_geometry: tuple[int, int, int, int] | None = None,
    ) -> bool:
        origin = (
            old_geometry
            if old_geometry is not None
            else (graphic_object.x, graphic_object.y, graphic_object.width, graphic_object.height)
        )
        destination = (
            new_geometry[0],
            new_geometry[1],
            max(MIN_OBJECT_SIZE, new_geometry[2]),
            max(MIN_OBJECT_SIZE, new_geometry[3]),
        )
        if origin == destination:
            self._sync_object_geometry(graphic_object)
            return False
        self.undo_stack.push(
            TransformObjectCommand(graphic_object, origin, destination, self._sync_object_geometry)
        )
        return True

    def transform_frame(
        self,
        frame: Frame,
        new_geometry: tuple[int, int, int, int],
        *,
        old_geometry: tuple[int, int, int, int] | None = None,
    ) -> bool:
        origin = (
            old_geometry
            if old_geometry is not None
            else (frame.x, frame.y, frame.width, frame.height)
        )
        destination = (
            new_geometry[0],
            new_geometry[1],
            max(MIN_FRAME_SIZE, new_geometry[2]),
            max(MIN_FRAME_SIZE, new_geometry[3]),
        )
        if origin == destination:
            self._sync_frame_geometry(frame)
            return False
        self.undo_stack.push(
            TransformFrameCommand(frame, origin, destination, self._sync_frame_geometry)
        )
        return True

    def reorder_selected_object(self, mode: str) -> bool:
        frame = self._editing_frame
        graphic_object = self.selected_object()
        if frame is None or graphic_object is None:
            return False
        old_index = next(index for index, obj in enumerate(frame.objects) if obj is graphic_object)
        if mode == "front":
            new_index = len(frame.objects) - 1
        elif mode == "back":
            new_index = 0
        elif mode == "up":
            new_index = old_index + 1
        elif mode == "down":
            new_index = old_index - 1
        else:
            raise ValueError(f"unknown reorder mode {mode!r}")
        if not 0 <= new_index < len(frame.objects):
            return False
        self.undo_stack.push(
            ReorderObjectCommand(
                frame,
                graphic_object,
                old_index,
                new_index,
                self._refresh_current_page,
            )
        )
        # The refresh rebuilds the scene items and clears the selection.
        self.select_object(graphic_object)
        return True

    def set_shape_style(
        self,
        fill: Color | None,
        stroke: Color,
        stroke_width: int,
    ) -> bool:
        graphic_object = self.selected_object()
        if not isinstance(graphic_object, ShapeObject):
            return False
        old_style = (graphic_object.fill, graphic_object.stroke, graphic_object.stroke_width)
        new_style = (fill, stroke, max(1, stroke_width))
        if old_style == new_style:
            return False
        self.undo_stack.push(
            SetShapeStyleCommand(graphic_object, old_style, new_style, self._sync_object_transform)
        )
        return True

    def set_frame_style(self, color: Color, border: bool | None = None) -> bool:
        frame = self.selected_frame()
        if frame is None:
            return False
        new_border = frame.border if border is None else border
        old_style = (frame.color, frame.border)
        new_style = (color, new_border)
        if old_style == new_style:
            return False
        self.undo_stack.push(
            SetFrameStyleCommand(frame, old_style, new_style, self._refresh_current_page)
        )
        return True

    def edit_text_object(
        self,
        text_object: TextObject,
        new_text: str,
        new_font: str,
        new_color: Color,
        new_bold: bool | None = None,
        new_italic: bool | None = None,
        new_underline: bool | None = None,
    ) -> bool:
        old_text = text_object.text
        old_font = text_object.font
        old_color = text_object.color
        old_style = (text_object.bold, text_object.italic, text_object.underline)
        new_style = (
            text_object.bold if new_bold is None else new_bold,
            text_object.italic if new_italic is None else new_italic,
            text_object.underline if new_underline is None else new_underline,
        )
        if (
            new_text == old_text
            and new_font == old_font
            and new_color == old_color
            and new_style == old_style
        ):
            return False
        self.undo_stack.push(
            EditTextObjectCommand(
                text_object,
                old_text,
                new_text,
                old_font,
                new_font,
                old_color,
                new_color,
                old_style,
                new_style,
                lambda _object: self._refresh_current_page(),
            )
        )
        self.select_object(text_object)
        return True

    def start_inline_text_edit(self, item: ObjectGraphicsItem) -> None:
        if self._editing_frame is None or self._inline_proxy is not None:
            return
        graphic_object = item.graphic_object
        if not isinstance(graphic_object, TextObject):
            return
        editor = InlineTextEditor(
            graphic_object.text,
            _font_from_legacy_string(graphic_object.font),
            QColor.fromRgbF(
                graphic_object.color.red, graphic_object.color.green, graphic_object.color.blue
            ),
        )
        editor.setFixedSize(max(1, graphic_object.width), max(1, graphic_object.height))
        proxy = self.scene.addWidget(editor)
        proxy.setPos(item.scenePos())
        proxy.setZValue(1000)
        self._inline_proxy = proxy
        self._inline_editor = editor
        self._inline_object = graphic_object
        editor.accepted.connect(self._accept_inline_text)
        editor.canceled.connect(self._cancel_inline_text)
        editor.setFocus()

    def _accept_inline_text(self) -> None:
        self._finish_inline_text_edit(True)

    def _cancel_inline_text(self) -> None:
        self._finish_inline_text_edit(False)

    def _finish_inline_text_edit(self, accepted: bool) -> None:
        editor = self._inline_editor
        proxy = self._inline_proxy
        graphic_object = self._inline_object
        self._inline_proxy = None
        self._inline_editor = None
        self._inline_object = None
        if editor is not None:
            try:
                editor.accepted.disconnect(self._accept_inline_text)
                editor.canceled.disconnect(self._cancel_inline_text)
            except TypeError:
                pass
            editor.setVisible(False)
        if proxy is not None:
            self.scene.removeItem(proxy)
        if accepted and editor is not None and graphic_object is not None:
            new_text = editor.toPlainText().strip()
            if new_text:
                self.edit_text_object(
                    graphic_object, new_text, graphic_object.font, graphic_object.color
                )
            else:
                self._refresh_current_page()

    def move_object(
        self,
        graphic_object: GraphicObject,
        new_position: tuple[int, int],
        *,
        old_position: tuple[int, int] | None = None,
    ) -> bool:
        origin = (
            old_position
            if old_position is not None
            else (
                graphic_object.x,
                graphic_object.y,
            )
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
        snapped = (self._snap_value(new_position[0]), self._snap_value(new_position[1]))
        if origin == snapped:
            self._sync_frame_position(frame)
            return False
        self.undo_stack.push(MoveFrameCommand(frame, origin, snapped, self._sync_frame_position))
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
            max(MIN_FRAME_SIZE, self._snap_value(new_size[0])),
            max(MIN_FRAME_SIZE, self._snap_value(new_size[1])),
        )
        origin = old_size if old_size is not None else (frame.width, frame.height)
        return self.transform_frame(
            frame,
            (frame.x, frame.y, destination[0], destination[1]),
            old_geometry=(frame.x, frame.y, origin[0], origin[1]),
        )

    # --- Creation tools -------------------------------------------------

    def begin_creation(self, frame_item: FrameGraphicsItem, position: QPointF) -> None:
        if self._tool not in CREATION_TOOLS or self._editing_frame is not frame_item.frame:
            return
        if self._frame_items.get(id(frame_item.frame)) is not frame_item:
            # Stale graphics item from a previous scene refresh.
            return
        self.cancel_creation()
        self._creation_frame_item = frame_item
        self._creation_tool = self._tool
        self._creation_start = QPointF(position)
        self._creation_current = QPointF(position)
        self._creation_points = [QPointF(position)]
        preview: QGraphicsItem
        pen = QPen(QColor("#1677ff"), 2, Qt.PenStyle.DashLine)
        if self._tool == TOOL_RECT:
            preview = QGraphicsRectItem(frame_item)
            preview.setPen(pen)
        elif self._tool == TOOL_ELLIPSE:
            preview = QGraphicsEllipseItem(frame_item)
            preview.setPen(pen)
        elif self._tool == TOOL_LINE:
            preview = QGraphicsLineItem(frame_item)
            preview.setPen(pen)
        else:
            preview = QGraphicsPathItem(frame_item)
            stroke = QPen(QColor("#1677ff"), 2)
            stroke.setCapStyle(Qt.PenCapStyle.RoundCap)
            stroke.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            preview.setPen(stroke)
        preview.setZValue(1000)
        preview.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._creation_preview = preview

    def update_creation(self, position: QPointF) -> None:
        preview = self._creation_preview
        if preview is None or self._creation_tool is None:
            return
        self._creation_current = QPointF(position)
        if self._creation_tool in (TOOL_RECT, TOOL_ELLIPSE):
            preview.setRect(QRectF(self._creation_start, position).normalized())
        elif self._creation_tool == TOOL_LINE:
            preview.setLine(QLineF(self._creation_start, position))
        else:
            last = self._creation_points[-1]
            if (position - last).manhattanLength() < 1.5:
                return
            self._creation_points.append(QPointF(position))
            path = QPainterPath(self._creation_points[0])
            for point in self._creation_points[1:]:
                path.lineTo(point)
            preview.setPath(path)

    def finish_creation(self) -> None:
        tool = self._creation_tool
        start = QPointF(self._creation_start)
        current = QPointF(self._creation_current)
        points = [QPointF(point) for point in self._creation_points]
        self.cancel_creation()
        if tool is None:
            return
        graphic_object: ShapeObject | None = None
        fill, stroke, stroke_width = self.default_shape_style
        if tool in (TOOL_RECT, TOOL_ELLIPSE):
            rect = QRectF(start, current).normalized()
            if rect.width() < 2 or rect.height() < 2:
                return
            graphic_object = ShapeObject(
                x=round(rect.x()),
                y=round(rect.y()),
                width=max(1, round(rect.width())),
                height=max(1, round(rect.height())),
                kind=tool,
                fill=fill,
                stroke=stroke,
                stroke_width=stroke_width,
            )
        elif tool == TOOL_LINE:
            rect = QRectF(start, current).normalized()
            if rect.width() < 1 and rect.height() < 1:
                return
            absolute = [(start.x(), start.y()), (current.x(), current.y())]
            graphic_object = ShapeObject(
                x=round(rect.x()),
                y=round(rect.y()),
                width=max(1, round(rect.width())),
                height=max(1, round(rect.height())),
                kind=TOOL_LINE,
                fill=None,
                stroke=stroke,
                stroke_width=stroke_width,
                points=normalized_points(
                    absolute,
                    GeoRect(rect.x(), rect.y(), max(1.0, rect.width()), max(1.0, rect.height())),
                ),
            )
        elif tool == TOOL_FREEHAND:
            if len(points) < 2:
                return
            xs = [point.x() for point in points]
            ys = [point.y() for point in points]
            rect = QRectF(
                min(xs), min(ys), max(1.0, max(xs) - min(xs)), max(1.0, max(ys) - min(ys))
            )
            absolute = [(point.x(), point.y()) for point in points]
            graphic_object = ShapeObject(
                x=round(rect.x()),
                y=round(rect.y()),
                width=max(1, round(rect.width())),
                height=max(1, round(rect.height())),
                kind=TOOL_FREEHAND,
                fill=None,
                stroke=stroke,
                stroke_width=stroke_width,
                points=normalized_points(
                    absolute, GeoRect(rect.x(), rect.y(), rect.width(), rect.height())
                ),
            )
        if graphic_object is None:
            return
        self.add_graphic_object(graphic_object)

    def cancel_creation(self) -> None:
        preview = self._creation_preview
        self._creation_preview = None
        self._creation_tool = None
        self._creation_frame_item = None
        self._creation_points = []
        if preview is not None:
            try:
                scene = preview.scene()
            except RuntimeError:
                scene = None
            if scene is not None:
                scene.removeItem(preview)

    # --- Synchronisation -----------------------------------------------

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
            item.setPos(frame.x, frame.y)

    def _sync_object_position(self, graphic_object: GraphicObject) -> None:
        item = self._object_items.get(id(graphic_object))
        if item is not None:
            item.setPos(graphic_object.x, graphic_object.y)

    def _sync_object_geometry(self, graphic_object: GraphicObject) -> None:
        item = self._object_items.get(id(graphic_object))
        if item is not None:
            item.setPos(graphic_object.x, graphic_object.y)
            item.setRect(0, 0, graphic_object.width, graphic_object.height)
            item._update_content_scale(graphic_object.width, graphic_object.height)
            self._apply_object_visual_transform(item, graphic_object)

    def _sync_object_transform(self, graphic_object: GraphicObject) -> None:
        item = self._object_items.get(id(graphic_object))
        if item is not None:
            self._apply_object_visual_transform(item, graphic_object)

    def _apply_object_visual_transform(
        self, item: ObjectGraphicsItem, graphic_object: GraphicObject
    ) -> None:
        item.setRect(0, 0, graphic_object.width, graphic_object.height)
        item.setTransform(
            _visual_transform(
                graphic_object.width,
                graphic_object.height,
                graphic_object.angle,
                graphic_object.flip_horizontal,
                graphic_object.flip_vertical,
            )
        )

    # --- Zoom ----------------------------------------------------------

    def zoom_in(self) -> None:
        self._zoom_by(1.2)

    def zoom_out(self) -> None:
        self._zoom_by(1 / 1.2)

    def reset_zoom(self) -> None:
        self.resetTransform()
        self.zoomChanged.emit(self.zoom_percent())

    def fit_page(self) -> None:
        if self._comic is not None:
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.zoomChanged.emit(self.zoom_percent())

    def zoom_percent(self) -> int:
        return round(self.transform().m11() * 100)

    def _zoom_by(self, factor: float) -> None:
        center = self.viewport().rect().center()
        self._zoom_at(QPointF(center), factor)

    def _zoom_at(self, view_position: QPointF, factor: float) -> None:
        scene_before = self.mapToScene(view_position.toPoint())
        self.scale(factor, factor)
        scene_after = self.mapToScene(view_position.toPoint())
        delta = scene_after - scene_before
        self.translate(delta.x(), delta.y())
        self.zoomChanged.emit(self.zoom_percent())

    def wheelEvent(self, event) -> None:
        pixel_delta = event.pixelDelta()
        if pixel_delta is not None and (pixel_delta.x() or pixel_delta.y()):
            super().wheelEvent(event)
            return
        angle_delta = event.angleDelta()
        if angle_delta.y() == 0:
            return
        factor = 1.15 if angle_delta.y() > 0 else 1 / 1.15
        self._zoom_at(event.position(), factor)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Control:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        elif event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Control, Qt.Key.Key_Space):
            self.setDragMode(self._base_drag_mode)
        super().keyReleaseEvent(event)

    def dragEnterEvent(self, event) -> None:
        if self._editing_frame is not None and event.mimeData().hasUrls():
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dropEvent(self, event) -> None:
        if self._editing_frame is None:
            return
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                self.assetDropped.emit(Path(url.toLocalFile()))
        event.acceptProposedAction()

    def _add_object(
        self,
        obj: GraphicObject,
        parent: FrameGraphicsItem,
        *,
        editable: bool,
    ) -> None:
        container = ObjectGraphicsItem(obj, self, parent, editable=editable)
        self._object_items[id(obj)] = container
        item: QGraphicsItem | None = None
        natural_size: tuple[int, int] | None = None
        if isinstance(obj, TextObject):
            text_item = QGraphicsTextItem(obj.text, container)
            text_item.setDefaultTextColor(
                QColor.fromRgbF(obj.color.red, obj.color.green, obj.color.blue)
            )
            text_item.setFont(_font_for_object(obj))
            text_item.setTextWidth(obj.width)
            item = text_item
        elif isinstance(obj, SvgObject):
            resolved = self._resolve_asset(obj.path)
            if resolved is not None:
                svg_item = QGraphicsSvgItem(str(resolved), container)
                bounds = svg_item.boundingRect()
                if bounds.width() and bounds.height():
                    natural_size = (round(bounds.width()), round(bounds.height()))
                item = svg_item
            else:
                item = _missing_asset_item(obj, container)
        elif isinstance(obj, ImageObject):
            resolved = self._resolve_asset(obj.path)
            pixmap = QPixmap(str(resolved)) if resolved is not None else QPixmap()
            if pixmap.isNull():
                item = _missing_asset_item(obj, container)
            else:
                pixmap_item = QGraphicsPixmapItem(pixmap, container)
                pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                natural_size = (pixmap.width(), pixmap.height())
                item = pixmap_item
        elif isinstance(obj, ShapeObject):
            item = None
        else:
            return

        container.setPos(obj.x, obj.y)
        if item is not None:
            container.set_content(item, natural_size=natural_size)
            container._update_content_scale(obj.width, obj.height)
            item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._apply_object_visual_transform(container, obj)

    def _resolve_asset(self, asset_path: Path) -> Path | None:
        if asset_path.is_absolute() and asset_path.is_file():
            return asset_path
        if self._asset_root is not None:
            candidate = self._asset_root / asset_path
            if candidate.is_file():
                return candidate
        return None


class InlineTextEditor(QPlainTextEdit):
    """Floating text editor placed over a TextObject for inline editing.

    Based on ksnip's ``InlineTextEditor`` (git submodule
    ``third-party/ksnip/ksnip_py/canvas.py``):
    https://github.com/wachin/ksnip/blob/master/ksnip_py/canvas.py
    Ctrl+Enter to accept, Esc to cancel, focus-out to accept.
    """

    accepted = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, text: str, font: QFont, color: QColor, parent=None) -> None:
        super().__init__(parent)
        self._finished = False
        self.setPlainText(text)
        self.setFont(font)
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        self.document().setDefaultStyleSheet(f"color: {color.name()};")

    def keyPressEvent(self, event) -> None:
        if (
            event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self._emit_accepted()
            return
        if event.key() == Qt.Key.Key_Escape:
            self._emit_canceled()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event) -> None:
        if event.reason() == Qt.FocusReason.PopupFocusReason:
            super().focusOutEvent(event)
            return
        self._emit_accepted()
        # Do not call super() afterwards: the handler may delete this widget
        # while the event is still being processed.

    def _emit_accepted(self) -> None:
        if self._finished:
            return
        self._finished = True
        self.accepted.emit()

    def _emit_canceled(self) -> None:
        if self._finished:
            return
        self._finished = True
        self.canceled.emit()


def _font_for_object(obj: TextObject) -> QFont:
    font = _font_from_legacy_string(obj.font)
    font.setBold(obj.bold)
    font.setItalic(obj.italic)
    font.setUnderline(obj.underline)
    return font


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


def _alignment_target(items, mode: str):
    if mode == "left":
        target = min(item.x for item in items)
        return lambda item: (target, item.y)
    if mode == "right":
        target = max(item.x + item.width for item in items)
        return lambda item: (target - item.width, item.y)
    if mode == "hcenter":
        centers = [item.x + item.width / 2 for item in items]
        target = sum(centers) / len(centers)
        return lambda item: (round(target - item.width / 2), item.y)
    if mode == "top":
        target = min(item.y for item in items)
        return lambda item: (item.x, target)
    if mode == "bottom":
        target = max(item.y + item.height for item in items)
        return lambda item: (item.x, target - item.height)
    if mode == "vcenter":
        centers = [item.y + item.height / 2 for item in items]
        target = sum(centers) / len(centers)
        return lambda item: (item.x, round(target - item.height / 2))
    raise ValueError(f"unknown alignment mode {mode!r}")


def _distribution_positions(items, axis: str) -> list[tuple[int, int]]:
    if axis == "horizontal":
        ordered = sorted(items, key=lambda item: item.x + item.width / 2)
        centers = [item.x + item.width / 2 for item in ordered]
        start, end = centers[0], centers[-1]
        step = (end - start) / (len(ordered) - 1) if len(ordered) > 1 else 0
        return [
            (round(start + index * step - item.width / 2), item.y)
            for index, item in enumerate(ordered)
        ]
    if axis == "vertical":
        ordered = sorted(items, key=lambda item: item.y + item.height / 2)
        centers = [item.y + item.height / 2 for item in ordered]
        start, end = centers[0], centers[-1]
        step = (end - start) / (len(ordered) - 1) if len(ordered) > 1 else 0
        return [
            (item.x, round(start + index * step - item.height / 2))
            for index, item in enumerate(ordered)
        ]
    raise ValueError(f"unknown distribution axis {axis!r}")
