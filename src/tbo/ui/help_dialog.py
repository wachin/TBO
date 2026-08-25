from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class HelpDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("TBO Help"))
        self.resize(680, 560)

        browser = QTextBrowser()
        browser.setMarkdown(self._help_text())
        browser.setOpenExternalLinks(True)
        browser.document().setDefaultStyleSheet("body { font-size: 13px; }")

        layout = QVBoxLayout(self)
        layout.addWidget(browser)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)

    def _help_text(self) -> str:
        return self.tr(
            """\
# TBO 2 — Help

## Where are the `.tbo` files?

TBO documents are complete comic files (pages, panels and objects). The
distribution includes two examples:

- `data/tut.tbo` — the tutorial.
- `doc/pres-final.tbo` — a presentation example.

## Where are the characters (doodles and speech bubbles)?

There is no `.tbo` file per character. Characters, decorations and speech
bubbles are **SVG files** shipped under the `doodle` directory, organised by
category (body, eyes, mouth, accessories, characters, etc.).

To use them:

1. **Double-click a panel** to enter its editing mode.
2. In the **Asset Library** dock on the right, choose the **Doodles** tab
   (decorations and characters), **Character** (buildable head parts),
   **Accessories** (actions, devices, emotes, pcs) or **Bubbles** (speech
   bubbles).
3. Type in the search box or browse the categories.
4. **Click or drag** a thumbnail to insert it into the panel.

When you insert a **speech bubble** (Bubbles tab), an editable **text object**
is automatically placed inside it, centered and ready to be edited. **Double
click** the text to edit it in place (Ctrl+Enter accepts, Esc cancels), or
select it and press `E` / use **Edit ▸ Edit Text**.

Everything you insert can be moved, resized, rotated, flipped, cloned and
deleted, and is saved in the `.tbo` file.

## How does the last-folder memory work?

The program remembers the last folder you used. When you open, save, export or
import a file, that folder is saved. The next time you open **Open**, **Save
As**, **Export**, **Add Image** or **Add SVG**, the dialog starts in that
folder. The first time, with no history, it starts in your home directory
(`~`).

## Multi-selection, alignment and distribution

Hold **`Ctrl`** while clicking several panels or objects, or drag a rectangle
on the canvas, to select them at once. **`Ctrl+A`** selects all panels on a
page, or all objects inside a panel.

Hold the **space bar** and drag to pan the view without moving the selection
(Inkscape-style).

Use the **Flip** buttons on the toolbar (or `H` / `V`) to mirror a bubble or
object horizontally or vertically — for example, to point the bubble tail
toward the character's mouth.

With several items selected you can:

- Press **`Delete`** to remove them all in one step (reversible with undo).
- Use the **Edit ▸ Align** menu (left, center, right, top, etc.) to align the
  selected panels.
- Use **Edit ▸ Distribute** to space them evenly.

To **copy and paste** between pages use **`Ctrl+C`** and **`Ctrl+V`**: copy
panels (on the page) or objects (inside a panel) and paste them on the current
page or panel.

## Drag from the library

Besides clicking a thumbnail, you can **drag** it from the Asset Library and
**drop** it into the panel you are editing.

## Adding your own drawings (SVG)

You can create your own eyes, mouths, ears, noses, eyebrows, eyelashes, lips,
or any other element in **SVG** and the program will load them automatically.
No conversion is needed — the program uses SVGs directly.

Just place your **.svg** files in one of these folders (the program does not
create them, you must):

- `~/.tbo/doodle/` (e.g. `~/.tbo/doodle/head/eyes/my_eyes.svg`)
- `~/.local/share/tbo/doodle/`

Organise them by folder the same way as the example character (e.g.
`head/eyes/`, `head/mouths/`, `noses/`). The program will merge them with the
shipped resources and show them in the corresponding tab.

## Buildable character

The **Character** tab in the library contains an example buildable character
made of independent parts you can combine at will:

- **Head**: a blank face (no eyes, ears or mouth).
- **Eyes**: normal, happy, sad, closed, surprised…
- **Mouth**: smile, neutral, sad, open, tongue…
- **Ears**: normal, pointy.

Place the head first, then drag each part into position. You can use **Rotate**
(`[` / `]`), **Flip** (`H` / `V`), **Resize** (drag the bottom-right handle)
and mix any expressions you like.

## Presentation and export

- Press **`F5`** (View ▸ Presentation) to read the comic in full screen.
  Navigate with the arrow keys, `Space` or `Page Up`/`Page Down`; exit with
  `Esc`.
- **Export** (`Ctrl+E`) lets you choose the format, whether to export all pages
  or only the current one, and the output scale (up to 1000 %) for PNG.

## Theme, grid and session

- **View ▸ Theme**: choose **System**, **Dark** or **Light**. The choice is
  remembered between sessions.
- **View ▸ Snap to Grid**: when active, panels snap to a 10 px grid while
  moving or resizing, and the grid is shown on the canvas. Also remembered.
- The program **reopens the last document** you had open when you close it.

## Pages and search

- The **Pages** dock on the left shows a **thumbnail** of every page; click one
  to jump to it. Thumbnails refresh as the comic is edited.
- **Edit ▸ Find Text…** (`Ctrl+F`) searches every text object in the document
  and navigates to the page and panel containing a match.

## Useful shortcuts

| Shortcut | Action |
| -------- | ------ |
| `Ctrl+N` | New comic |
| `Ctrl+O` | Open |
| `Ctrl+S` | Save |
| `Ctrl+E` | Export |
| `Page Up` / `Page Down` | Previous / next page |
| `F` | Add panel (on the page) |
| Double-click panel | Edit its contents |
| `T` | Add text (while editing a panel) |
| `Esc` | Leave panel editing |
| `Ctrl+D` | Clone selected panel / object |
| `Ctrl+C` / `Ctrl+V` | Copy / paste panels or objects |
| `Ctrl` + click / drag | Multi-select |
| `Ctrl+A` | Select all |
| `Space` + drag | Pan the view |
| `Delete` | Delete selected panel(s) / object(s) |
| `[` / `]` | Rotate object left / right |
| `H` / `V` | Flip object horizontally / vertically |
| `Ctrl` + wheel, `+` / `-` / `1` / `2` | Zoom in / out / actual size / fit page |
| `F5` | Full-screen presentation |
| `Ctrl+F` | Find text in the document |
| `Ctrl+Z` / `Ctrl+Shift+Z` | Undo / redo |
"""
        )
