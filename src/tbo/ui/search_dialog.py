from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from tbo.document.model import Comic, Frame, GraphicObject, TextObject


class SearchDialog(QDialog):
    goTo = pyqtSignal(int, Frame, GraphicObject)

    def __init__(self, comic: Comic, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Find Text"))
        self.resize(420, 360)
        self._comic = comic
        self._results: list[tuple[int, Frame, GraphicObject]] = []

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText(self.tr("Search text in the document…"))
        self.query_input.setClearButtonEnabled(True)
        self.query_input.textChanged.connect(self._search)

        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self._activate)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.addButton(self.tr("Go to"), QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.accepted.connect(self._activate_current)

        layout = QVBoxLayout(self)
        layout.addWidget(self.query_input)
        layout.addWidget(self.results_list, 1)
        layout.addWidget(buttons)
        self.query_input.setFocus()

    def _search(self, query: str) -> None:
        normalized = query.strip().lower()
        self._results.clear()
        self.results_list.clear()
        if not normalized:
            return
        for page_index, page in enumerate(self._comic.pages):
            for frame in page.frames:
                for graphic_object in frame.objects:
                    if (
                        isinstance(graphic_object, TextObject)
                        and normalized in graphic_object.text.lower()
                    ):
                        self._results.append((page_index, frame, graphic_object))
                        preview = graphic_object.text.strip().replace("\n", " ")
                        if len(preview) > 40:
                            preview = preview[:40] + "…"
                        self.results_list.addItem(
                            self.tr("Page {page}: {preview}").format(
                                page=page_index + 1, preview=preview
                            )
                        )

    def _activate_current(self) -> None:
        item = self.results_list.currentItem()
        if item is not None:
            self._activate(item)

    def _activate(self, item: QListWidgetItem) -> None:
        row = self.results_list.row(item)
        if 0 <= row < len(self._results):
            page_index, frame, graphic_object = self._results[row]
            self.goTo.emit(page_index, frame, graphic_object)
            self.accept()
