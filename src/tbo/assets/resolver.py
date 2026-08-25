from __future__ import annotations

from pathlib import Path


def resolve_asset(asset_path: Path, *, roots: list[Path]) -> Path | None:
    """Locate an asset without allowing directory traversal outside the roots.

    Absolute paths are only honored when the file exists (historical documents
    embed absolute locations). Relative paths are searched under each provided
    root in order. The lookup never escapes the supplied roots for relative
    references.
    """
    if asset_path.is_absolute():
        return asset_path if asset_path.is_file() else None
    normalized = asset_path
    for root in roots:
        candidate = (root / normalized).resolve()
        if root.resolve() in candidate.parents and candidate.is_file():
            return candidate
    return None
