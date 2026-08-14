from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtGui import QUndoCommand

from tbo.document.model import Frame, Page

ChangeCallback = Callable[[], None]
MoveCallback = Callable[[Frame], None]


def _identity_index(frames: list[Frame], target: Frame) -> int:
    for index, frame in enumerate(frames):
        if frame is target:
            return index
    raise ValueError("frame is not part of the page")


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
