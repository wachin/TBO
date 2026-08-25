from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

FORMAT_FILTERS = {
    "png": "PNG Images (*.png)",
    "pdf": "PDF Document (*.pdf)",
    "svg": "SVG Image (*.svg)",
}


class ExportDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        page_count: int,
        current_page: int,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Export Options"))

        self.format_input = QComboBox()
        for fmt, label in FORMAT_FILTERS.items():
            self.format_input.addItem(label, fmt)
        self.format_input.setCurrentIndex(0)

        self.range_input = QComboBox()
        self.range_input.addItem(self.tr("All pages ({count})").format(count=page_count))
        self.range_input.addItem(
            self.tr("Current page ({index} of {count})").format(
                index=current_page + 1, count=page_count
            )
        )

        self.scale_input = QSpinBox()
        self.scale_input.setRange(10, 1000)
        self.scale_input.setValue(100)
        self.scale_input.setSuffix(" %")
        self.scale_input.setToolTip(self.tr("Output resolution for PNG export"))
        self.format_input.currentIndexChanged.connect(self._on_format_changed)

        form = QFormLayout()
        form.addRow(self.tr("Format:"), self.format_input)
        form.addRow(self.tr("Range:"), self.range_input)
        form.addRow(self.tr("Scale:"), self.scale_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._on_format_changed(0)

    def _on_format_changed(self, _index: int) -> None:
        fmt = self.format_input.currentData()
        self.scale_input.setEnabled(fmt == "png")

    def values(self) -> tuple[str, bool, int]:
        fmt_key = self.format_input.currentData()
        current_only = self.range_input.currentIndex() == 1
        return fmt_key, current_only, self.scale_input.value()
