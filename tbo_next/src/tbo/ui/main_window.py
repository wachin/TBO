from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox

from tbo.document.model import Comic, Page
from tbo.formats.tbo_v1 import TboFormatError, load, save
from tbo.ui.canvas import ComicCanvas
from tbo.ui.new_comic_dialog import NewComicDialog


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
        self.canvas.pageChanged.connect(self._update_page_actions)
        self.canvas.modeChanged.connect(self._on_mode_changed)
        self.canvas.scene.selectionChanged.connect(self._update_edit_actions)
        self._update_edit_actions()

    def _create_actions(self) -> None:
        file_menu = self.menuBar().addMenu(self.tr("&File"))
        new_action = QAction(self.tr("&New…"), self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_document_dialog)
        file_menu.addAction(new_action)

        open_action = QAction(self.tr("&Open…"), self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_dialog)
        file_menu.addAction(open_action)

        self.save_action = QAction(self.tr("&Save"), self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self.save_document)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction(self.tr("Save &As…"), self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self.save_as_dialog)
        file_menu.addAction(self.save_as_action)

        edit_menu = self.menuBar().addMenu(self.tr("&Edit"))
        self.undo_action = self.canvas.undo_stack.createUndoAction(self, self.tr("&Undo"))
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(self.undo_action)
        self.redo_action = self.canvas.undo_stack.createRedoAction(self, self.tr("&Redo"))
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()
        self.add_frame_action = QAction(self.tr("Add &Panel"), self)
        self.add_frame_action.setShortcut("F")
        self.add_frame_action.triggered.connect(self.add_frame)
        edit_menu.addAction(self.add_frame_action)
        self.delete_frame_action = QAction(self.tr("&Delete Panel"), self)
        self.delete_frame_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_frame_action.triggered.connect(self.delete_frame)
        edit_menu.addAction(self.delete_frame_action)

        self.clone_frame_action = QAction(self.tr("&Clone Panel"), self)
        self.clone_frame_action.setShortcut("Ctrl+D")
        self.clone_frame_action.triggered.connect(self.clone_frame)
        edit_menu.addAction(self.clone_frame_action)

        self.leave_frame_action = QAction(self.tr("Leave Panel"), self)
        self.leave_frame_action.setShortcut("Escape")
        self.leave_frame_action.triggered.connect(self.leave_frame)
        edit_menu.addAction(self.leave_frame_action)

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

        navigate_menu = self.menuBar().addMenu(self.tr("&Page"))
        self.previous_page_action = QAction(self.tr("&Previous Page"), self)
        self.previous_page_action.setShortcut("PageUp")
        self.previous_page_action.triggered.connect(self.previous_page)
        navigate_menu.addAction(self.previous_page_action)

        self.next_page_action = QAction(self.tr("&Next Page"), self)
        self.next_page_action.setShortcut("PageDown")
        self.next_page_action.triggered.connect(self.next_page)
        navigate_menu.addAction(self.next_page_action)

        navigate_menu.addSeparator()
        self.add_page_action = QAction(self.tr("Add Page"), self)
        self.add_page_action.setShortcut("Ctrl+Shift+N")
        self.add_page_action.triggered.connect(self.add_page)
        navigate_menu.addAction(self.add_page_action)

        self.delete_page_action = QAction(self.tr("Delete Page"), self)
        self.delete_page_action.setShortcut("Ctrl+Delete")
        self.delete_page_action.triggered.connect(self.delete_page)
        navigate_menu.addAction(self.delete_page_action)

        self.move_page_left_action = QAction(self.tr("Move Page Left"), self)
        self.move_page_left_action.setShortcut("Ctrl+PageUp")
        self.move_page_left_action.triggered.connect(lambda: self.move_page(-1))
        navigate_menu.addAction(self.move_page_left_action)

        self.move_page_right_action = QAction(self.tr("Move Page Right"), self)
        self.move_page_right_action.setShortcut("Ctrl+PageDown")
        self.move_page_right_action.triggered.connect(lambda: self.move_page(1))
        navigate_menu.addAction(self.move_page_right_action)

        view_menu = self.menuBar().addMenu(self.tr("&View"))
        fit_action = QAction(self.tr("Fit Page"), self)
        fit_action.setShortcut("2")
        fit_action.triggered.connect(self.canvas.fit_page)
        view_menu.addAction(fit_action)

        zoom_in_action = QAction(self.tr("Zoom In"), self)
        zoom_in_action.setShortcut("+")
        zoom_in_action.triggered.connect(self.canvas.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction(self.tr("Zoom Out"), self)
        zoom_out_action.setShortcut("-")
        zoom_out_action.triggered.connect(self.canvas.zoom_out)
        view_menu.addAction(zoom_out_action)

        reset_zoom_action = QAction(self.tr("Actual Size"), self)
        reset_zoom_action.setShortcut("1")
        reset_zoom_action.triggered.connect(self.canvas.reset_zoom)
        view_menu.addAction(reset_zoom_action)

    def open_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open Comic"),
            "",
            self.tr("TBO Files (*.tbo);;All Files (*)"),
        )
        if filename and self._confirm_replacing_modified_document():
            self.open_document(Path(filename))

    def new_document_dialog(self) -> None:
        dialog = NewComicDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        title, width, height = dialog.values()
        if self._confirm_replacing_modified_document():
            self.new_document(title, width, height)

    def new_document(self, title: str, width: int, height: int) -> None:
        self._set_document(Comic(title, width, height, [Page()]), filename=None)

    def open_document(self, filename: Path) -> bool:
        try:
            comic = load(filename)
        except TboFormatError as error:
            QMessageBox.critical(self, self.tr("Could Not Open File"), str(error))
            return False

        self._set_document(comic, filename=filename)
        return True

    def _set_document(self, comic: Comic, *, filename: Path | None) -> None:
        self.canvas.set_comic(comic)
        self._filename = filename
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)
        self._update_page_actions()
        self._update_edit_actions()
        self._update_window_title()
        self.canvas.fit_page()

    def save_document(self) -> bool:
        if self._filename is None:
            return self.save_as_dialog()
        return self._save_to(self._filename)

    def save_as_dialog(self) -> bool:
        if self.canvas.comic is None:
            return False
        suggested = str(self._filename or Path(f"{self.canvas.comic.title}.tbo"))
        filename, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save Comic"), suggested, self.tr("TBO Files (*.tbo)")
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
            QMessageBox.critical(self, self.tr("Could Not Save File"), str(error))
            return False
        self._filename = filename
        comic.title = filename.stem
        self.canvas.undo_stack.setClean()
        self._update_window_title()
        self.statusBar().showMessage(
            self.tr("Saved to {filename}").format(filename=filename), 5000
        )
        return True

    def _confirm_replacing_modified_document(self) -> bool:
        if self.canvas.comic is None or self.canvas.undo_stack.isClean():
            return True
        answer = QMessageBox.warning(
            self,
            self.tr("Unsaved Changes"),
            self.tr(
                "The document has unsaved changes. Do you want to save them before continuing?"
            ),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Save:
            return self.save_document()
        return answer == QMessageBox.StandardButton.Discard

    def closeEvent(self, event) -> None:
        if self._confirm_replacing_modified_document():
            event.accept()
        else:
            event.ignore()

    def previous_page(self) -> None:
        if self.canvas.previous_page():
            self.canvas.fit_page()
        self._update_page_actions()

    def next_page(self) -> None:
        if self.canvas.next_page():
            self.canvas.fit_page()
        self._update_page_actions()

    def add_page(self) -> None:
        self.canvas.add_page()

    def delete_page(self) -> None:
        self.canvas.delete_current_page()

    def move_page(self, offset: int) -> None:
        self.canvas.move_current_page(offset)

    def add_frame(self) -> None:
        frame = self.canvas.add_frame()
        if frame is not None:
            self._update_edit_actions()

    def delete_frame(self) -> None:
        deleted = (
            self.canvas.delete_selected_object()
            if self.canvas.editing_frame is not None
            else self.canvas.delete_selected_frame()
        )
        if deleted:
            self._update_edit_actions()

    def clone_frame(self) -> None:
        cloned = (
            self.canvas.clone_selected_object()
            if self.canvas.editing_frame is not None
            else self.canvas.clone_selected_frame()
        )
        if cloned is not None:
            self._update_edit_actions()

    def nudge_selected_frame(self, dx: int, dy: int) -> None:
        if self.canvas.editing_frame is not None:
            self.canvas.nudge_selected_object(dx, dy)
        else:
            self.canvas.nudge_selected_frame(dx, dy)

    def leave_frame(self) -> None:
        self.canvas.leave_frame()

    def _on_mode_changed(self, editing: bool) -> None:
        self._update_page_actions()
        self._update_edit_actions()

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
        editing = self.canvas.editing_frame is not None
        selected = self.canvas.selected_object() if editing else self.canvas.selected_frame()
        self.add_frame_action.setEnabled(has_page and not editing)
        self.delete_frame_action.setEnabled(selected is not None)
        self.clone_frame_action.setEnabled(selected is not None)
        self.delete_frame_action.setText(
            self.tr("Delete Object") if editing else self.tr("Delete Panel")
        )
        self.clone_frame_action.setText(
            self.tr("Clone Object") if editing else self.tr("Clone Panel")
        )
        self.leave_frame_action.setEnabled(editing)

    def _update_page_actions(self, *args) -> None:
        index = self.canvas.page_index
        count = self.canvas.page_count
        editing = self.canvas.editing_frame is not None
        self.previous_page_action.setEnabled(not editing and count > 0 and index > 0)
        self.next_page_action.setEnabled(not editing and count > 0 and index + 1 < count)
        self.add_page_action.setEnabled(not editing and self.canvas.comic is not None)
        self.delete_page_action.setEnabled(not editing and count > 1)
        self.move_page_left_action.setEnabled(not editing and count > 1 and index > 0)
        self.move_page_right_action.setEnabled(not editing and count > 1 and index + 1 < count)
        if editing:
            message = self.tr(
                "Editing panel — press Esc to return · Page {current} of {count}"
            ).format(current=index + 1, count=count)
        else:
            message = (
                self.tr("Page {current} of {count}").format(
                    current=index + 1, count=count
                )
                if count
                else self.tr("Document has no pages")
            )
        self.statusBar().showMessage(message)
