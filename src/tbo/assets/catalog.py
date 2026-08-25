from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class AssetEntry:
    name: str
    path: Path
    category: str


@dataclass(slots=True)
class AssetCategory:
    name: str
    entries: list[AssetEntry] = field(default_factory=list)
    base_dir: Path | None = None


class AssetCatalog:
    """Index of SVG doodles and speech bubbles found on disk.

    Assets are scanned from one or more roots. The application ships a system
    tree (``data/doodle``), and the user can extend it by placing their own SVG
    files in a user data directory; categories with the same name are merged so
    user drawings appear alongside the shipped ones.

    Speech bubbles live in a ``bubble`` subtree and are exposed separately so the
    user can tell decorative doodles apart from text containers. Each bubble
    subdirectory (``square``, ``ellipse``, …) becomes its own category.
    """

    def __init__(self, roots: Path | list[Path]) -> None:
        if isinstance(roots, Path):
            roots = [roots]
        self._roots = [Path(root) for root in roots]
        self._doodle_categories: list[AssetCategory] = []
        self._bubble_categories: list[AssetCategory] = []
        self._scan()

    @property
    def roots(self) -> list[Path]:
        return self._roots

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
        for root in self._roots:
            self._scan_root(root)

    def _scan_root(self, root: Path) -> None:
        if not root.is_dir():
            return
        bubble_root = root / "bubble"
        for directory in sorted(root.iterdir()):
            if not directory.is_dir() or directory == bubble_root:
                continue
            category = self._category_from(directory)
            if category is not None:
                self._merge(self._doodle_categories, category)
        if bubble_root.is_dir():
            subdirectories = sorted(child for child in bubble_root.iterdir() if child.is_dir())
            if subdirectories:
                for subdirectory in subdirectories:
                    category = self._category_from(
                        subdirectory, prefix=f"bubble/{subdirectory.name}"
                    )
                    if category is not None:
                        self._merge(self._bubble_categories, category)
            else:
                category = self._category_from(bubble_root, prefix="bubble")
                if category is not None:
                    self._merge(self._bubble_categories, category)

    def _merge(self, categories: list[AssetCategory], category: AssetCategory) -> None:
        for existing in categories:
            if existing.name == category.name:
                existing.entries.extend(category.entries)
                return
        categories.append(category)

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
        return AssetCategory(name=display_name, entries=entries, base_dir=directory)

    def split_by_subdirectory(self, category: AssetCategory) -> list[AssetCategory]:
        """Split a flat category into subcategories by immediate subdirectory.

        Used to expose separately-organized parts (e.g. the character's eyes,
        mouth and ears) while keeping the original top-level grouping intact.
        """
        groups: dict[str, list[AssetEntry]] = {}
        for entry in category.entries:
            part = self._category_part(entry, category.name)
            groups.setdefault(part, []).append(entry)
        result: list[AssetCategory] = []
        for part in sorted(groups):
            result.append(
                AssetCategory(
                    name=part,
                    entries=[
                        AssetEntry(
                            name=entry.name,
                            path=entry.path,
                            category=f"{category.name}/{part}",
                        )
                        for entry in groups[part]
                    ],
                )
            )
        return result

    @staticmethod
    def _category_part(entry: AssetEntry, category_name: str) -> str:
        parts = entry.path.parent.parts
        for index, part in enumerate(parts):
            if part == category_name:
                return parts[index + 1] if index + 1 < len(parts) else category_name
        return category_name
