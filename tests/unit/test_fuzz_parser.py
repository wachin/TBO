from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tbo.document.model import (
    Color,
    Comic,
    Frame,
    GraphicObject,
    ImageObject,
    Page,
    SvgObject,
    TextObject,
)
from tbo.formats.tbo_v1 import TboFormatError, dumps, loads

FIXTURES = Path(__file__).parents[1] / "fixtures"


def _object_round_trip(data: bytes) -> tuple[Comic, Comic]:
    first = loads(data, title="fixture")
    second = loads(dumps(first), title="fixture")
    return first, second


def _assert_comic_equivalent(first: Comic, second: Comic) -> None:
    assert first.title == second.title
    assert (first.width, first.height) == (second.width, second.height)
    assert len(first.pages) == len(second.pages)
    for first_page, second_page in zip(first.pages, second.pages):
        assert len(first_page.frames) == len(second_page.frames)
        for first_frame, second_frame in zip(first_page.frames, second_page.frames):
            assert (first_frame.x, first_frame.y) == (second_frame.x, second_frame.y)
            assert (first_frame.width, first_frame.height) == (
                second_frame.width,
                second_frame.height,
            )
            assert first_frame.border == second_frame.border
            assert len(first_frame.objects) == len(second_frame.objects)
            for first_obj, second_obj in zip(first_frame.objects, second_frame.objects):
                assert type(first_obj) is type(second_obj)
                assert (first_obj.x, first_obj.y) == (second_obj.x, second_obj.y)
                assert (first_obj.width, first_obj.height) == (
                    second_obj.width,
                    second_obj.height,
                )
                assert first_obj.angle == second_obj.angle
                assert first_obj.flip_horizontal == second_obj.flip_horizontal
                assert first_obj.flip_vertical == second_obj.flip_vertical
                if isinstance(first_obj, TextObject):
                    assert first_obj.text == second_obj.text
                    assert first_obj.font == second_obj.font
                    assert first_obj.color == second_obj.color
                elif isinstance(first_obj, (SvgObject, ImageObject)):
                    assert first_obj.path == second_obj.path


def test_round_trip_preserves_fixtures() -> None:
    for fixture in FIXTURES.glob("*.tbo"):
        data = fixture.read_bytes()
        first, second = _object_round_trip(data)
        _assert_comic_equivalent(first, second)


@settings(max_examples=50, deadline=None)
@given(st.binary(max_size=20_000))
def test_loads_never_crashes_on_arbitrary_bytes(data: bytes) -> None:
    try:
        comic = loads(data, title="fuzz")
    except TboFormatError:
        return
    assert isinstance(comic, Comic)


@settings(max_examples=50, deadline=None)
@given(
    st.integers(min_value=1, max_value=2000),
    st.integers(min_value=1, max_value=2000),
)
def test_round_trip_generated_comic(width: int, height: int) -> None:
    comic = Comic("Generated", width, height, [Page()])
    frame = Frame(x=10, y=10, width=max(1, width - 20), height=max(1, height - 20))
    frame.objects.append(TextObject(x=10, y=10, width=50, height=20, text="Hi", font="Sans 12"))
    comic.pages[0].frames.append(frame)
    first, second = _object_round_trip(dumps(comic))
    _assert_comic_equivalent(first, second)


_VALID_XML_CHARS = st.characters(
    min_codepoint=0x20,
    max_codepoint=0xD7FF,
    whitelist_categories=("L", "N", "P", "S", "Z", "M", "Cc"),
)



@settings(max_examples=20, deadline=None)
@given(
    st.lists(
        st.text(alphabet=_VALID_XML_CHARS, min_size=1, max_size=80),
        min_size=1,
        max_size=5,
    ),
    st.text(alphabet=_VALID_XML_CHARS, min_size=1, max_size=80),
)
def test_round_trip_arbitrary_texts(lines: list[str], font: str) -> None:
    comic = Comic("Text", 300, 200, [Page()])
    frame = Frame(x=10, y=10, width=200, height=150)
    text = "\n".join(lines)
    frame.objects.append(TextObject(x=10, y=10, width=180, height=120, text=text, font=font))
    comic.pages[0].frames.append(frame)
    first, second = _object_round_trip(dumps(comic))
    _assert_comic_equivalent(first, second)


def test_fixtures_are_valid_and_load() -> None:
    assert FIXTURES.is_dir()
    fixtures = list(FIXTURES.glob("*.tbo"))
    assert len(fixtures) >= 3
    for fixture in fixtures:
        comic = loads(fixture.read_bytes(), title=fixture.stem)
        assert comic.title
        assert comic.width > 0 and comic.height > 0
