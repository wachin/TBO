from tbo.document.model import Frame, Page
from tbo.ui.commands import AddFrameCommand, DeleteFrameCommand, MoveFrameCommand


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
