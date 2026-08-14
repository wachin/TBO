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
        self.canvas.undo_stack.cleanChanged.connect(self._on_clean_changed)
        self.canvas.scene.selectionChanged.connect(self._update_edit_actions)
        self._update_edit_actions()

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

        edit_menu = self.menuBar().addMenu("&Editar")
        self.undo_action = self.canvas.undo_stack.createUndoAction(self, "&Deshacer")
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(self.undo_action)
        self.redo_action = self.canvas.undo_stack.createRedoAction(self, "&Rehacer")
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()
        self.add_frame_action = QAction("Añadir &viñeta", self)
        self.add_frame_action.setShortcut("F")
        self.add_frame_action.triggered.connect(self.add_frame)
        edit_menu.addAction(self.add_frame_action)
        self.delete_frame_action = QAction("&Eliminar viñeta", self)
        self.delete_frame_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_frame_action.triggered.connect(self.delete_frame)
        edit_menu.addAction(self.delete_frame_action)

        self.clone_frame_action = QAction("&Clonar viñeta", self)
        self.clone_frame_action.setShortcut("Ctrl+D")
        self.clone_frame_action.triggered.connect(self.clone_frame)
        edit_menu.addAction(self.clone_frame_action)

        for shortcut, dx, dy in (
            ("Left", -5, 0),
            ("Right", 5, 0),
            ("Up", 0, -5),
            ("Down", 0, 5),
        ):
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(
                lambda checked=False, x=dx, y=dy: self.nudge_selected_frame(x, y)
            )
            self.addAction(action)

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

        zoom_in_action = QAction("Acercar", self)
        zoom_in_action.setShortcut("+")
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Alejar", self)
        zoom_out_action.setShortcut("-")
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction("Tamaño real", self)
        reset_zoom_action.setShortcut("1")
        reset_zoom_action.triggered.connect(self.canvas.reset_zoom)
        view_menu.addAction(reset_zoom_action)

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
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)
        self._update_page_actions()
        self._update_edit_actions()
        self._update_window_title()
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
        self.canvas.undo_stack.setClean()
        self._update_window_title()
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

    def add_frame(self) -> None:
        frame = self.canvas.add_frame()
        if frame is not None:
            self._update_edit_actions()

    def delete_frame(self) -> None:
        if self.canvas.delete_selected_frame():
            self._update_edit_actions()

    def clone_frame(self) -> None:
        if self.canvas.clone_selected_frame() is not None:
            self._update_edit_actions()

    def nudge_selected_frame(self, dx: int, dy: int) -> None:
        self.canvas.nudge_selected_frame(dx, dy)

    def _on_clean_changed(self, clean: bool) -> None:
        self._update_window_title()

    def _update_window_title(self) -> None:
        comic = self.canvas.comic
        if comic is None:
            self.setWindowTitle("TBO 2")
            return
        modified = " *" if not self.canvas.undo_stack.isClean() else ""
        self.setWindowTitle(f"{comic.title}{modified} — TBO 2")

    def _update_edit_actions(self) -> None:
        has_page = self.canvas.current_page is not None
        self.add_frame_action.setEnabled(has_page)
        self.delete_frame_action.setEnabled(self.canvas.selected_frame() is not None)
        self.clone_frame_action.setEnabled(self.canvas.selected_frame() is not None)

    def _update_page_actions(self) -> None:
        index = self.canvas.page_index
        count = self.canvas.page_count
        self.previous_page_action.setEnabled(count > 0 and index > 0)
        self.next_page_action.setEnabled(count > 0 and index + 1 < count)
        message = f"Página {index + 1} de {count}" if count else "Documento sin páginas"
        self.statusBar().showMessage(message)
