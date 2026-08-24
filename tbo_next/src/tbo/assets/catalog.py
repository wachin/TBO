from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AssetEntry:
    name: str
    path: Path
    category: str


@dataclass(slots=True)
class AssetCategory:
    name: str
    entries: list[AssetEntry]


class AssetCatalog:
    """Index of SVG doodles and speech bubbles found on disk.

    The legacy application grouped assets by directory under a ``doodle`` root.
    Speech bubbles live in a ``bubble`` subtree and are exposed separately so the
    user can tell decorative doodles apart from text containers. Each bubble
    subdirectory (``square``, ``ellipse``, …) becomes its own category.
    """

    def __init__(self, root: Path) -> None:
        self._root = root
        self._doodle_categories: list[AssetCategory] = []
        self._bubble_categories: list[AssetCategory] = []
        self._scan()

    @property
    def root(self) -> Path:
        return self._root

    @property
    def doodle_categories(self) -> list[AssetCategory]:
        return self._doodle_categories

    @property
    def bubble_categories(self) -> list[AssetCategory]:
        return self._bubble_categories

    def entries(self, *, bubbles: bool) -> list[AssetEntry]:
        categories = self._bubble_categories if bubbles else self._doodle_categories
        result: list[AssetEntry] = []
        for category in categories:
            result.extend(category.entries)
        return result

    def search(self, query: str, *, bubbles: bool) -> list[AssetEntry]:
        normalized = query.strip().lower()
        return [
            entry
            for entry in self.entries(bubbles=bubbles)
            if normalized in entry.name.lower() or normalized in entry.category.lower()
        ]

    def _scan(self) -> None:
        if not self._root.is_dir():
            return
        bubble_root = self._root / "bubble"
        for directory in sorted(self._root.iterdir()):
            if not directory.is_dir() or directory == bubble_root:
                continue
            category = self._category_from(directory)
            if category is not None:
                self._doodle_categories.append(category)
        if bubble_root.is_dir():
            subdirectories = sorted(
                child for child in bubble_root.iterdir() if child.is_dir()
            )
            if subdirectories:
                for subdirectory in subdirectories:
                    category = self._category_from(subdirectory, prefix=f"bubble/{subdirectory.name}")
                    if category is not None:
                        self._bubble_categories.append(category)
            else:
                category = self._category_from(bubble_root, prefix="bubble")
                if category is not None:
                    self._bubble_categories.append(category)

    def _category_from(self, directory: Path, prefix: str = "") -> AssetCategory | None:
        entries: list[AssetEntry] = []
        for path in sorted(directory.rglob("*.svg")):
            if not path.is_file():
                continue
            category_name = prefix or directory.name
            entries.append(AssetEntry(name=path.stem, path=path, category=category_name))
        if not entries:
            return None
        display_name = prefix.rsplit("/", 1)[-1] if prefix else directory.name
        return AssetCategory(name=display_name, entries=entries)
