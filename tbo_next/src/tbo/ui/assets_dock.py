from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QMimeData, QRectF, QSize, QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QDrag, QIcon, QImage, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QToolBox,
    QVBoxLayout,
    QWidget,
)

from tbo.assets import AssetCatalog, AssetEntry

ICON_SIZE = 64


class _DraggableListWidget(QListWidget):
    def mimeData(self, items):
        data = QMimeData()
        urls = []
        texts = []
        for item in items:
            raw = item.data(Qt.ItemDataRole.UserRole)
            if raw:
                urls.append(QUrl.fromLocalFile(raw))
                texts.append(raw)
        if urls:
            data.setUrls(urls)
        if texts:
            data.setText("\n".join(texts))
        return data


class _LibraryTab(QWidget):
    assetActivated = pyqtSignal(Path)

    def __init__(self, categories, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._categories = list(categories)
        self._icon_cache: dict[Path, QIcon] = {}

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.tr("Search…"))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._apply_filter)

        self.toolbox = QToolBox()
        self._pages: list[QListWidget] = []
        for category in self._categories:
            list_widget = _DraggableListWidget()
            list_widget.setViewMode(QListWidget.ViewMode.IconMode)
            list_widget.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
            list_widget.setMovement(QListWidget.Movement.Static)
            list_widget.setWordWrap(True)
            list_widget.setDragEnabled(True)
            list_widget.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
            list_widget.itemClicked.connect(self._on_item_clicked)
            self.toolbox.addItem(list_widget, category.name)
            self._pages.append(list_widget)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.search_input)
        layout.addWidget(self.toolbox)
        self._apply_filter("")

    def _apply_filter(self, query: str) -> None:
        normalized = query.strip().lower()
        for list_widget, category in zip(self._pages, self._categories):
            list_widget.clear()
            visible = (
                True
                if not normalized
                else any(normalized in entry.name.lower() for entry in category.entries)
            )
            self.toolbox.setItemEnabled(self.toolbox.indexOf(list_widget), visible)
            for entry in category.entries:
                if normalized and normalized not in entry.name.lower():
                    continue
                item = QListWidgetItem()
                item.setIcon(self._icon(entry))
                item.setText(entry.name.replace("-", " "))
                item.setToolTip(str(entry.path))
                item.setData(Qt.ItemDataRole.UserRole, str(entry.path))
                item.setSizeHint(QSize(96, 96))
                list_widget.addItem(item)

    def _icon(self, entry: AssetEntry) -> QIcon:
        cached = self._icon_cache.get(entry.path)
        if cached is not None:
            return cached
        icon = QIcon(_render_svg_preview(entry.path, ICON_SIZE))
        self._icon_cache[entry.path] = icon
        return icon

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        raw = item.data(Qt.ItemDataRole.UserRole)
        if raw:
            self.assetActivated.emit(Path(raw))


def _render_svg_preview(path: Path, size: int) -> QPixmap:
    renderer = QSvgRenderer(str(path))
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    if renderer.isValid():
        natural = renderer.defaultSize()
        width = natural.width()
        height = natural.height()
        if width > 0 and height > 0:
            scale = min(size / width, size / height)
            target = QRectF(0, 0, width * scale, height * scale)
            renderer.render(painter, target)
    painter.end()
    return QPixmap.fromImage(image)


class AssetsDock(QDockWidget):
    assetActivated = pyqtSignal(Path)

    def __init__(
        self,
        catalog: AssetCatalog,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Asset Library"))
        self.setObjectName("assets_dock")
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)

        character_categories, accessories_categories, doodle_categories = (
            self._split_categories(catalog)
        )

        self.tabs = QTabWidget()
        self._doodles_tab = _LibraryTab(doodle_categories)
        self._character_tab = _LibraryTab(character_categories)
        self._accessories_tab = _LibraryTab(accessories_categories)
        self._bubbles_tab = _LibraryTab(catalog.bubble_categories)
        for tab in (
            self._doodles_tab,
            self._character_tab,
            self._accessories_tab,
            self._bubbles_tab,
        ):
            tab.assetActivated.connect(self.assetActivated)
        self.tabs.addTab(self._doodles_tab, self.tr("Doodles"))
        self.tabs.addTab(self._character_tab, self.tr("Character"))
        self.tabs.addTab(self._accessories_tab, self.tr("Accessories"))
        self.tabs.addTab(self._bubbles_tab, self.tr("Bubbles"))
        self.setWidget(self.tabs)

    def _split_categories(
        self, catalog: AssetCatalog
    ) -> tuple[list, list, list]:
        head_root = catalog.root / "head"
        accessories_root = catalog.root / "accesories"
        character: list = []
        accessories: list = []
        regular: list = []
        for category in catalog.doodle_categories:
            if any(head_root in entry.path.parents for entry in category.entries):
                character.append(category)
            elif any(
                accessories_root in entry.path.parents for entry in category.entries
            ):
                accessories.append(category)
            else:
                regular.append(category)
        return character, accessories, regular
