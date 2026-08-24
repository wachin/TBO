from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QLocale, QLibraryInfo, QTranslator, Qt
from PyQt6.QtWidgets import QApplication

from tbo.resources import find_asset_root
from tbo.ui.main_window import MainWindow
from tbo.ui.preferences import Preferences

TRANSLATION_DIRS = (
    Path(__file__).resolve().parent.parent / "translations",
    Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)),
)


def _install_translator() -> None:
    """Install the Qt and application translators for the active locale."""
    preferences = Preferences()
    locale_name = preferences.locale()
    locale = QLocale(locale_name)
    QLocale.setDefault(locale)

    application_translator = QTranslator()
    for directory in TRANSLATION_DIRS:
        if application_translator.load(locale, "tbo", "_", str(directory), ".qm"):
            QCoreApplication.installTranslator(application_translator)
            break

    qt_translator = QTranslator()
    if qt_translator.load(locale, "qtbase", "_", str(TRANSLATION_DIRS[1])):
        QCoreApplication.installTranslator(qt_translator)


def main(argv: list[str] | None = None) -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    arguments = list(sys.argv if argv is None else argv)
    application = QApplication(arguments)
    _install_translator()

    window = MainWindow(asset_root=find_asset_root())
    if len(arguments) > 1:
        window.open_document(Path(arguments[1]))
    else:
        window.new_document(QCoreApplication.translate("Application", "Untitled"), 800, 450)
    window.show()
    return application.exec()
