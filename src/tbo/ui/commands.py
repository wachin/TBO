from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QUndoCommand

from tbo.document.model import Color, Comic, Frame, GraphicObject, Page, TextObject

ChangeCallback = Callable[[], None]
MoveCallback = Callable[[Frame], None]
PageChangeCallback = Callable[[int], None]
ObjectMoveCallback = Callable[[GraphicObject], None]


def _tr(text: str) -> str:
    return QCoreApplication.translate("UndoCommands", text)


def _identity_index(frames: list[Frame], target: Frame) -> int:
    for index, frame in enumerate(frames):
        if frame is target:
            return index
    raise ValueError("frame is not part of the page")


def _page_identity_index(pages: list[Page], target: Page) -> int:
    for index, page in enumerate(pages):
        if page is target:
            return index
    raise ValueError("page is not part of the comic")


def _object_identity_index(objects: list[GraphicObject], target: GraphicObject) -> int:
    for index, graphic_object in enumerate(objects):
        if graphic_object is target:
            return index
    raise ValueError("object is not part of the frame")


class MoveFrameCommand(QUndoCommand):
    def __init__(
        self,
        frame: Frame,
        old_position: tuple[int, int],
        new_position: tuple[int, int],
        on_change: MoveCallback,
    ) -> None:
        super().__init__(_tr("Move panel"))
        self._frame = frame
        self._old_position = old_position
        self._new_position = new_position
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new_position)

    def undo(self) -> None:
        self._apply(self._old_position)

    def _apply(self, position: tuple[int, int]) -> None:
        self._frame.x, self._frame.y = position
        self._on_change(self._frame)


class AddFrameCommand(QUndoCommand):
    def __init__(
        self,
        page: Page,
        frame: Frame,
        on_change: ChangeCallback,
        *,
        index: int | None = None,
        text: str | None = None,
    ) -> None:
        super().__init__(text or _tr("Add panel"))
        self._page = page
        self._frame = frame
        self._index = len(page.frames) if index is None else index
        self._on_change = on_change

    def redo(self) -> None:
        try:
            _identity_index(self._page.frames, self._frame)
        except ValueError:
            self._page.frames.insert(min(self._index, len(self._page.frames)), self._frame)
        self._on_change()

    def undo(self) -> None:
        del self._page.frames[_identity_index(self._page.frames, self._frame)]
        self._on_change()


class DeleteFrameCommand(QUndoCommand):
    def __init__(self, page: Page, frame: Frame, on_change: ChangeCallback) -> None:
        super().__init__(_tr("Delete panel"))
        self._page = page
        self._frame = frame
        self._index = _identity_index(page.frames, frame)
        self._on_change = on_change

    def redo(self) -> None:
        del self._page.frames[_identity_index(self._page.frames, self._frame)]
        self._on_change()

    def undo(self) -> None:
        self._page.frames.insert(min(self._index, len(self._page.frames)), self._frame)
        self._on_change()


class ResizeFrameCommand(QUndoCommand):
    def __init__(
        self,
        frame: Frame,
        old_size: tuple[int, int],
        new_size: tuple[int, int],
        on_change: MoveCallback,
    ) -> None:
        super().__init__(_tr("Resize panel"))
        self._frame = frame
        self._old_size = old_size
        self._new_size = new_size
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new_size)

    def undo(self) -> None:
        self._apply(self._old_size)

    def _apply(self, size: tuple[int, int]) -> None:
        self._frame.width, self._frame.height = size
        self._on_change(self._frame)


class AlignFramesCommand(QUndoCommand):
    def __init__(
        self,
        frames: list[Frame],
        old_positions: list[tuple[int, int]],
        new_positions: list[tuple[int, int]],
        on_change: ChangeCallback,
    ) -> None:
        super().__init__(_tr("Align panels"))
        self._frames = frames
        self._old_positions = old_positions
        self._new_positions = new_positions
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new_positions)

    def undo(self) -> None:
        self._apply(self._old_positions)

    def _apply(self, positions: list[tuple[int, int]]) -> None:
        for frame, (x, y) in zip(self._frames, positions, strict=False):
            frame.x, frame.y = x, y
        self._on_change()


class AddPageCommand(QUndoCommand):
    def __init__(
        self,
        comic: Comic,
        page: Page,
        index: int,
        on_change: PageChangeCallback,
    ) -> None:
        super().__init__(_tr("Add page"))
        self._comic = comic
        self._page = page
        self._index = index
        self._on_change = on_change

    def redo(self) -> None:
        try:
            _page_identity_index(self._comic.pages, self._page)
        except ValueError:
            self._comic.pages.insert(min(self._index, len(self._comic.pages)), self._page)
        self._on_change(_page_identity_index(self._comic.pages, self._page))

    def undo(self) -> None:
        del self._comic.pages[_page_identity_index(self._comic.pages, self._page)]
        self._on_change(min(max(0, self._index - 1), len(self._comic.pages) - 1))


class DeletePageCommand(QUndoCommand):
    def __init__(
        self,
        comic: Comic,
        page: Page,
        on_change: PageChangeCallback,
    ) -> None:
        if len(comic.pages) <= 1:
            raise ValueError("the last page cannot be deleted")
        super().__init__(_tr("Delete page"))
        self._comic = comic
        self._page = page
        self._index = _page_identity_index(comic.pages, page)
        self._on_change = on_change

    def redo(self) -> None:
        index = _page_identity_index(self._comic.pages, self._page)
        del self._comic.pages[index]
        self._on_change(min(index, len(self._comic.pages) - 1))

    def undo(self) -> None:
        self._comic.pages.insert(min(self._index, len(self._comic.pages)), self._page)
        self._on_change(_page_identity_index(self._comic.pages, self._page))


class MovePageCommand(QUndoCommand):
    def __init__(
        self,
        comic: Comic,
        page: Page,
        destination: int,
        on_change: PageChangeCallback,
    ) -> None:
        super().__init__(_tr("Reorder page"))
        self._comic = comic
        self._page = page
        self._origin = _page_identity_index(comic.pages, page)
        self._destination = destination
        self._on_change = on_change

    def redo(self) -> None:
        self._move_to(self._destination)

    def undo(self) -> None:
        self._move_to(self._origin)

    def _move_to(self, destination: int) -> None:
        current = _page_identity_index(self._comic.pages, self._page)
        page = self._comic.pages.pop(current)
        bounded_destination = max(0, min(destination, len(self._comic.pages)))
        self._comic.pages.insert(bounded_destination, page)
        self._on_change(bounded_destination)


class MoveObjectCommand(QUndoCommand):
    def __init__(
        self,
        graphic_object: GraphicObject,
        old_position: tuple[int, int],
        new_position: tuple[int, int],
        on_change: ObjectMoveCallback,
    ) -> None:
        super().__init__(_tr("Move object"))
        self._object = graphic_object
        self._old_position = old_position
        self._new_position = new_position
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new_position)

    def undo(self) -> None:
        self._apply(self._old_position)

    def _apply(self, position: tuple[int, int]) -> None:
        self._object.x, self._object.y = position
        self._on_change(self._object)


class AddObjectCommand(QUndoCommand):
    def __init__(
        self,
        frame: Frame,
        graphic_object: GraphicObject,
        on_change: ChangeCallback,
        *,
        index: int | None = None,
        text: str | None = None,
    ) -> None:
        super().__init__(text or _tr("Add object"))
        self._frame = frame
        self._object = graphic_object
        self._index = len(frame.objects) if index is None else index
        self._on_change = on_change

    def redo(self) -> None:
        try:
            _object_identity_index(self._frame.objects, self._object)
        except ValueError:
            self._frame.objects.insert(min(self._index, len(self._frame.objects)), self._object)
        self._on_change()

    def undo(self) -> None:
        del self._frame.objects[_object_identity_index(self._frame.objects, self._object)]
        self._on_change()


class DeleteObjectCommand(QUndoCommand):
    def __init__(
        self,
        frame: Frame,
        graphic_object: GraphicObject,
        on_change: ChangeCallback,
    ) -> None:
        super().__init__(_tr("Delete object"))
        self._frame = frame
        self._object = graphic_object
        self._index = _object_identity_index(frame.objects, graphic_object)
        self._on_change = on_change

    def redo(self) -> None:
        del self._frame.objects[_object_identity_index(self._frame.objects, self._object)]
        self._on_change()

    def undo(self) -> None:
        self._frame.objects.insert(min(self._index, len(self._frame.objects)), self._object)
        self._on_change()


class RotateObjectCommand(QUndoCommand):
    def __init__(
        self,
        graphic_object: GraphicObject,
        old_angle: float,
        new_angle: float,
        on_change: ObjectMoveCallback,
    ) -> None:
        super().__init__(_tr("Rotate object"))
        self._object = graphic_object
        self._old_angle = old_angle
        self._new_angle = new_angle
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new_angle)

    def undo(self) -> None:
        self._apply(self._old_angle)

    def _apply(self, angle: float) -> None:
        self._object.angle = angle
        self._on_change(self._object)


class FlipObjectCommand(QUndoCommand):
    def __init__(
        self,
        graphic_object: GraphicObject,
        axis: str,
        on_change: ObjectMoveCallback,
    ) -> None:
        if axis not in {"horizontal", "vertical"}:
            raise ValueError("axis must be 'horizontal' or 'vertical'")
        super().__init__(_tr("Flip object"))
        self._object = graphic_object
        self._axis = axis
        self._on_change = on_change

    def redo(self) -> None:
        self._toggle()

    def undo(self) -> None:
        self._toggle()

    def _toggle(self) -> None:
        if self._axis == "horizontal":
            self._object.flip_horizontal = not self._object.flip_horizontal
        else:
            self._object.flip_vertical = not self._object.flip_vertical
        self._on_change(self._object)


class ResizeObjectCommand(QUndoCommand):
    def __init__(
        self,
        graphic_object: GraphicObject,
        old_size: tuple[int, int],
        new_size: tuple[int, int],
        on_change: ObjectMoveCallback,
    ) -> None:
        super().__init__(_tr("Resize object"))
        self._object = graphic_object
        self._old_size = old_size
        self._new_size = new_size
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new_size)

    def undo(self) -> None:
        self._apply(self._old_size)

    def _apply(self, size: tuple[int, int]) -> None:
        self._object.width, self._object.height = size
        self._on_change(self._object)


class EditTextObjectCommand(QUndoCommand):
    def __init__(
        self,
        text_object: TextObject,
        old_text: str,
        new_text: str,
        old_font: str,
        new_font: str,
        old_color: Color,
        new_color: Color,
        old_style: tuple[bool, bool, bool],
        new_style: tuple[bool, bool, bool],
        on_change: ObjectMoveCallback,
    ) -> None:
        super().__init__(_tr("Edit text"))
        self._object = text_object
        self._old = (old_text, old_font, old_color, old_style)
        self._new = (new_text, new_font, new_color, new_style)
        self._on_change = on_change

    def redo(self) -> None:
        self._apply(self._new)

    def undo(self) -> None:
        self._apply(self._old)

    def _apply(self, state) -> None:
        text, font, color, style = state
        self._object.text = text
        self._object.font = font
        self._object.color = color
        self._object.bold, self._object.italic, self._object.underline = style
        self._on_change(self._object)
