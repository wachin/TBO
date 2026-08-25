from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QImage, QPainter, QPalette, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from tbo import __version__
from tbo.resources import find_icon

LOGO_SIZE = 300


def _logo_pixmap() -> QPixmap:
    icon_path = find_icon()
    if icon_path is None:
        return QPixmap()
    if icon_path.suffix.lower() == ".svg":
        renderer = QSvgRenderer(str(icon_path))
        image = QImage(LOGO_SIZE, LOGO_SIZE, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        renderer.render(painter, QRectF(0, 0, LOGO_SIZE, LOGO_SIZE))
        painter.end()
        return QPixmap.fromImage(image)
    pixmap = QPixmap(str(icon_path))
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(
        LOGO_SIZE,
        LOGO_SIZE,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

EMAIL = "linuxfrontier@proton.me"
REPOSITORY = "https://github.com/wachin/TBO"


def _link_color(application: QApplication) -> QColor:
    window = application.palette().color(QPalette.ColorRole.Window)
    if window.lightness() < 128:
        return QColor("#7ab8ff")
    return QColor("#0057d4")


def _html(application: QApplication) -> str:
    text_color = application.palette().color(QPalette.ColorRole.WindowText).name()
    link = _link_color(application).name()
    muted = text_color
    return (
        "<div style='color:{text}'>"
        f"<h1 style='margin:0 0 4px 0; font-size:26pt;'>TBO</h1>"
        f"<p style='margin:0 0 12px 0; font-size:11pt;'><b>Version {__version__}</b></p>"
        f"<p style='margin:0 0 14px 0; font-size:10.5pt;'>A modern comic editor "
        f"compatible with legacy TBO documents.</p>"
        f"<h2 style='margin:10px 0 4px 0; font-size:12pt;'>PyQt6 port by</h2>"
        f"<p style='margin:0 0 12px 0; font-size:10.5pt;'>"
        f"<b>Washington Indacochea Delgado</b><br>"
        f"<a href='mailto:{EMAIL}' style='color:{link}; text-decoration:underline;'>"
        f"{EMAIL}</a><br>"
        f"<a href='{REPOSITORY}' style='color:{link}; text-decoration:underline;'>"
        f"{REPOSITORY}</a></p>"
        f"<h2 style='margin:10px 0 4px 0; font-size:12pt;'>Original TBO (C/GTK)</h2>"
        f"<p style='margin:0 0 12px 0; font-size:10.5pt;'>Daniel Garcia Moreno</p>"
        f"<h2 style='margin:10px 0 4px 0; font-size:12pt;'>Art</h2>"
        f"<p style='margin:0 0 4px 0; font-size:10.5pt;'>Daniel Garcia Moreno</p>"
        f"<p style='margin:0 0 12px 0; font-size:10.5pt;'>Arcadia Project "
        f"(Samuel Navas Portillo, Daniel Pavón Pérez, Juan Jesús Pérez Luna)</p>"
        f"<p style='margin:0 0 12px 0; font-size:10.5pt;'>and TBO contributors.</p>"
        f"<p style='margin:0; font-size:10pt;'>{muted}License: GPL-3.0-or-later</p>"
        "</div>"
    )


class AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("About TBO"))
        self.setModal(True)
        self.resize(680, 420)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = _logo_pixmap()
        if not pixmap.isNull():
            logo.setPixmap(pixmap)
            logo.setFixedWidth(LOGO_SIZE + 20)
        logo.setStyleSheet("background-color: transparent;")

        application = QApplication.instance()
        text_label = QLabel()
        text_label.setTextFormat(Qt.TextFormat.RichText)
        text_label.setText(_html(application))
        text_label.setOpenExternalLinks(True)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        text_label.setStyleSheet("background-color: transparent;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(text_label, 1)
