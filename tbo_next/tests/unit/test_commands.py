import pytest

from tbo.document.model import Comic, Frame, Page
from tbo.ui.commands import (
    AddFrameCommand,
    AddPageCommand,
    DeleteFrameCommand,
    DeletePageCommand,
    MoveFrameCommand,
    MovePageCommand,
    ResizeFrameCommand,
)


def test_move_frame_command_round_trip() -> None:
    frame = Frame(10, 20, 100, 80)
    changed: list[Frame] = []
    command = MoveFrameCommand(frame, (10, 20), (30, 40), changed.append)

    command.redo()
    assert (frame.x, frame.y) == (30, 40)
    command.undo()
    assert (frame.x, frame.y) == (10, 20)
    assert changed == [frame, frame]


def test_add_frame_command_preserves_index_across_undo() -> None:
    first = Frame(0, 0, 10, 10)
    added = Frame(10, 10, 20, 20)
    page = Page([first])
    command = AddFrameCommand(page, added, lambda: None)

    command.redo()
    assert page.frames == [first, added]
    command.undo()
    assert page.frames == [first]
    command.redo()
    assert page.frames == [first, added]


def test_delete_frame_command_restores_original_index() -> None:
    first = Frame(0, 0, 10, 10)
    deleted = Frame(10, 10, 20, 20)
    last = Frame(20, 20, 30, 30)
    page = Page([first, deleted, last])
    command = DeleteFrameCommand(page, deleted, lambda: None)

    command.redo()
    assert page.frames == [first, last]
    command.undo()
    assert page.frames == [first, deleted, last]


def test_resize_frame_command_round_trip() -> None:
    frame = Frame(10, 20, 100, 80)
    changed: list[Frame] = []
    command = ResizeFrameCommand(frame, (100, 80), (150, 120), changed.append)

    command.redo()
    assert (frame.width, frame.height) == (150, 120)
    command.undo()
    assert (frame.width, frame.height) == (100, 80)
    assert changed == [frame, frame]


def test_add_page_command_round_trip() -> None:
    first = Page()
    added = Page()
    comic = Comic("test", 800, 450, [first])
    indexes: list[int] = []
    command = AddPageCommand(comic, added, 1, indexes.append)

    command.redo()
    assert comic.pages[0] is first
    assert comic.pages[1] is added
    command.undo()
    assert len(comic.pages) == 1
    assert comic.pages[0] is first
    command.redo()
    assert comic.pages[0] is first
    assert comic.pages[1] is added
    assert indexes == [1, 0, 1]


def test_delete_page_command_preserves_page_and_index() -> None:
    first, deleted, last = Page(), Page(), Page()
    comic = Comic("test", 800, 450, [first, deleted, last])
    command = DeletePageCommand(comic, deleted, lambda index: None)

    command.redo()
    assert comic.pages[0] is first
    assert comic.pages[1] is last
    command.undo()
    assert comic.pages[0] is first
    assert comic.pages[1] is deleted
    assert comic.pages[2] is last


def test_cannot_delete_only_page() -> None:
    page = Page()
    comic = Comic("test", 800, 450, [page])

    with pytest.raises(ValueError, match="last page"):
        DeletePageCommand(comic, page, lambda index: None)


def test_move_page_command_round_trip() -> None:
    first, moved, last = Page(), Page(), Page()
    comic = Comic("test", 800, 450, [first, moved, last])
    indexes: list[int] = []
    command = MovePageCommand(comic, moved, 2, indexes.append)

    command.redo()
    assert comic.pages[0] is first
    assert comic.pages[1] is last
    assert comic.pages[2] is moved
    command.undo()
    assert comic.pages[0] is first
    assert comic.pages[1] is moved
    assert comic.pages[2] is last
    assert indexes == [2, 1]
