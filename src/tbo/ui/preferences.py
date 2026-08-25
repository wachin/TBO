from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QByteArray, QSettings

MAX_RECENT_FILES = 8


class Preferences:
    """Application preferences persisted with ``QSettings``.

    Configuration is stored separately from documents and never mixed into the
    ``.tbo`` files themselves.
    """

    def __init__(self, settings: QSettings | None = None) -> None:
        self._settings = settings if settings is not None else QSettings("TBO", "TBO 2")

    def window_geometry(self) -> QByteArray | None:
        value = self._settings.value("ui/windowGeometry")
        return value if isinstance(value, QByteArray) and not value.isEmpty() else None

    def set_window_geometry(self, geometry: QByteArray) -> None:
        self._settings.setValue("ui/windowGeometry", geometry)

    def last_directory(self) -> Path | None:
        value = self._settings.value("ui/lastDirectory")
        if not isinstance(value, str) or not value:
            return None
        path = Path(value)
        return path if path.is_dir() else None

    def set_last_directory(self, directory: Path) -> None:
        self._settings.setValue("ui/lastDirectory", str(directory))

    def recent_files(self) -> list[Path]:
        value = self._settings.value("recentFiles")
        if value is None:
            return []
        if not isinstance(value, list):
            value = [value]
        paths: list[Path] = []
        for item in value:
            if isinstance(item, str) and item:
                paths.append(Path(item))
        return paths

    def add_recent_file(self, filename: Path) -> None:
        current = [str(path) for path in self.recent_files() if path != filename]
        current.insert(0, str(filename))
        self._settings.setValue("recentFiles", current[:MAX_RECENT_FILES])

    def remove_recent_file(self, filename: Path) -> None:
        current = [str(path) for path in self.recent_files() if path != filename]
        self._settings.setValue("recentFiles", current)

    def locale(self) -> str:
        value = self._settings.value("locale")
        return value if isinstance(value, str) and value else ""

    def set_locale(self, locale: str) -> None:
        self._settings.setValue("locale", locale)

    def theme(self) -> str:
        value = self._settings.value("theme")
        return value if value in {"system", "dark", "light"} else "system"

    def set_theme(self, mode: str) -> None:
        if mode in {"system", "dark", "light"}:
            self._settings.setValue("theme", mode)

    def last_filename(self) -> Path | None:
        value = self._settings.value("session/lastFilename")
        if not isinstance(value, str) or not value:
            return None
        path = Path(value)
        return path if path.is_file() else None

    def set_last_filename(self, filename: Path | None) -> None:
        if filename is not None:
            self._settings.setValue("session/lastFilename", str(filename))

    def snap_to_grid(self) -> bool:
        return self._settings.value("view/snapToGrid", False) in (True, "true")

    def set_snap_to_grid(self, enabled: bool) -> None:
        self._settings.setValue("view/snapToGrid", bool(enabled))
