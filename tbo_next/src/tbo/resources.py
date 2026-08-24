from __future__ import annotations

import sys
from pathlib import Path


def _candidate_roots() -> list[Path]:
    package_dir = Path(__file__).resolve().parent
    repository_root = package_dir.parents[2]
    return [
        package_dir.parent / "data" / "doodle",
        package_dir / "data" / "doodle",
        repository_root / "data" / "doodle",
        Path(sys.prefix) / "share" / "tbo" / "doodle",
    ]


def find_asset_root() -> Path | None:
    """Locate the shipped doodle/bubble assets.

    Returns the first existing directory among the development checkout, the
    installed package data, and the system data location. ``None`` means the
    assets are not available and the asset library must be hidden.
    """
    for candidate in _candidate_roots():
        if candidate.is_dir():
            return candidate
    return None


def find_icon() -> Path | None:
    """Locate the application icon bundled with the package.

    Prefers the PNG for window/taskbar use; the SVG is returned when the PNG
    is not shipped.
    """
    resources_dir = Path(__file__).resolve().parent / "resources"
    for name in ("icon.png", "icon.svg"):
        candidate = resources_dir / name
        if candidate.is_file():
            return candidate
    return None
