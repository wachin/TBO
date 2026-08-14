from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from tbo.formats.tbo_v1 import TboFormatError, load
from tbo.ui.canvas import ComicCanvas


class MainWindow(QMainWindow):
    def __init__(self, *, asset_root: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("TBO 2")
        self.resize(1000, 700)
        self.canvas = ComicCanvas(asset_root=asset_root)
        self.setCentralWidget(self.canvas)
        self._create_actions()

    def _create_actions(self) -> None:
        file_menu = self.menuBar().addMenu("&Archivo")
        open_action = QAction("&Abrir…", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_dialog)
        file_menu.addAction(open_action)

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
        self.setWindowTitle(f"{comic.title} — TBO 2")
        self.canvas.fit_page()
        return True

