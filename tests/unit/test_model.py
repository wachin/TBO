import pytest

from tbo.document.model import Color, Comic, DocumentValidationError, Frame


def test_model_accepts_legacy_coordinates() -> None:
    comic = Comic("example", 800, 450)
    frame = Frame(-10, -20, 200, 100, color=Color(0.1, 0.2, 0.3))

    assert comic.width == 800
    assert frame.x == -10


@pytest.mark.parametrize("value", [0, -1])
def test_comic_rejects_invalid_dimensions(value: int) -> None:
    with pytest.raises(DocumentValidationError):
        Comic("example", value, 450)


def test_color_rejects_out_of_range_component() -> None:
    with pytest.raises(DocumentValidationError):
        Color(1.1, 0.0, 0.0)

