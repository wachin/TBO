from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from tbo.formats.tbo_v1 import TboFormatError, load, save
from tbo.ui.canvas import ComicCanvas


class MainWindow(QMainWindow):
    def __init__(self, *, asset_root: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("TBO 2")
        self.resize(1000, 700)
        self._filename: Path | None = None
        self.canvas = ComicCanvas(asset_root=asset_root)
        self.setCentralWidget(self.canvas)
        self._create_actions()

    def _create_actions(self) -> None:
        file_menu = self.menuBar().addMenu("&Archivo")
        open_action = QAction("&Abrir…", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_dialog)
        file_menu.addAction(open_action)

        self.save_action = QAction("&Guardar", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self.save_document)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction("Guardar &como…", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self.save_as_dialog)
        file_menu.addAction(self.save_as_action)

        navigate_menu = self.menuBar().addMenu("&Página")
        self.previous_page_action = QAction("Página &anterior", self)
        self.previous_page_action.setShortcut("PageUp")
        self.previous_page_action.triggered.connect(self.previous_page)
        navigate_menu.addAction(self.previous_page_action)

        self.next_page_action = QAction("Página &siguiente", self)
        self.next_page_action.setShortcut("PageDown")
        self.next_page_action.triggered.connect(self.next_page)
        navigate_menu.addAction(self.next_page_action)

        view_menu = self.menuBar().addMenu("&Ver")
        fit_action = QAction("Ajustar página", self)
        fit_action.setShortcut("2")
        fit_action.triggered.connect(self.canvas.fit_page)
        view_menu.addAction(fit_action)

    def open_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Abrir cómic", "", "Archivos TBO (*.tbo);;Todos los archivos (*)"
        )
        if filename:
            self.open_document(Path(filename))

    def open_document(self, filename: Path) -> bool:
        try:
            comic = load(filename)
        except TboFormatError as error:
            QMessageBox.critical(self, "No se pudo abrir el archivo", str(error))
            return False

        self.canvas.set_comic(comic)
        self._filename = filename
        self.setWindowTitle(f"{comic.title} — TBO 2")
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)
        self._update_page_actions()
        self.canvas.fit_page()
        return True

    def save_document(self) -> bool:
        if self._filename is None:
            return self.save_as_dialog()
        return self._save_to(self._filename)

    def save_as_dialog(self) -> bool:
        if self.canvas.comic is None:
            return False
        suggested = str(self._filename or Path(f"{self.canvas.comic.title}.tbo"))
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar cómic", suggested, "Archivos TBO (*.tbo)"
        )
        if not filename:
            return False
        target = Path(filename)
        if target.suffix.lower() != ".tbo":
            target = target.with_suffix(".tbo")
        return self._save_to(target)

    def _save_to(self, filename: Path) -> bool:
        comic = self.canvas.comic
        if comic is None:
            return False
        try:
            save(comic, filename)
        except TboFormatError as error:
            QMessageBox.critical(self, "No se pudo guardar el archivo", str(error))
            return False
        self._filename = filename
        comic.title = filename.stem
        self.setWindowTitle(f"{comic.title} — TBO 2")
        self.statusBar().showMessage(f"Guardado en {filename}", 5000)
        return True

    def previous_page(self) -> None:
        if self.canvas.previous_page():
            self.canvas.fit_page()
        self._update_page_actions()

    def next_page(self) -> None:
        if self.canvas.next_page():
            self.canvas.fit_page()
        self._update_page_actions()

    def _update_page_actions(self) -> None:
        index = self.canvas.page_index
        count = self.canvas.page_count
        self.previous_page_action.setEnabled(count > 0 and index > 0)
        self.next_page_action.setEnabled(count > 0 and index + 1 < count)
        message = f"Página {index + 1} de {count}" if count else "Documento sin páginas"
        self.statusBar().showMessage(message)
