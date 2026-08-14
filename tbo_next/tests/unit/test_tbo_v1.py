from pathlib import Path

import pytest

from tbo.document.model import SvgObject, TextObject
from tbo.formats.tbo_v1 import TboFormatError, loads


TUTORIAL = Path(__file__).parents[3] / "data" / "tut.tbo"


def test_loads_historical_tutorial() -> None:
    from tbo.formats.tbo_v1 import load

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

