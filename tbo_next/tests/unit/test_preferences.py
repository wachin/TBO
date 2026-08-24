from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSettings

from tbo.ui.preferences import MAX_RECENT_FILES, Preferences


def _fresh_preferences(tmp_path: Path) -> Preferences:
    settings = QSettings(str(tmp_path / "config.ini"), QSettings.Format.IniFormat)
    return Preferences(settings)


def test_recent_files_round_trip(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    preferences.add_recent_file(Path("/one/a.tbo"))
    preferences.add_recent_file(Path("/two/b.tbo"))
    assert preferences.recent_files() == [Path("/two/b.tbo"), Path("/one/a.tbo")]


def test_recent_files_deduplicate_and_keep_order(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    preferences.add_recent_file(Path("/one/a.tbo"))
    preferences.add_recent_file(Path("/two/b.tbo"))
    preferences.add_recent_file(Path("/one/a.tbo"))
    assert preferences.recent_files() == [Path("/one/a.tbo"), Path("/two/b.tbo")]


def test_recent_files_remove(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    preferences.add_recent_file(Path("/one/a.tbo"))
    preferences.remove_recent_file(Path("/one/a.tbo"))
    assert preferences.recent_files() == []


def test_recent_files_limited(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    for index in range(MAX_RECENT_FILES + 5):
        preferences.add_recent_file(Path(f"/dir/{index}.tbo"))
    assert len(preferences.recent_files()) == MAX_RECENT_FILES
    assert preferences.recent_files()[0] == Path(f"/dir/{MAX_RECENT_FILES + 4}.tbo")


def test_last_directory_persisted(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    assert preferences.last_directory() is None
    directory = tmp_path / "docs"
    directory.mkdir()
    preferences.set_last_directory(directory)
    assert preferences.last_directory() == directory


def test_last_directory_ignores_missing_path(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    preferences.set_last_directory(tmp_path / "missing")
    assert preferences.last_directory() is None


def test_locale_default_and_persisted(monkeypatch, tmp_path: Path) -> None:
    preferences = _fresh_preferences(tmp_path)
    assert preferences.locale() == "en"
    fresh = _fresh_preferences(tmp_path)
    fresh._settings.setValue("locale", "es")
    assert fresh.locale() == "es"
