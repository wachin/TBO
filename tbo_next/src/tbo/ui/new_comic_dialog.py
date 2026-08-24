from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

MAX_CANVAS_SIZE = 1_000_000


class NewComicDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("New comic"))

        self.title_input = QLineEdit(self.tr("Untitled"))
        self.title_input.selectAll()
        self.width_input = QSpinBox()
        self.width_input.setRange(1, MAX_CANVAS_SIZE)
        self.width_input.setValue(800)
        self.width_input.setSuffix(" px")
        self.height_input = QSpinBox()
        self.height_input.setRange(1, MAX_CANVAS_SIZE)
        self.height_input.setValue(450)
        self.height_input.setSuffix(" px")

        form = QFormLayout()
        form.addRow(self.tr("Title:"), self.title_input)
        form.addRow(self.tr("Width:"), self.width_input)
        form.addRow(self.tr("Height:"), self.height_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, int, int]:
        title = self.title_input.text().strip() or self.tr("Untitled")
        return title, self.width_input.value(), self.height_input.value()
