from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QKeyEvent, QPainter, QPixmap
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget

from tbo.document.model import Comic
from tbo.rendering.renderer import ComicRenderer


class PresentationDialog(QDialog):
    """Full-screen reader that steps through the pages of a comic."""

    def __init__(
        self,
        comic: Comic,
        start_page: int = 0,
        parent: QWidget | None = None,
        *,
        asset_root: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self._comic = comic
        self._page_index = max(0, min(start_page, len(comic.pages) - 1))
        self._renderer = ComicRenderer(asset_root=asset_root)
        self.setWindowTitle(self.tr("Presentation"))
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)

        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self._update_page()

    def showEvent(self, event) -> None:
        self.showFullScreen()
        super().showEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_page()

    def _update_page(self) -> None:
        if not self._comic.pages:
            return
        page = self._comic.pages[self._page_index]
        image = QImage(self._comic.width, self._comic.height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        self._renderer.paint_page(painter, page, self._comic)
        painter.end()
        pixmap = QPixmap.fromImage(image)
        available = self._label.size()
        if available.isValid() and not available.isEmpty():
            pixmap = pixmap.scaled(
                available,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self._label.setPixmap(pixmap)
        self.setWindowTitle(
            self.tr("Presentation — Page {current} of {count}").format(
                current=self._page_index + 1, count=len(self._comic.pages)
            )
        )

    def _next_page(self) -> None:
        if self._page_index + 1 < len(self._comic.pages):
            self._page_index += 1
            self._update_page()

    def _previous_page(self) -> None:
        if self._page_index > 0:
            self._page_index -= 1
            self._update_page()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.accept()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_Down, Qt.Key.Key_Space, Qt.Key.Key_PageDown):
            self._next_page()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Up, Qt.Key.Key_Backspace, Qt.Key.Key_PageUp):
            self._previous_page()
        else:
            super().keyPressEvent(event)
