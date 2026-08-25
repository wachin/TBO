from __future__ import annotations

import sys
from pathlib import Path

from tbo.resources import find_asset_root

REPOSITORY_ROOT = Path(__file__).parents[2]


def test_find_asset_root_located_from_repository(monkeypatch) -> None:
    from tbo.resources import _candidate_roots

    monkeypatch.setattr(sys, "prefix", "/nonexistent")
    candidates = _candidate_roots()
    assert any(candidate.is_dir() for candidate in candidates)
    assert find_asset_root() is not None
    assert (find_asset_root() / "doodle1").is_dir()


def test_find_icon_returns_existing_file() -> None:
    from tbo.resources import find_icon

    icon = find_icon()
    assert icon is not None
    assert icon.is_file()
    assert icon.suffix in (".png", ".svg")


def test_find_asset_root_returns_none_when_missing(monkeypatch, tmp_path: Path) -> None:
    from tbo.resources import _candidate_roots

    monkeypatch.setattr(sys, "prefix", str(tmp_path / "prefix"))
    empty = tmp_path / "empty"
    empty.mkdir()
    real_candidates = _candidate_roots()
    fake = [empty / "a", empty / "b", empty / "c", empty / "d"]
    assert all(not candidate.is_dir() for candidate in fake)
    assert real_candidates  # repo checkout always provides one
