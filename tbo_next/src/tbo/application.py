from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from tbo.ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv if argv is None else argv)
    application = QApplication(arguments)

    repository_root = Path(__file__).resolve().parents[3]
    asset_root = repository_root / "data" / "doodle"
    window = MainWindow(asset_root=asset_root if asset_root.is_dir() else None)
    if len(arguments) > 1:
        window.open_document(Path(arguments[1]))
    else:
        window.new_document(QCoreApplication.translate("Application", "Untitled"), 800, 450)
    window.show()
    return application.exec()
