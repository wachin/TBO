from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QFont, QImageReader, QKeySequence
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMessageBox

from tbo.assets import AssetCatalog
from tbo.document.model import Color, Comic, ImageObject, Page, SvgObject, TextObject
from tbo.formats.tbo_v1 import TboFormatError, load, save
from tbo.rendering import ExportError, export_comic
from tbo.ui.assets_dock import AssetsDock
from tbo.ui.canvas import ComicCanvas
from tbo.ui.new_comic_dialog import NewComicDialog
from tbo.ui.text_object_dialog import TextObjectDialog


class MainWindow(QMainWindow):
    def __init__(self, *, asset_root: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("TBO 2")
        self.resize(1000, 700)
        self._filename: Path | None = None
        self.canvas = ComicCanvas(asset_root=asset_root)
        self.setCentralWidget(self.canvas)
        self.assets_catalog = AssetCatalog(asset_root) if asset_root is not None else None
        self.assets_dock: AssetsDock | None = None
        if self.assets_catalog is not None:
            self.assets_dock = AssetsDock(self.assets_catalog, self)
            self.assets_dock.assetActivated.connect(self.add_svg_from_path)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.assets_dock)
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

        self.export_action = QAction(self.tr("&Export…"), self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setEnabled(False)
        self.export_action.triggered.connect(self.export_dialog)
        file_menu.addAction(self.export_action)

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

        edit_menu.addSeparator()
        self.add_text_action = QAction(self.tr("Add &Text…"), self)
        self.add_text_action.setShortcut("T")
        self.add_text_action.triggered.connect(self.add_text_dialog)
        edit_menu.addAction(self.add_text_action)

        self.add_image_action = QAction(self.tr("Add &Image…"), self)
        self.add_image_action.triggered.connect(self.add_image_dialog)
        edit_menu.addAction(self.add_image_action)

        self.add_svg_action = QAction(self.tr("Add &SVG…"), self)
        self.add_svg_action.triggered.connect(self.add_svg_dialog)
        edit_menu.addAction(self.add_svg_action)

        edit_menu.addSeparator()
        self.rotate_left_action = QAction(self.tr("Rotate &Left"), self)
        self.rotate_left_action.setShortcut("[")
        self.rotate_left_action.triggered.connect(lambda: self.rotate_selected_object(-15))
        edit_menu.addAction(self.rotate_left_action)

        self.rotate_right_action = QAction(self.tr("Rotate &Right"), self)
        self.rotate_right_action.setShortcut("]")
        self.rotate_right_action.triggered.connect(lambda: self.rotate_selected_object(15))
        edit_menu.addAction(self.rotate_right_action)

        self.flip_horizontal_action = QAction(self.tr("Flip &Horizontally"), self)
        self.flip_horizontal_action.setShortcut("H")
        self.flip_horizontal_action.triggered.connect(lambda: self.flip_selected_object("horizontal"))
        edit_menu.addAction(self.flip_horizontal_action)

        self.flip_vertical_action = QAction(self.tr("Flip &Vertically"), self)
        self.flip_vertical_action.setShortcut("V")
        self.flip_vertical_action.triggered.connect(lambda: self.flip_selected_object("vertical"))
        edit_menu.addAction(self.flip_vertical_action)

        self.edit_text_action = QAction(self.tr("Edit &Text…"), self)
        self.edit_text_action.setShortcut("E")
        self.edit_text_action.triggered.connect(self.edit_text_dialog)
        edit_menu.addAction(self.edit_text_action)

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
        self.export_action.setEnabled(True)
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

    def export_dialog(self) -> None:
        if self.canvas.comic is None:
            return
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            self.tr("Export Comic"),
            str(self._filename or Path(f"{self.canvas.comic.title}")),
            self.tr("PNG Images (*.png);;PDF Document (*.pdf);;SVG Image (*.svg)"),
        )
        if not filename:
            return
        target = Path(filename)
        fmt = {
            "PNG Images (*.png)": "png",
            "PDF Document (*.pdf)": "pdf",
            "SVG Image (*.svg)": "svg",
        }.get(selected_filter)
        if fmt is None:
            fmt = target.suffix.lstrip(".") or "png"
        try:
            written = export_comic(
                self.canvas.comic,
                target,
                fmt=fmt,
                asset_root=self._asset_root(),
            )
        except ExportError as error:
            QMessageBox.critical(self, self.tr("Could Not Export"), str(error))
            return
        if written:
            self.statusBar().showMessage(
                self.tr("Exported {count} file(s)").format(count=len(written)), 5000
            )

    def _asset_root(self) -> Path | None:
        return self.canvas._asset_root

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

    def rotate_selected_object(self, delta_degrees: float) -> None:
        if self.canvas.rotate_selected_object(delta_degrees):
            self._update_edit_actions()

    def flip_selected_object(self, axis: str) -> None:
        if self.canvas.flip_selected_object(axis):
            self._update_edit_actions()

    def edit_text_dialog(self) -> None:
        selected = self.canvas.selected_object()
        if not isinstance(selected, TextObject):
            return
        dialog = TextObjectDialog(self)
        dialog.set_color(QColor.fromRgbF(selected.color.red, selected.color.green, selected.color.blue))
        dialog.text_input.setPlainText(selected.text)
        family, _, size = selected.font.rpartition(" ")
        if family and size.isdigit():
            dialog.font_input.setCurrentFont(QFont(family))
            dialog.size_input.setValue(int(size))
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        text, font, qt_color = dialog.values()
        if self.canvas.edit_text_object(
            selected,
            text,
            font,
            Color(qt_color.redF(), qt_color.greenF(), qt_color.blueF()),
        ):
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

    def add_text_dialog(self) -> None:
        if self.canvas.editing_frame is None:
            return
        dialog = TextObjectDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        text, font, qt_color = dialog.values()
        frame = self.canvas.editing_frame
        if frame is None:
            return
        width = min(300, max(1, frame.width - 40))
        height = min(120, max(1, frame.height - 40))
        x, y = self._centered_position(width, height)
        self.canvas.add_graphic_object(
            TextObject(
                x=x,
                y=y,
                width=width,
                height=height,
                text=text,
                font=font,
                color=Color(qt_color.redF(), qt_color.greenF(), qt_color.blueF()),
            )
        )

    def add_image_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Add Image"),
            "",
            self.tr("Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)"),
        )
        if filename and not self.add_image_from_path(Path(filename)):
            QMessageBox.warning(
                self,
                self.tr("Could Not Add Image"),
                self.tr("The selected file is not a supported or readable image."),
            )

    def add_svg_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, self.tr("Add SVG"), "", self.tr("SVG Files (*.svg);;All Files (*)")
        )
        if filename and not self.add_svg_from_path(Path(filename)):
            QMessageBox.warning(
                self,
                self.tr("Could Not Add SVG"),
                self.tr("The selected file is not a valid SVG image."),
            )

    def add_image_from_path(self, filename: Path) -> bool:
        if self.canvas.editing_frame is None:
            return False
        reader = QImageReader(str(filename))
        if not reader.canRead():
            return False
        size = reader.size()
        width, height = self._fitted_object_size(size.width(), size.height())
        x, y = self._centered_position(width, height)
        return self.canvas.add_graphic_object(
            ImageObject(
                x=x,
                y=y,
                width=width,
                height=height,
                path=filename.resolve(),
            )
        )

    def add_svg_from_path(self, filename: Path) -> bool:
        if self.canvas.editing_frame is None:
            return False
        renderer = QSvgRenderer(str(filename))
        if not renderer.isValid():
            return False
        size = renderer.defaultSize()
        width, height = self._fitted_object_size(size.width(), size.height())
        x, y = self._centered_position(width, height)
        return self.canvas.add_graphic_object(
            SvgObject(
                x=x,
                y=y,
                width=width,
                height=height,
                path=filename.resolve(),
            )
        )

    def _fitted_object_size(self, natural_width: int, natural_height: int) -> tuple[int, int]:
        frame = self.canvas.editing_frame
        if frame is None:
            return 1, 1
        width = max(1, natural_width)
        height = max(1, natural_height)
        maximum_width = max(1, int(frame.width * 0.7))
        maximum_height = max(1, int(frame.height * 0.7))
        scale = min(1.0, maximum_width / width, maximum_height / height)
        return max(1, round(width * scale)), max(1, round(height * scale))

    def _centered_position(self, width: int, height: int) -> tuple[int, int]:
        frame = self.canvas.editing_frame
        if frame is None:
            return 0, 0
        return (frame.width - width) // 2, (frame.height - height) // 2

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
        self.add_text_action.setEnabled(editing)
        self.add_image_action.setEnabled(editing)
        self.add_svg_action.setEnabled(editing)
        if self.assets_dock is not None:
            self.assets_dock.setEnabled(editing)
        selected_object = self.canvas.selected_object()
        object_selected = editing and selected_object is not None
        self.rotate_left_action.setEnabled(object_selected)
        self.rotate_right_action.setEnabled(object_selected)
        self.flip_horizontal_action.setEnabled(object_selected)
        self.flip_vertical_action.setEnabled(object_selected)
        self.edit_text_action.setEnabled(object_selected and isinstance(selected_object, TextObject))

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
