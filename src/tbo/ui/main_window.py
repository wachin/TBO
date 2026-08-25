from __future__ import annotations

import contextlib
import shutil
from copy import deepcopy
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QColor, QFont, QIcon, QImageReader, QKeySequence
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFontComboBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSpinBox,
    QToolButton,
)

from tbo.assets import AssetCatalog
from tbo.document.model import (
    Color,
    Comic,
    ImageObject,
    Page,
    SvgObject,
    TextObject,
)
from tbo.formats.tbo_v1 import TboFormatError, load, save
from tbo.rendering import ExportError, export_comic, export_page
from tbo.resources import user_asset_roots
from tbo.ui.assets_dock import AssetsDock
from tbo.ui.canvas import ComicCanvas
from tbo.ui.new_comic_dialog import NewComicDialog
from tbo.ui.pages_dock import PagesDock
from tbo.ui.preferences import Preferences
from tbo.ui.text_object_dialog import TextObjectDialog
from tbo.ui.theme import apply_theme


class MainWindow(QMainWindow):
    def __init__(self, *, asset_root: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle("TBO 2")
        self.resize(1000, 700)
        self._filename: Path | None = None
        self._clipboard: list = []
        self._clipboard_is_objects = False
        self.preferences = Preferences()
        self.canvas = ComicCanvas(asset_root=asset_root)
        self.setCentralWidget(self.canvas)
        self._restore_window_state()
        self.asset_roots = [asset_root] if asset_root is not None else []
        self.asset_roots.extend(user_asset_roots())
        self.assets_catalog = AssetCatalog(self.asset_roots) if self.asset_roots else None
        self.assets_dock: AssetsDock | None = None
        if self.assets_catalog is not None:
            self.assets_dock = AssetsDock(self.assets_catalog, self)
            self.assets_dock.assetActivated.connect(self.add_svg_from_path)
            self.assets_dock.bubbleActivated.connect(self.add_bubble_from_path)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.assets_dock)
        self.pages_dock = PagesDock(self, asset_root=asset_root)
        self.pages_dock.pageSelected.connect(self._go_to_page)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pages_dock)
        self._create_actions()
        self._create_toolbar()
        self._create_text_toolbar()
        self.canvas.undo_stack.cleanChanged.connect(self._on_clean_changed)
        self.canvas.undo_stack.indexChanged.connect(self._refresh_page_thumbnails)
        self.canvas.pageChanged.connect(self._update_page_actions)
        self.canvas.pageChanged.connect(self.pages_dock.set_current_page)
        self.canvas.modeChanged.connect(self._on_mode_changed)
        self.canvas.scene.selectionChanged.connect(self._update_edit_actions)
        self.canvas.assetDropped.connect(self.add_svg_from_path)
        self.canvas.zoomChanged.connect(self._update_zoom_label)
        self.canvas.set_snap_to_grid(self.preferences.snap_to_grid())
        self.zoom_label = QLabel(self.tr("100%"))
        self.statusBar().addPermanentWidget(self.zoom_label)
        self._update_edit_actions()
        self.autosave_timer = QTimer(self)
        self.autosave_timer.setInterval(30_000)
        self.autosave_timer.timeout.connect(self._autosave)
        self.autosave_timer.start()

    def _create_actions(self) -> None:
        file_menu = self.menuBar().addMenu(self.tr("&File"))
        self.new_action = QAction(self.tr("&New…"), self)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.setIcon(self._action_icon("document-new.svg"))
        self.new_action.setToolTip(self.tr("New"))
        self.new_action.triggered.connect(self.new_document_dialog)
        file_menu.addAction(self.new_action)

        self.open_action = QAction(self.tr("&Open…"), self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.setIcon(self._action_icon("document-open.svg"))
        self.open_action.setToolTip(self.tr("Open"))
        self.open_action.triggered.connect(self.open_dialog)
        file_menu.addAction(self.open_action)

        self.save_action = QAction(self.tr("&Save"), self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setIcon(self._action_icon("document-save.svg"))
        self.save_action.setToolTip(self.tr("Save"))
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self.save_document)
        file_menu.addAction(self.save_action)

        self.save_as_action = QAction(self.tr("Save &As…"), self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setIcon(self._action_icon("document-save.svg"))
        self.save_as_action.setToolTip(self.tr("Save As"))
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self.save_as_dialog)
        file_menu.addAction(self.save_as_action)

        self.export_action = QAction(self.tr("&Export…"), self)
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setEnabled(False)
        self.export_action.triggered.connect(self.export_dialog)
        file_menu.addAction(self.export_action)

        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu(self.tr("&Recent Files"))
        self.recent_menu.menuAction().setEnabled(False)
        self._refresh_recent_files()

        edit_menu = self.menuBar().addMenu(self.tr("&Edit"))
        self.undo_action = self.canvas.undo_stack.createUndoAction(self, self.tr("&Undo"))
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.setIcon(self._action_icon("edit-undo.svg"))
        self.undo_action.setToolTip(self.tr("Undo"))
        edit_menu.addAction(self.undo_action)
        self.redo_action = self.canvas.undo_stack.createRedoAction(self, self.tr("&Redo"))
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.setIcon(self._action_icon("edit-redo.svg"))
        self.redo_action.setToolTip(self.tr("Redo"))
        edit_menu.addAction(self.redo_action)

        self.copy_action = QAction(self.tr("&Copy"), self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.copy_selection)
        edit_menu.addAction(self.copy_action)
        self.paste_action = QAction(self.tr("&Paste"), self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.setEnabled(False)
        self.paste_action.triggered.connect(self.paste_clipboard)
        edit_menu.addAction(self.paste_action)

        self.select_all_action = QAction(self.tr("Select &All"), self)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        self.select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(self.select_all_action)

        edit_menu.addSeparator()
        self.add_frame_action = QAction(self.tr("Add &Panel"), self)
        self.add_frame_action.setShortcut("F")
        self.add_frame_action.setIcon(self._action_icon("add-panel.svg"))
        self.add_frame_action.setToolTip(self.tr("Add Panel"))
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

        align_menu = edit_menu.addMenu(self.tr("Ali&gn"))
        self.align_left_action = QAction(self.tr("Left"), self)
        self.align_left_action.triggered.connect(lambda: self.canvas.align_selected_frames("left"))
        align_menu.addAction(self.align_left_action)
        self.align_hcenter_action = QAction(self.tr("Horizontal Center"), self)
        self.align_hcenter_action.triggered.connect(
            lambda: self.canvas.align_selected_frames("hcenter")
        )
        align_menu.addAction(self.align_hcenter_action)
        self.align_right_action = QAction(self.tr("Right"), self)
        self.align_right_action.triggered.connect(
            lambda: self.canvas.align_selected_frames("right")
        )
        align_menu.addAction(self.align_right_action)
        align_menu.addSeparator()
        self.align_top_action = QAction(self.tr("Top"), self)
        self.align_top_action.triggered.connect(lambda: self.canvas.align_selected_frames("top"))
        align_menu.addAction(self.align_top_action)
        self.align_vcenter_action = QAction(self.tr("Vertical Center"), self)
        self.align_vcenter_action.triggered.connect(
            lambda: self.canvas.align_selected_frames("vcenter")
        )
        align_menu.addAction(self.align_vcenter_action)
        self.align_bottom_action = QAction(self.tr("Bottom"), self)
        self.align_bottom_action.triggered.connect(
            lambda: self.canvas.align_selected_frames("bottom")
        )
        align_menu.addAction(self.align_bottom_action)

        distribute_menu = edit_menu.addMenu(self.tr("&Distribute"))
        self.distribute_h_action = QAction(self.tr("Horizontally"), self)
        self.distribute_h_action.triggered.connect(
            lambda: self.canvas.distribute_selected_frames("horizontal")
        )
        distribute_menu.addAction(self.distribute_h_action)
        self.distribute_v_action = QAction(self.tr("Vertically"), self)
        self.distribute_v_action.triggered.connect(
            lambda: self.canvas.distribute_selected_frames("vertical")
        )
        distribute_menu.addAction(self.distribute_v_action)

        edit_menu.addSeparator()
        self.add_text_action = QAction(self.tr("Add &Text…"), self)
        self.add_text_action.setShortcut("T")
        self.add_text_action.setIcon(self._action_icon("draw-text.svg"))
        self.add_text_action.setToolTip(self.tr("Add Text"))
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
        self.flip_horizontal_action.setIcon(self._action_icon("flip-horizontal.svg"))
        self.flip_horizontal_action.setToolTip(self.tr("Flip Horizontally"))
        self.flip_horizontal_action.triggered.connect(
            lambda: self.flip_selected_object("horizontal")
        )
        edit_menu.addAction(self.flip_horizontal_action)

        self.flip_vertical_action = QAction(self.tr("Flip &Vertically"), self)
        self.flip_vertical_action.setShortcut("V")
        self.flip_vertical_action.setIcon(self._action_icon("flip-vertical.svg"))
        self.flip_vertical_action.setToolTip(self.tr("Flip Vertically"))
        self.flip_vertical_action.triggered.connect(lambda: self.flip_selected_object("vertical"))
        edit_menu.addAction(self.flip_vertical_action)

        self.edit_text_action = QAction(self.tr("Edit &Text…"), self)
        self.edit_text_action.setShortcut("E")
        self.edit_text_action.triggered.connect(self.edit_text_dialog)
        edit_menu.addAction(self.edit_text_action)

        edit_menu.addSeparator()
        self.find_text_action = QAction(self.tr("&Find Text…"), self)
        self.find_text_action.setShortcut(QKeySequence.StandardKey.Find)
        self.find_text_action.triggered.connect(self._open_search_dialog)
        edit_menu.addAction(self.find_text_action)

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
        self.fit_page_action = QAction(self.tr("Fit Page"), self)
        self.fit_page_action.setShortcut("2")
        self.fit_page_action.setIcon(self._action_icon("zoom-fit-page.svg"))
        self.fit_page_action.setToolTip(self.tr("Fit Page"))
        self.fit_page_action.triggered.connect(self.canvas.fit_page)
        view_menu.addAction(self.fit_page_action)

        self.zoom_in_action = QAction(self.tr("Zoom In"), self)
        self.zoom_in_action.setShortcut("+")
        self.zoom_in_action.setIcon(self._action_icon("zoom-in.svg"))
        self.zoom_in_action.setToolTip(self.tr("Zoom In"))
        self.zoom_in_action.triggered.connect(self.canvas.zoom_in)
        view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction(self.tr("Zoom Out"), self)
        self.zoom_out_action.setShortcut("-")
        self.zoom_out_action.setIcon(self._action_icon("zoom-out.svg"))
        self.zoom_out_action.setToolTip(self.tr("Zoom Out"))
        self.zoom_out_action.triggered.connect(self.canvas.zoom_out)
        view_menu.addAction(self.zoom_out_action)

        self.reset_zoom_action = QAction(self.tr("Actual Size"), self)
        self.reset_zoom_action.setShortcut("1")
        self.reset_zoom_action.setIcon(self._action_icon("zoom-original.svg"))
        self.reset_zoom_action.setToolTip(self.tr("Actual Size"))
        self.reset_zoom_action.triggered.connect(self.canvas.reset_zoom)
        view_menu.addAction(self.reset_zoom_action)

        self.present_action = QAction(self.tr("&Presentation…"), self)
        self.present_action.setShortcut("F5")
        self.present_action.triggered.connect(self.start_presentation)
        view_menu.addAction(self.present_action)

        self.snap_action = QAction(self.tr("S&nap to Grid"), self)
        self.snap_action.setCheckable(True)
        self.snap_action.setChecked(self.preferences.snap_to_grid())
        self.snap_action.toggled.connect(self._on_snap_toggled)
        view_menu.addAction(self.snap_action)

        theme_menu = view_menu.addMenu(self.tr("&Theme"))
        self._theme_group = QActionGroup(self)
        self._theme_group.setExclusive(True)
        self._theme_actions: dict[str, QAction] = {}
        for mode, label in (
            ("system", self.tr("System")),
            ("dark", self.tr("Dark")),
            ("light", self.tr("Light")),
        ):
            action = QAction(label, self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked=False, m=mode: self._set_theme(m))
            self._theme_group.addAction(action)
            self._theme_actions[mode] = action
            theme_menu.addAction(action)
        current = self.preferences.theme()
        self._set_theme(current)

        help_menu = self.menuBar().addMenu(self.tr("&Help"))
        help_action = QAction(self.tr("&Help Contents"), self)
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)

        about_action = QAction(self.tr("&About TBO"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _show_help(self) -> None:
        from tbo.ui.help_dialog import HelpDialog

        dialog = HelpDialog(self)
        dialog.exec()

    def _show_about(self) -> None:
        from tbo.ui.about_dialog import AboutDialog

        dialog = AboutDialog(self)
        dialog.exec()

    def _action_icon(self, name: str) -> QIcon:
        icon_dir = Path(__file__).resolve().parent.parent / "resources" / "icons"
        return QIcon(str(icon_dir / name))

    def _create_toolbar(self) -> None:
        toolbar = self.addToolBar(self.tr("Main Toolbar"))
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.save_as_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.add_frame_action)
        toolbar.addAction(self.add_text_action)
        toolbar.addSeparator()
        toolbar.addAction(self.flip_horizontal_action)
        toolbar.addAction(self.flip_vertical_action)
        toolbar.addSeparator()
        toolbar.addAction(self.zoom_in_action)
        toolbar.addAction(self.zoom_out_action)
        toolbar.addAction(self.reset_zoom_action)
        toolbar.addAction(self.fit_page_action)

    def _create_text_toolbar(self) -> None:
        text_toolbar = self.addToolBar(self.tr("Text"))
        text_toolbar.setObjectName("text_toolbar")
        text_toolbar.setMovable(False)
        text_toolbar.setEnabled(False)
        self.text_toolbar = text_toolbar

        self.text_font_combo = QFontComboBox()
        self.text_font_combo.setMaximumWidth(140)
        self.text_font_combo.setToolTip(self.tr("Font family"))
        self.text_font_combo.currentFontChanged.connect(self._apply_text_style)
        text_toolbar.addWidget(self.text_font_combo)

        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(6, 144)
        self.text_size_spin.setValue(8)
        self.text_size_spin.setFixedWidth(56)
        self.text_size_spin.setSuffix(" pt")
        self.text_size_spin.setToolTip(self.tr("Font size"))
        self.text_size_spin.valueChanged.connect(self._apply_text_style)
        text_toolbar.addWidget(self.text_size_spin)

        self.text_bold_button = QToolButton()
        self.text_bold_button.setText(self.tr("B"))
        self.text_bold_button.setCheckable(True)
        self.text_bold_button.setToolTip(self.tr("Bold"))
        self.text_bold_button.setStyleSheet("font-weight: bold;")
        self.text_bold_button.toggled.connect(self._apply_text_style)
        text_toolbar.addWidget(self.text_bold_button)

        self.text_italic_button = QToolButton()
        self.text_italic_button.setText(self.tr("I"))
        self.text_italic_button.setCheckable(True)
        self.text_italic_button.setToolTip(self.tr("Italic"))
        self.text_italic_button.setStyleSheet("font-style: italic;")
        self.text_italic_button.toggled.connect(self._apply_text_style)
        text_toolbar.addWidget(self.text_italic_button)

        self.text_underline_button = QToolButton()
        self.text_underline_button.setText(self.tr("U"))
        self.text_underline_button.setCheckable(True)
        self.text_underline_button.setToolTip(self.tr("Underline"))
        self.text_underline_button.setStyleSheet("text-decoration: underline;")
        self.text_underline_button.toggled.connect(self._apply_text_style)
        text_toolbar.addWidget(self.text_underline_button)

        self.text_color_button = QToolButton()
        self.text_color_button.setText("")
        self.text_color_button.setToolTip(self.tr("Text color"))
        self.text_color_button.setFixedWidth(28)
        self.text_color_button.setStyleSheet("background-color: black;")
        self.text_color_button.clicked.connect(self._choose_text_color)
        text_toolbar.addWidget(self.text_color_button)

    def _apply_text_style(self, *args) -> None:
        obj = self.canvas.selected_object()
        if not isinstance(obj, TextObject):
            return
        family = self.text_font_combo.currentFont().family()
        size = self.text_size_spin.value()
        self.canvas.edit_text_object(
            obj,
            obj.text,
            f"{family} {size}",
            obj.color,
            self.text_bold_button.isChecked(),
            self.text_italic_button.isChecked(),
            self.text_underline_button.isChecked(),
        )
        self._update_edit_actions()

    def _choose_text_color(self) -> None:
        obj = self.canvas.selected_object()
        if not isinstance(obj, TextObject):
            return
        current = QColor.fromRgbF(obj.color.red, obj.color.green, obj.color.blue)
        color = QColorDialog.getColor(current, self, self.tr("Choose Text Color"))
        if color.isValid():
            self.canvas.edit_text_object(
                obj,
                obj.text,
                obj.font,
                Color(color.redF(), color.greenF(), color.blueF()),
            )
            self._sync_text_toolbar()

    def _sync_text_toolbar(self) -> None:
        obj = self.canvas.selected_object()
        is_text = isinstance(obj, TextObject)
        self.text_toolbar.setEnabled(self.canvas.editing_frame is not None and is_text)
        if not is_text:
            return
        family, _, size = obj.font.rpartition(" ")
        self.text_font_combo.blockSignals(True)
        self.text_font_combo.setCurrentFont(QFont(family))
        self.text_font_combo.blockSignals(False)
        self.text_size_spin.blockSignals(True)
        if size.isdigit():
            self.text_size_spin.setValue(int(size))
        self.text_size_spin.blockSignals(False)
        self.text_bold_button.blockSignals(True)
        self.text_bold_button.setChecked(obj.bold)
        self.text_bold_button.blockSignals(False)
        self.text_italic_button.blockSignals(True)
        self.text_italic_button.setChecked(obj.italic)
        self.text_italic_button.blockSignals(False)
        self.text_underline_button.blockSignals(True)
        self.text_underline_button.setChecked(obj.underline)
        self.text_underline_button.blockSignals(False)
        color = QColor.fromRgbF(obj.color.red, obj.color.green, obj.color.blue)
        self.text_color_button.setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {'white' if color.lightness() < 128 else 'black'};"
        )

    def _directory_hint(self) -> Path:
        return self.preferences.last_directory() or Path.home()

    def open_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open Comic"),
            str(self._directory_hint()),
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
        self.preferences.add_recent_file(filename.resolve())
        self.preferences.set_last_directory(filename.parent.resolve())
        self._refresh_recent_files()
        return True

    def _set_document(self, comic: Comic, *, filename: Path | None) -> None:
        self._clear_autosave()
        self.canvas.set_comic(comic)
        self.pages_dock.set_comic(comic)
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
        suggested = str(
            self._filename or Path(self._directory_hint()) / f"{self.canvas.comic.title}.tbo"
        )
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
        from tbo.ui.export_dialog import ExportDialog

        options = ExportDialog(
            self,
            page_count=self.canvas.page_count,
            current_page=self.canvas.page_index,
        )
        if options.exec() != QDialog.DialogCode.Accepted:
            return
        fmt_key, current_only, scale = options.values()
        default_name = (
            self._filename.stem if self._filename is not None else self.canvas.comic.title
        )
        filter_label = {
            "png": "PNG Images (*.png)",
            "pdf": "PDF Document (*.pdf)",
            "svg": "SVG Image (*.svg)",
        }[fmt_key]
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Export Comic"),
            str(Path(self._directory_hint()) / default_name),
            filter_label,
        )
        if not filename:
            return
        target = Path(filename)
        try:
            if current_only and fmt_key != "pdf":
                written = [
                    export_page(
                        self.canvas.current_page,
                        self.canvas.comic,
                        target,
                        fmt=fmt_key,
                        asset_root=self._asset_root(),
                        scale=scale / 100.0,
                    )
                ]
            else:
                written = export_comic(
                    self.canvas.comic,
                    target,
                    fmt=fmt_key,
                    asset_root=self._asset_root(),
                    scale=scale / 100.0,
                )
        except ExportError as error:
            QMessageBox.critical(self, self.tr("Could Not Export"), str(error))
            return
        if written:
            self.preferences.set_last_directory(target.parent.resolve())
            self.statusBar().showMessage(
                self.tr("Exported {count} file(s)").format(count=len(written)), 5000
            )

    def _asset_root(self) -> Path | None:
        return self.canvas._asset_root

    def _go_to_page(self, index: int) -> None:
        if index < 0 or index >= self.canvas.page_count:
            return
        if self.canvas.editing_frame is not None:
            self.canvas.leave_frame()
        self.canvas.show_page(index)
        self.canvas.fit_page()
        self._update_page_actions()

    def _open_search_dialog(self) -> None:
        if self.canvas.comic is None:
            return
        from tbo.ui.search_dialog import SearchDialog

        dialog = SearchDialog(self.canvas.comic, self)
        dialog.goTo.connect(self._go_to_search_result)
        dialog.exec()

    def _go_to_search_result(self, page_index: int, frame, graphic_object) -> None:
        self.canvas.show_page(page_index)
        self.canvas.fit_page()
        if self.canvas.enter_frame(frame):
            self.canvas.select_object(graphic_object)
            item = self.canvas._object_items.get(id(graphic_object))
            if item is not None:
                self.canvas.centerOn(item)
        self._update_page_actions()
        self._update_edit_actions()

    def _refresh_page_thumbnails(self, *args) -> None:
        if self.canvas.comic is not None:
            self.pages_dock._render_all()

    def start_presentation(self) -> None:
        if self.canvas.comic is None:
            return
        from tbo.ui.presentation import PresentationDialog

        dialog = PresentationDialog(
            self.canvas.comic,
            start_page=self.canvas.page_index,
            parent=self,
            asset_root=self._asset_root(),
        )
        dialog.exec()

    def _refresh_recent_files(self) -> None:
        self.recent_menu.clear()
        recent = self.preferences.recent_files()
        self.recent_menu.menuAction().setEnabled(bool(recent))
        for filename in recent:
            action = self.recent_menu.addAction(str(filename))
            action.triggered.connect(
                lambda checked=False, path=filename: self._open_recent_file(path)
            )

    def _open_recent_file(self, filename: Path) -> None:
        if not filename.is_file():
            self.preferences.remove_recent_file(filename)
            self._refresh_recent_files()
            QMessageBox.warning(
                self,
                self.tr("File Not Found"),
                self.tr("{filename} no longer exists.").format(filename=filename),
            )
            return
        if self._confirm_replacing_modified_document():
            self.open_document(filename)

    def _save_to(self, filename: Path) -> bool:
        comic = self.canvas.comic
        if comic is None:
            return False
        try:
            self._backup_existing(filename)
            save(comic, filename)
        except TboFormatError as error:
            QMessageBox.critical(self, self.tr("Could Not Save File"), str(error))
            return False
        self._filename = filename
        comic.title = filename.stem
        self.canvas.undo_stack.setClean()
        self._clear_autosave()
        self.preferences.add_recent_file(filename.resolve())
        self.preferences.set_last_directory(filename.parent.resolve())
        self._refresh_recent_files()
        self._update_window_title()
        self.statusBar().showMessage(self.tr("Saved to {filename}").format(filename=filename), 5000)
        return True

    def _backup_existing(self, filename: Path) -> None:
        if not filename.is_file():
            return
        backup = filename.with_suffix(filename.suffix + ".bak")
        with contextlib.suppress(OSError):
            shutil.copy2(filename, backup)

    def _autosave_path(self, filename: Path) -> Path:
        return filename.with_suffix(filename.suffix + ".autosave")

    def _autosave(self) -> None:
        if self._filename is None or self.canvas.undo_stack.isClean():
            return
        comic = self.canvas.comic
        if comic is None:
            return
        with contextlib.suppress(TboFormatError):
            save(comic, self._autosave_path(self._filename))

    def _clear_autosave(self) -> None:
        if self._filename is None:
            return
        with contextlib.suppress(OSError):
            self._autosave_path(self._filename).unlink()

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
            self.preferences.set_last_filename(
                self._filename.resolve() if self._filename is not None else None
            )
            self._save_window_state()
            event.accept()
        else:
            event.ignore()

    def _restore_window_state(self) -> None:
        geometry = self.preferences.window_geometry()
        if geometry is not None:
            self.restoreGeometry(geometry)

    def _save_window_state(self) -> None:
        self.preferences.set_window_geometry(self.saveGeometry())

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
        dialog.set_color(
            QColor.fromRgbF(selected.color.red, selected.color.green, selected.color.blue)
        )
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

    def select_all(self) -> None:
        self.canvas.select_all()
        self._update_edit_actions()

    def copy_selection(self) -> None:
        if self.canvas.editing_frame is not None:
            objects = self.canvas.selected_objects()
            if not objects:
                return
            self._clipboard = [deepcopy(obj) for obj in objects]
            self._clipboard_is_objects = True
        else:
            frames = self.canvas.selected_frames()
            if not frames:
                return
            self._clipboard = [deepcopy(frame) for frame in frames]
            self._clipboard_is_objects = False
        for item in self._clipboard:
            item.x += 10
            item.y += 10
        self.paste_action.setEnabled(True)

    def paste_clipboard(self) -> None:
        if not self._clipboard:
            return
        if self._clipboard_is_objects:
            objects = [deepcopy(item) for item in self._clipboard]
            if self.canvas.editing_frame is None:
                return
            self.canvas.add_objects(objects)
        else:
            frames = [deepcopy(item) for item in self._clipboard]
            if self.canvas.editing_frame is not None:
                return
            self.canvas.add_frames(frames)
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
            str(self._directory_hint()),
            self.tr("Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)"),
        )
        if filename:
            selected = Path(filename)
            if self.add_image_from_path(selected):
                self.preferences.set_last_directory(selected.parent.resolve())
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Could Not Add Image"),
                    self.tr("The selected file is not a supported or readable image."),
                )

    def add_svg_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Add SVG"),
            str(self._directory_hint()),
            self.tr("SVG Files (*.svg);;All Files (*)"),
        )
        if filename:
            selected = Path(filename)
            if self.add_svg_from_path(selected):
                self.preferences.set_last_directory(selected.parent.resolve())
            else:
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

    def add_bubble_from_path(self, filename: Path) -> bool:
        if self.canvas.editing_frame is None:
            return False
        renderer = QSvgRenderer(str(filename))
        if not renderer.isValid():
            return False
        size = renderer.defaultSize()
        width, height = self._fitted_object_size(size.width(), size.height())
        x, y = self._centered_position(width, height)
        if not self.canvas.add_graphic_object(
            SvgObject(
                x=x,
                y=y,
                width=width,
                height=height,
                path=filename.resolve(),
            )
        ):
            return False
        text_width = max(1, int(width * 0.8))
        text_height = max(1, int(height * 0.65))
        self.canvas.add_graphic_object(
            TextObject(
                x=x + (width - text_width) // 2,
                y=y + (height - text_height) // 2,
                width=text_width,
                height=text_height,
                text=self.tr("Text"),
                font="Sans 8",
                color=Color(0.0, 0.0, 0.0),
            )
        )
        return True

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
        self.select_all_action.setEnabled(has_page)
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
        frame_count = len(self.canvas.selected_frames()) if not editing else 0
        can_align = frame_count >= 2
        can_distribute = frame_count >= 3
        for action in (
            self.align_left_action,
            self.align_hcenter_action,
            self.align_right_action,
            self.align_top_action,
            self.align_vcenter_action,
            self.align_bottom_action,
        ):
            action.setEnabled(can_align)
        self.distribute_h_action.setEnabled(can_distribute)
        self.distribute_v_action.setEnabled(can_distribute)
        selected_object = self.canvas.selected_object()
        object_selected = editing and selected_object is not None
        self.rotate_left_action.setEnabled(object_selected)
        self.rotate_right_action.setEnabled(object_selected)
        self.flip_horizontal_action.setEnabled(object_selected)
        self.flip_vertical_action.setEnabled(object_selected)
        self.edit_text_action.setEnabled(
            object_selected and isinstance(selected_object, TextObject)
        )
        has_selection = bool(self.canvas.selected_objects()) if editing else frame_count > 0
        self.copy_action.setEnabled(has_selection)
        clipboard_matches = editing == self._clipboard_is_objects if self._clipboard else False
        self.paste_action.setEnabled(bool(self._clipboard) and clipboard_matches)
        self._sync_text_toolbar()

    def _update_zoom_label(self, percent: int) -> None:
        self.zoom_label.setText(self.tr("{percent}%").format(percent=percent))

    def _on_snap_toggled(self, enabled: bool) -> None:
        self.preferences.set_snap_to_grid(enabled)
        self.canvas.set_snap_to_grid(enabled)

    def _set_theme(self, mode: str) -> None:
        self.preferences.set_theme(mode)
        application = QApplication.instance()
        if application is not None:
            apply_theme(application, mode)
        action = self._theme_actions.get(mode)
        if action is not None:
            action.setChecked(True)

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
                self.tr("Page {current} of {count}").format(current=index + 1, count=count)
                if count
                else self.tr("Document has no pages")
            )
        self.statusBar().showMessage(message)
