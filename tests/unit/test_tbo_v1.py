from pathlib import Path

import pytest

from tbo.document.model import SvgObject, TextObject
from tbo.formats.tbo_v1 import TboFormatError, dumps, load, loads, save


TUTORIAL = Path(__file__).parents[2] / "data" / "tut.tbo"


def test_loads_historical_tutorial() -> None:
    comic = load(TUTORIAL)

    assert comic.title == "tut"
    assert (comic.width, comic.height) == (800, 450)
    assert len(comic.pages) == 11
    assert comic.pages[0].frames[0].color.red == 1.0
    assert isinstance(comic.pages[0].frames[0].objects[0], SvgObject)
    text = comic.pages[0].frames[0].objects[1]
    assert isinstance(text, TextObject)
    assert text.text == "Tutorial"


def test_accepts_comma_and_dot_decimal_separators() -> None:
    comic = loads(
        b'<tbo width="10" height="20"><page><frame x="0" y="0" '
        b'width="10" height="20" r="0,5" g="0.25" b="1"/></page></tbo>'
    )

    assert comic.pages[0].frames[0].color.red == 0.5
    assert comic.pages[0].frames[0].color.green == 0.25


@pytest.mark.parametrize(
    "xml",
    [
        b"<wrong />",
        b'<tbo width="0" height="10" />',
        b'<tbo width="10" height="10"><frame /></tbo>',
        b'<!DOCTYPE tbo [<!ENTITY x "boom">]><tbo width="10" height="10" />',
        b'<tbo width="10" height="10"><page><frame x="0" y="0" width="1" '
        b'height="1"><unknown x="0" y="0" width="1" height="1"/></frame></page></tbo>',
    ],
)
def test_rejects_invalid_documents(xml: bytes) -> None:
    with pytest.raises(TboFormatError):
        loads(xml)


def test_rejects_non_finite_numbers() -> None:
    xml = (
        b'<tbo width="10" height="10"><page><frame x="0" y="0" width="1" '
        b'height="1"><svgimage x="0" y="0" width="1" height="1" angle="nan" '
        b'path="asset.svg"/></frame></page></tbo>'
    )
    with pytest.raises(TboFormatError, match="finite"):
        loads(xml)


def test_tutorial_round_trip_preserves_document() -> None:
    original = load(TUTORIAL)

    serialized = dumps(original)
    restored = loads(serialized, title=original.title)

    assert restored == original
    assert b'r="1.000000"' in serialized
    assert b"1,000000" not in serialized


def test_save_replaces_existing_file_atomically(tmp_path: Path) -> None:
    target = tmp_path / "comic.tbo"
    target.write_text("old contents", encoding="utf-8")
    comic = load(TUTORIAL)

    save(comic, target)

    restored = load(target)
    assert restored.title == "comic"
    assert restored.width == comic.width
    assert restored.height == comic.height
    assert restored.pages == comic.pages
    assert not list(tmp_path.glob(".comic.tbo.*.tmp"))


def test_save_does_not_touch_target_when_serialization_fails(tmp_path: Path) -> None:
    target = tmp_path / "comic.tbo"
    target.write_text("original", encoding="utf-8")
    comic = load(TUTORIAL)
    comic.width = 0

    with pytest.raises(TboFormatError):
        save(comic, target)

    assert target.read_text(encoding="utf-8") == "original"


def test_save_cleans_temporary_file_when_replace_fails(tmp_path: Path, monkeypatch) -> None:
    target = tmp_path / "comic.tbo"
    target.write_text("original", encoding="utf-8")
    comic = load(TUTORIAL)

    def fail_replace(source, destination) -> None:
        raise OSError("simulated replacement failure")

    monkeypatch.setattr("tbo.formats.tbo_v1.os.replace", fail_replace)

    with pytest.raises(TboFormatError, match="simulated replacement failure"):
        save(comic, target)

    assert target.read_text(encoding="utf-8") == "original"
    assert not list(tmp_path.glob(".comic.tbo.*.tmp"))
