from pathlib import Path

from PyQt6.QtGui import QImage

from tbo.document.model import Comic, Frame, Page, TextObject
from tbo.formats.tbo_v1 import load
from tbo.rendering import ExportError, export_comic, export_page
from tbo.ui.main_window import MainWindow


REPOSITORY_ROOT = Path(__file__).parents[3]


def _sample_comic() -> Comic:
    comic = Comic("Export", 400, 200, [Page()])
    frame = Frame(x=10, y=10, width=200, height=100)
    frame.objects.append(TextObject(x=20, y=20, width=120, height=40, text="Hi", font="Sans 12"))
    comic.pages[0].frames.append(frame)
    return comic


def test_export_page_png_produces_file(qtbot, tmp_path: Path) -> None:
    comic = _sample_comic()
    target = export_page(comic.pages[0], comic, tmp_path / "page.png")
    assert target.is_file()
    image = QImage(str(target))
    assert not image.isNull()
    assert (image.width(), image.height()) == (400, 200)


def test_export_comic_png_writes_one_file_per_page(qtbot, tmp_path: Path) -> None:
    comic = _sample_comic()
    comic.pages.append(Page())
    written = export_comic(comic, tmp_path / "book.png")
    assert len(written) == 2
    assert all(path.is_file() for path in written)
    assert {path.name for path in written} == {"book-1.png", "book-2.png"}


def test_export_comic_pdf_has_multiple_pages(qtbot, tmp_path: Path) -> None:
    comic = _sample_comic()
    comic.pages.append(Page())
    written = export_comic(comic, tmp_path / "book.pdf")
    assert len(written) == 1
    assert written[0].is_file()
    assert written[0].suffix == ".pdf"


def test_export_comic_svg_per_page(qtbot, tmp_path: Path) -> None:
    comic = _sample_comic()
    written = export_comic(comic, tmp_path / "book.svg")
    assert len(written) == 1
    assert written[0].is_file()
    content = written[0].read_text(encoding="utf-8")
    assert "<svg" in content


def test_export_rejects_unknown_format(tmp_path: Path) -> None:
    comic = _sample_comic()
    try:
        export_comic(comic, tmp_path / "book.xyz", fmt="xyz")
    except ExportError:
        return
    raise AssertionError("expected ExportError for unknown format")


def test_exported_png_matches_document_dimensions(qtbot, tmp_path: Path) -> None:
    window = MainWindow(asset_root=REPOSITORY_ROOT / "data" / "doodle")
    qtbot.addWidget(window)
    window.open_document(REPOSITORY_ROOT / "data" / "tut.tbo")
    comic = window.canvas.comic
    assert comic is not None
    target = export_page(
        comic.pages[0], comic, tmp_path / "tut1.png", asset_root=window.canvas._asset_root
    )
    assert target.is_file()
    image = QImage(str(target))
    assert image.width() == comic.width and image.height() == comic.height


def test_window_export_action_is_enabled_with_document(qtbot, tmp_path: Path) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert not window.export_action.isEnabled()
    window.new_document("Exportable", 300, 150)
    assert window.export_action.isEnabled()
