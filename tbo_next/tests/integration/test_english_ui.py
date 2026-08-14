from tbo.ui.main_window import MainWindow
from tbo.ui.new_comic_dialog import NewComicDialog


def test_primary_interface_language_is_english(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    dialog = NewComicDialog(window)
    qtbot.addWidget(dialog)

    menu_titles = [action.text() for action in window.menuBar().actions()]
    assert menu_titles == ["&File", "&Edit", "&Page", "&View"]
    assert window.save_action.text() == "&Save"
    assert window.add_frame_action.text() == "Add &Panel"
    assert dialog.windowTitle() == "New comic"
    assert dialog.values()[0] == "Untitled"
