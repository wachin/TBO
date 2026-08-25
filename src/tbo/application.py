from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QLibraryInfo, QLocale, Qt, QTranslator
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from tbo.resources import find_asset_root, find_icon
from tbo.ui.main_window import MainWindow
from tbo.ui.preferences import Preferences
from tbo.ui.theme import apply_theme

_package_dir = Path(__file__).resolve().parent
TRANSLATION_DIRS = (
    _package_dir / "translations",
    _package_dir.parent.parent / "translations",
    Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)),
)

_APP_TRANSLATOR = QTranslator()
_QT_TRANSLATOR = QTranslator()


def _install_translator(locale_override: str | None = None) -> None:
    """Install the Qt and application translators for the active locale."""
    preferences = Preferences()
    locale_name = locale_override or preferences.locale()
    locale = QLocale.system() if not locale_name or locale_name == "auto" else QLocale(locale_name)
    QLocale.setDefault(locale)

    global _APP_TRANSLATOR, _QT_TRANSLATOR
    for directory in TRANSLATION_DIRS:
        if _APP_TRANSLATOR.load(locale, "tbo", "_", str(directory), ".qm"):
            QCoreApplication.installTranslator(_APP_TRANSLATOR)
            break

    if _QT_TRANSLATOR.load(locale, "qtbase", "_", str(TRANSLATION_DIRS[2])):
        QCoreApplication.installTranslator(_QT_TRANSLATOR)


def _parse_language(arguments: list[str]) -> tuple[str | None, list[str]]:
    override: str | None = None
    clean: list[str] = []
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument in ("--lang", "--language") and index + 1 < len(arguments):
            override = arguments[index + 1]
            index += 2
            continue
        clean.append(argument)
        index += 1
    return override, clean


def main(argv: list[str] | None = None) -> int:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    arguments = list(sys.argv if argv is None else argv)
    language, arguments = _parse_language(arguments)
    application = QApplication(arguments)
    _install_translator(language)
    apply_theme(application, Preferences().theme())

    window = MainWindow(asset_root=find_asset_root())
    icon_path = find_icon()
    if icon_path is not None:
        icon = QIcon(str(icon_path))
        application.setWindowIcon(icon)
        window.setWindowIcon(icon)
    if len(arguments) > 1:
        window.open_document(Path(arguments[1]))
    else:
        last = Preferences().last_filename()
        if last is not None:
            window.open_document(last)
        else:
            window.new_document(QCoreApplication.translate("Application", "Untitled"), 800, 450)
    window.show()
    return application.exec()
