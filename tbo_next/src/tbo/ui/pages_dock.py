from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QImage, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from tbo.document.model import Comic
from tbo.rendering.renderer import ComicRenderer

THUMBNAIL_WIDTH = 160


class PagesDock(QDockWidget):
    pageSelected = pyqtSignal(int)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        asset_root: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Pages"))
        self.setObjectName("pages_dock")
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)

        self._renderer = ComicRenderer(asset_root=asset_root)
        self._comic: Comic | None = None

        self._list = QListWidget()
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(QSize(THUMBNAIL_WIDTH, int(THUMBNAIL_WIDTH * 0.625)))
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setWordWrap(True)
        self._list.itemClicked.connect(self._on_clicked)
        self.setWidget(self._list)

    def set_comic(self, comic: Comic | None) -> None:
        self._comic = comic
        self._render_all()

    def set_current_page(self, index: int) -> None:
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item is not None:
                item.setSelected(i == index)

    def _render_all(self) -> None:
        self._list.clear()
        if self._comic is None:
            return
        for index in range(len(self._comic.pages)):
            self._render_thumbnail(index)

    def _render_thumbnail(self, index: int) -> None:
        page = self._comic.pages[index]
        width = THUMBNAIL_WIDTH
        height = max(1, int(width * self._comic.height / self._comic.width))
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        painter.scale(width / self._comic.width, height / self._comic.height)
        self._renderer.paint_page(painter, page, self._comic)
        painter.end()
        pixmap = QPixmap.fromImage(image)
        item = QListWidgetItem(QIcon(pixmap), str(index + 1))
        item.setData(Qt.ItemDataRole.UserRole, index)
        item.setSizeHint(QSize(THUMBNAIL_WIDTH + 20, height + 30))
        self._list.addItem(item)

    def _on_clicked(self, item: QListWidgetItem) -> None:
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is not None:
            self.pageSelected.emit(index)