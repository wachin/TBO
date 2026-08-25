from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFontComboBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TextObjectDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Add Text"))
        self.resize(460, 320)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(self.tr("Ctrl+Enter to accept. Shift+Enter for a new line."))
        self.font_input = QFontComboBox()
        self.size_input = QSpinBox()
        self.size_input.setRange(1, 512)
        self.size_input.setValue(8)
        self.size_input.setSuffix(" pt")
        self._color = QColor("black")
        self.color_button = QPushButton()
        self.color_button.clicked.connect(self.choose_color)
        self._update_color_button()

        font_row = QHBoxLayout()
        font_row.addWidget(self.font_input, 1)
        font_row.addWidget(self.size_input)

        form = QFormLayout()
        form.addRow(self.tr("Font:"), font_row)
        form.addRow(self.tr("Color:"), self.color_button)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.text_input.textChanged.connect(self._update_accept_state)
        self._update_accept_state()

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_input, 1)
        layout.addLayout(form)
        layout.addWidget(self.buttons)

    def keyPressEvent(self, event) -> None:
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter} and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
            if button.isEnabled():
                self.accept()
            return
        super().keyPressEvent(event)

    def choose_color(self) -> None:
        color = QColorDialog.getColor(self._color, self, self.tr("Choose Text Color"))
        if color.isValid():
            self.set_color(color)

    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self._update_color_button()

    def values(self) -> tuple[str, str, QColor]:
        text = self.text_input.toPlainText().strip()
        font = f"{self.font_input.currentFont().family()} {self.size_input.value()}"
        return text, font, QColor(self._color)

    def _update_accept_state(self) -> None:
        button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        button.setEnabled(bool(self.text_input.toPlainText().strip()))

    def _update_color_button(self) -> None:
        self.color_button.setText(self._color.name().upper())
        foreground = "white" if self._color.lightnessF() < 0.5 else "black"
        self.color_button.setStyleSheet(
            f"background-color: {self._color.name()}; color: {foreground};"
        )
