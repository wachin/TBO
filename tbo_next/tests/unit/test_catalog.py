from pathlib import Path

from tbo.assets import AssetCatalog, resolve_asset
from tbo.assets.catalog import AssetCategory, AssetEntry

REPOSITORY_ROOT = Path(__file__).parents[3]
DOODLE_ROOT = REPOSITORY_ROOT / "data" / "doodle"


def test_catalog_indexes_doodle_and_bubble_categories() -> None:
    catalog = AssetCatalog(DOODLE_ROOT)
    doodle_names = {category.name for category in catalog.doodle_categories}
    assert "eyes" in doodle_names
    assert "mouth" in doodle_names
    assert "ears" in doodle_names
    assert "head" in doodle_names
    assert "bubble" not in doodle_names
    bubble_names = {category.name for category in catalog.bubble_categories}
    assert "square" in bubble_names
    assert "ellipse" in bubble_names


def test_catalog_counts_assets() -> None:
    catalog = AssetCatalog(DOODLE_ROOT)
    assert len(catalog.entries(bubbles=False)) >= 100
    assert len(catalog.entries(bubbles=True)) >= 10


def test_catalog_character_head_has_face_parts() -> None:
    catalog = AssetCatalog(DOODLE_ROOT)
    head = next(
        (category for category in catalog.doodle_categories if category.name == "head"),
        None,
    )
    assert head is not None
    assert any(entry.name == "head" for entry in head.entries)
    parts = {category.name: len(category.entries) for category in catalog.doodle_categories}
    assert parts.get("eyes", 0) >= 1
    assert parts.get("mouth", 0) >= 1
    assert parts.get("ears", 0) >= 1


def test_catalog_search_filters_by_name_and_category() -> None:
    catalog = AssetCatalog(DOODLE_ROOT)
    eyes = catalog.search("eyes", bubbles=False)
    assert eyes
    assert all("eyes" in entry.name or "eyes" in entry.category for entry in eyes)
    squares = catalog.search("square", bubbles=True)
    assert squares
    assert all(entry.category.startswith("bubble/") for entry in squares)


def test_catalog_entries_have_absolute_existing_paths() -> None:
    catalog = AssetCatalog(DOODLE_ROOT)
    for entry in catalog.entries(bubbles=True):
        assert isinstance(entry, AssetEntry)
        assert entry.path.is_file()


def test_catalog_missing_root_is_empty() -> None:
    catalog = AssetCatalog(DOODLE_ROOT / "does-not-exist")
    assert catalog.doodle_categories == []
    assert catalog.bubble_categories == []
    assert catalog.entries(bubbles=False) == []
    assert catalog.entries(bubbles=True) == []


def test_resolve_asset_does_not_escape_root(tmp_path: Path) -> None:
    (tmp_path / "asset.svg").write_text("<svg/>", encoding="utf-8")
    assert resolve_asset(Path("asset.svg"), roots=[tmp_path]) == tmp_path / "asset.svg"
    assert resolve_asset(Path("../outside.svg"), roots=[tmp_path]) is None


def test_resolve_asset_absolute_existing_path_is_honored() -> None:
    entry = AssetCatalog(DOODLE_ROOT).entries(bubbles=True)[0]
    assert resolve_asset(entry.path, roots=[DOODLE_ROOT]) == entry.path
