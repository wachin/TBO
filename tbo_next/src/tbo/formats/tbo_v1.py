from __future__ import annotations

import math
import os
import stat
import tempfile
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


def dumps(comic: Comic) -> bytes:
    """Serialize a document using the legacy, unversioned TBO v1 format."""
    _validate_document_size(comic)
    root = ET.Element("tbo", {"width": str(comic.width), "height": str(comic.height)})
    for page_index, page in enumerate(comic.pages):
        page_element = ET.SubElement(root, "page")
        for frame_index, frame in enumerate(page.frames):
            context = f"page {page_index + 1}, frame {frame_index + 1}"
            frame_element = ET.SubElement(
                page_element,
                "frame",
                {
                    "x": str(frame.x),
                    "y": str(frame.y),
                    "width": str(frame.width),
                    "height": str(frame.height),
                    "border": _format_bool(frame.border),
                    **_color_attributes(frame.color, context),
                },
            )
            for object_index, graphic_object in enumerate(frame.objects):
                frame_element.append(
                    _serialize_object(graphic_object, f"{context}, object {object_index + 1}")
                )

    ET.indent(root, space=" ")
    data = ET.tostring(root, encoding="utf-8", xml_declaration=True, short_empty_elements=False)
    if len(data) > MAX_FILE_SIZE:
        raise TboFormatError(f"Serialized document exceeds the {MAX_FILE_SIZE}-byte limit")
    return data + b"\n"


def save(comic: Comic, filename: str | Path) -> None:
    """Atomically save a document without exposing a partially written target."""
    target = Path(filename)
    data = dumps(comic)
    if not target.parent.is_dir():
        raise TboFormatError(f"Destination directory does not exist: {target.parent}")

    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        if target.exists():
            os.chmod(temporary_name, stat.S_IMODE(target.stat().st_mode))
        with os.fdopen(descriptor, "wb") as temporary_file:
            temporary_file.write(data)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_name, target)
        temporary_name = None
    except OSError as error:
        raise TboFormatError(f"Could not save {target}: {error}") from error
    finally:
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            except OSError:
                pass


def _serialize_object(graphic_object: GraphicObject, context: str) -> ET.Element:
    common = {
        "x": str(graphic_object.x),
        "y": str(graphic_object.y),
        "width": str(graphic_object.width),
        "height": str(graphic_object.height),
        "angle": _format_float(graphic_object.angle, context),
        "flipv": _format_bool(graphic_object.flip_vertical),
        "fliph": _format_bool(graphic_object.flip_horizontal),
    }
    if isinstance(graphic_object, TextObject):
        if not graphic_object.text or len(graphic_object.text) > MAX_TEXT_LENGTH:
            raise TboFormatError(f"{context}: text must be non-empty and within the limit")
        _validate_xml_text(graphic_object.text, "text", context)
        element = ET.Element(
            "text",
            {
                **common,
                "font": _validate_string(graphic_object.font, "font", context),
                **_color_attributes(graphic_object.color, context),
            },
        )
        element.text = graphic_object.text
        return element
    if isinstance(graphic_object, (SvgObject, ImageObject)):
        tag = "svgimage" if isinstance(graphic_object, SvgObject) else "piximage"
        return ET.Element(
            tag,
            {
                **common,
                "path": _validate_string(str(graphic_object.path), "path", context),
            },
        )
    raise TboFormatError(f"{context}: unsupported object type {type(graphic_object).__name__}")


def _validate_document_size(comic: Comic) -> None:
    if not 0 < comic.width <= MAX_DIMENSION or not 0 < comic.height <= MAX_DIMENSION:
        raise TboFormatError(f"Document dimensions must be between 1 and {MAX_DIMENSION}")
    if len(comic.pages) > MAX_PAGES:
        raise TboFormatError(f"Document contains more than {MAX_PAGES} pages")
    for page_index, page in enumerate(comic.pages):
        if len(page.frames) > MAX_FRAMES_PER_PAGE:
            raise TboFormatError(f"Page {page_index + 1} contains too many frames")
        for frame_index, frame in enumerate(page.frames):
            context = f"page {page_index + 1}, frame {frame_index + 1}"
            if not 0 < frame.width <= MAX_DIMENSION or not 0 < frame.height <= MAX_DIMENSION:
                raise TboFormatError(f"{context}: dimensions are outside the supported range")
            if len(frame.objects) > MAX_OBJECTS_PER_FRAME:
                raise TboFormatError(f"{context} contains too many objects")
            for object_index, graphic_object in enumerate(frame.objects):
                if not 0 < graphic_object.width <= MAX_DIMENSION or not (
                    0 < graphic_object.height <= MAX_DIMENSION
                ):
                    raise TboFormatError(
                        f"{context}, object {object_index + 1}: dimensions are outside the supported range"
                    )


def _color_attributes(color: Color, context: str) -> dict[str, str]:
    return {
        "r": _format_color(color.red, context),
        "g": _format_color(color.green, context),
        "b": _format_color(color.blue, context),
    }


def _format_color(value: float, context: str) -> str:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise TboFormatError(f"{context}: color components must be between 0 and 1")
    return f"{value:.6f}"


def _format_float(value: float, context: str) -> str:
    if not math.isfinite(value):
        raise TboFormatError(f"{context}: angle must be finite")
    return f"{value:.6f}"


def _format_bool(value: bool) -> str:
    return "1" if value else "0"


def _validate_string(value: str, name: str, context: str) -> str:
    if not value:
        raise TboFormatError(f"{context}: {name} must not be empty")
    if len(value) > MAX_PATH_LENGTH:
        raise TboFormatError(f"{context}: {name} is too long")
    _validate_xml_text(value, name, context)
    return value


def _validate_xml_text(value: str, name: str, context: str) -> None:
    for character in value:
        code = ord(character)
        valid = (
            code in (0x9, 0xA, 0xD)
            or 0x20 <= code <= 0xD7FF
            or 0xE000 <= code <= 0xFFFD
            or 0x10000 <= code <= 0x10FFFF
        )
        if not valid:
            raise TboFormatError(
                f"{context}: {name} contains a character that is not allowed in XML"
            )


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
