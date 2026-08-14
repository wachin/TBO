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
        self.setWindowTitle("Nuevo cómic")

        self.title_input = QLineEdit("Sin título")
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
        form.addRow("Título:", self.title_input)
        form.addRow("Anchura:", self.width_input)
        form.addRow("Altura:", self.height_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def values(self) -> tuple[str, int, int]:
        title = self.title_input.text().strip() or "Sin título"
        return title, self.width_input.value(), self.height_input.value()
