from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtGui import QUndoCommand

from tbo.document.model import Comic, Frame, Page

ChangeCallback = Callable[[], None]
MoveCallback = Callable[[Frame], None]
PageChangeCallback = Callable[[int], None]


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


class MoveFrameCommand(QUndoCommand):
    def __init__(
        self,
        frame: Frame,
        old_position: tuple[int, int],
        new_position: tuple[int, int],
        on_change: MoveCallback,
    ) -> None:
        super().__init__("Mover viñeta")
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
        text: str = "Añadir viñeta",
    ) -> None:
        super().__init__(text)
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
        super().__init__("Eliminar viñeta")
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
        super().__init__("Redimensionar viñeta")
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


class AddPageCommand(QUndoCommand):
    def __init__(
        self,
        comic: Comic,
        page: Page,
        index: int,
        on_change: PageChangeCallback,
    ) -> None:
        super().__init__("Añadir página")
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
        super().__init__("Eliminar página")
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
        super().__init__("Reordenar página")
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
