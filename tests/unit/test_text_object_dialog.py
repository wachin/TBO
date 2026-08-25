from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDialogButtonBox

from tbo.ui.text_object_dialog import TextObjectDialog


def test_text_dialog_requires_non_empty_text(qtbot) -> None:
    dialog = TextObjectDialog()
    qtbot.addWidget(dialog)
    ok_button = dialog.buttons.button(QDialogButtonBox.StandardButton.Ok)

    assert not ok_button.isEnabled()
    dialog.text_input.setPlainText("Hello world")
    assert ok_button.isEnabled()


def test_text_dialog_returns_font_size_and_color(qtbot) -> None:
    dialog = TextObjectDialog()
    qtbot.addWidget(dialog)
    dialog.text_input.setPlainText("A caption")
    dialog.size_input.setValue(18)
    dialog.set_color(QColor("#336699"))

    text, font, color = dialog.values()

    assert text == "A caption"
    assert font.endswith(" 18")
    assert color.name() == "#336699"
