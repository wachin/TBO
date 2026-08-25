from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QRect, QSize, QSizeF, Qt
from PyQt6.QtGui import QImage, QPageSize, QPainter, QPdfWriter
from PyQt6.QtSvg import QSvgGenerator

from tbo.document.model import Comic, Page
from tbo.rendering.renderer import ComicRenderer


class ExportError(ValueError):
    """Raised when a document cannot be exported to the requested format."""


SUPPORTED_FORMATS = ("png", "pdf", "svg")


def _validate_format(fmt: str) -> str:
    normalized = fmt.lower().lstrip(".")
    if normalized not in SUPPORTED_FORMATS:
        raise ExportError(f"Unsupported export format {fmt!r}; expected one of {SUPPORTED_FORMATS}")
    return normalized


def export_page(
    page: Page,
    comic: Comic,
    target: Path,
    *,
    fmt: str | None = None,
    asset_root: Path | None = None,
    scale: float = 1.0,
) -> Path:
    fmt = _validate_format(fmt or target.suffix)
    destination = target.with_suffix(f".{fmt}")
    renderer = ComicRenderer(asset_root=asset_root)

    if fmt == "png":
        width = max(1, round(comic.width * scale))
        height = max(1, round(comic.height * scale))
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        painter = QPainter()
        if not painter.begin(image):
            raise ExportError(f"Could not open {destination} for writing")
        painter.scale(scale, scale)
        _render_with(painter, renderer, page, comic)
        if not painter.end():
            raise ExportError(f"Could not finalize {destination}")
        if not image.save(str(destination)):
            raise ExportError(f"Could not write {destination}")
        return destination

    surface = _create_surface(fmt, destination, comic)
    painter = QPainter()
    if not painter.begin(surface):
        raise ExportError(f"Could not open {destination} for writing")
    _render_with(painter, renderer, page, comic)
    if not painter.end():
        raise ExportError(f"Could not finalize {destination}")
    return destination


def _render_with(painter: QPainter, renderer: ComicRenderer, page: Page, comic: Comic) -> None:
    painter.setRenderHints(
        QPainter.RenderHint.Antialiasing
        | QPainter.RenderHint.TextAntialiasing
        | QPainter.RenderHint.SmoothPixmapTransform
    )
    renderer.paint_page(painter, page, comic)


def export_comic(
    comic: Comic,
    target: Path,
    *,
    fmt: str | None = None,
    asset_root: Path | None = None,
    scale: float = 1.0,
) -> list[Path]:
    fmt = _validate_format(fmt or target.suffix)
    if fmt == "pdf":
        return [_export_pdf(comic, target, asset_root=asset_root)]
    if comic.pages:
        stem = target.with_suffix("").stem
        return [
            export_page(
                page,
                comic,
                target.with_name(f"{stem}-{index + 1}").with_suffix(f".{fmt}"),
                fmt=fmt,
                asset_root=asset_root,
                scale=scale,
            )
            for index, page in enumerate(comic.pages)
        ]
    return []


def _create_surface(fmt: str, destination: Path, comic: Comic):
    if fmt == "svg":
        generator = QSvgGenerator()
        generator.setFileName(str(destination))
        generator.setSize(QSize(comic.width, comic.height))
        generator.setViewBox(QRect(0, 0, comic.width, comic.height))
        return generator
    if fmt == "pdf":
        return _export_pdf_writer(comic, destination)
    raise ExportError(f"Unsupported export format {fmt!r}")


def _export_pdf(comic: Comic, target: Path, *, asset_root: Path | None = None) -> Path:
    destination = target.with_suffix(".pdf")
    writer = _export_pdf_writer(comic, destination)
    renderer = ComicRenderer(asset_root=asset_root)
    painter = QPainter()
    if not painter.begin(writer):
        writer.close()
        raise ExportError(f"Could not open {destination} for writing")
    painter.setRenderHints(
        QPainter.RenderHint.Antialiasing
        | QPainter.RenderHint.TextAntialiasing
        | QPainter.RenderHint.SmoothPixmapTransform
    )
    for index, page in enumerate(comic.pages):
        if index > 0:
            writer.newPage()
        renderer.paint_page(painter, page, comic)
    if not painter.end():
        raise ExportError(f"Could not finalize {destination}")
    return destination


def _export_pdf_writer(comic: Comic, destination: Path) -> QPdfWriter:
    writer = QPdfWriter(str(destination))
    writer.setResolution(96)
    writer.setPageSize(
        QPageSize(
            QSizeF(comic.width * 25.4 / 96.0, comic.height * 25.4 / 96.0),
            QPageSize.Unit.Millimeter,
        )
    )
    return writer
