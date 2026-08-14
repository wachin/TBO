from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

from tbo.document.model import (
    Color,
    Comic,
    DocumentValidationError,
    Frame,
    GraphicObject,
    ImageObject,
    Page,
    SvgObject,
    TextObject,
)

MAX_FILE_SIZE = 16 * 1024 * 1024
MAX_PAGES = 1_000
MAX_FRAMES_PER_PAGE = 10_000
MAX_OBJECTS_PER_FRAME = 100_000
MAX_TEXT_LENGTH = 1_000_000
MAX_PATH_LENGTH = 4_096
MAX_DIMENSION = 1_000_000


class TboFormatError(ValueError):
    """A legacy TBO file is malformed or exceeds a safety limit."""


def load(filename: str | Path) -> Comic:
    path = Path(filename)
    try:
        data = path.read_bytes()
    except OSError as error:
        raise TboFormatError(f"Could not read {path}: {error}") from error

    return loads(data, title=path.stem)


def loads(data: bytes, *, title: str = "Untitled") -> Comic:
    if len(data) > MAX_FILE_SIZE:
        raise TboFormatError(f"Document exceeds the {MAX_FILE_SIZE}-byte limit")

    lowered = data.lower()
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise TboFormatError("DTD and entity declarations are not allowed")

    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise TboFormatError(f"Invalid XML: {error}") from error

    if root.tag != "tbo":
        raise TboFormatError("Root element must be <tbo>")

    try:
        comic = Comic(
            title=title,
            width=_dimension(root, "width"),
            height=_dimension(root, "height"),
        )
        for page_index, page_element in enumerate(root):
            if page_element.tag != "page":
                raise TboFormatError(f"Unexpected <{page_element.tag}> inside <tbo>")
            if page_index >= MAX_PAGES:
                raise TboFormatError(f"Document contains more than {MAX_PAGES} pages")
            comic.pages.append(_parse_page(page_element, page_index))
    except (DocumentValidationError, ValueError) as error:
        if isinstance(error, TboFormatError):
            raise
        raise TboFormatError(str(error)) from error

    return comic


def _parse_page(element: ET.Element, page_index: int) -> Page:
    page = Page()
    for frame_index, frame_element in enumerate(element):
        if frame_element.tag != "frame":
            raise TboFormatError(
                f"Unexpected <{frame_element.tag}> inside page {page_index + 1}"
            )
        if frame_index >= MAX_FRAMES_PER_PAGE:
            raise TboFormatError(f"Page {page_index + 1} contains too many frames")
        page.frames.append(_parse_frame(frame_element, page_index, frame_index))
    return page


def _parse_frame(element: ET.Element, page_index: int, frame_index: int) -> Frame:
    context = f"page {page_index + 1}, frame {frame_index + 1}"
    frame = Frame(
        x=_integer(element, "x", context),
        y=_integer(element, "y", context),
        width=_dimension(element, "width", context),
        height=_dimension(element, "height", context),
        border=_boolean(element, "border", context, default=True),
        color=_color(element, context, default=1.0),
    )
    for object_index, object_element in enumerate(element):
        if object_index >= MAX_OBJECTS_PER_FRAME:
            raise TboFormatError(f"{context} contains too many objects")
        frame.objects.append(_parse_object(object_element, context, object_index))
    return frame


def _parse_object(element: ET.Element, frame_context: str, object_index: int) -> GraphicObject:
    context = f"{frame_context}, object {object_index + 1}"
    common: dict[str, object] = {
        "x": _integer(element, "x", context),
        "y": _integer(element, "y", context),
        "width": _dimension(element, "width", context),
        "height": _dimension(element, "height", context),
        "angle": _number(element, "angle", context, default=0.0),
        "flip_vertical": _boolean(element, "flipv", context, default=False),
        "flip_horizontal": _boolean(element, "fliph", context, default=False),
    }

    if element.tag == "text":
        value = (element.text or "").strip()
        if not value:
            raise TboFormatError(f"{context}: text object is empty")
        if len(value) > MAX_TEXT_LENGTH:
            raise TboFormatError(f"{context}: text exceeds the length limit")
        return TextObject(
            **common,
            text=value,
            font=_string(element, "font", context, default="Sans 12"),
            color=_color(element, context, default=0.0),
        )
    if element.tag in {"svgimage", "piximage"}:
        asset_path = Path(_string(element, "path", context))
        object_type = SvgObject if element.tag == "svgimage" else ImageObject
        return object_type(**common, path=asset_path)

    raise TboFormatError(f"{context}: unsupported element <{element.tag}>")


def _raw(element: ET.Element, name: str, context: str) -> str:
    value = element.get(name)
    if value is None:
        raise TboFormatError(f"{context}: missing attribute {name!r}")
    return value


def _string(
    element: ET.Element, name: str, context: str, *, default: str | None = None
) -> str:
    value = element.get(name, default)
    if value is None:
        raise TboFormatError(f"{context}: missing attribute {name!r}")
    if not value:
        raise TboFormatError(f"{context}: attribute {name!r} must not be empty")
    if len(value) > MAX_PATH_LENGTH:
        raise TboFormatError(f"{context}: attribute {name!r} is too long")
    return value


def _integer(element: ET.Element, name: str, context: str = "document") -> int:
    raw = _raw(element, name, context)
    try:
        return int(raw)
    except ValueError as error:
        raise TboFormatError(f"{context}: {name!r} must be an integer") from error


def _dimension(element: ET.Element, name: str, context: str = "document") -> int:
    value = _integer(element, name, context)
    if not 0 < value <= MAX_DIMENSION:
        raise TboFormatError(f"{context}: {name!r} must be between 1 and {MAX_DIMENSION}")
    return value


def _number(
    element: ET.Element, name: str, context: str, *, default: float | None = None
) -> float:
    raw = element.get(name)
    if raw is None:
        if default is None:
            raise TboFormatError(f"{context}: missing attribute {name!r}")
        return default
    try:
        value = float(raw.replace(",", "."))
    except ValueError as error:
        raise TboFormatError(f"{context}: {name!r} must be a number") from error
    if not math.isfinite(value):
        raise TboFormatError(f"{context}: {name!r} must be finite")
    return value


def _boolean(
    element: ET.Element, name: str, context: str, *, default: bool
) -> bool:
    raw = element.get(name)
    if raw is None:
        return default
    if raw not in {"0", "1"}:
        raise TboFormatError(f"{context}: {name!r} must be 0 or 1")
    return raw == "1"


def _color(element: ET.Element, context: str, *, default: float) -> Color:
    values = [
        _number(element, component, context, default=default) for component in ("r", "g", "b")
    ]
    try:
        return Color(*values)
    except DocumentValidationError as error:
        raise TboFormatError(f"{context}: {error}") from error

