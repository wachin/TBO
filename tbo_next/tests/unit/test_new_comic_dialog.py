from tbo.ui.new_comic_dialog import MAX_CANVAS_SIZE, NewComicDialog


def test_new_comic_dialog_has_sensible_defaults(qtbot) -> None:
    dialog = NewComicDialog()
    qtbot.addWidget(dialog)

    assert dialog.values() == ("Untitled", 800, 450)
    assert dialog.width_input.maximum() == MAX_CANVAS_SIZE
    assert dialog.height_input.maximum() == MAX_CANVAS_SIZE


def test_new_comic_dialog_normalizes_empty_title(qtbot) -> None:
    dialog = NewComicDialog()
    qtbot.addWidget(dialog)
    dialog.title_input.setText("   ")
    dialog.width_input.setValue(1200)
    dialog.height_input.setValue(900)

    assert dialog.values() == ("Untitled", 1200, 900)
