# TBO 2 (in development)

This directory contains the Python and PyQt6 reimplementation of TBO. The C/GTK
code in the repository root is retained as a compatibility reference.

English is the source language for the application. User-interface strings are
marked for Qt translation, but translation catalogs will be introduced only
after the functionality and terminology have stabilized.

## Running from the repository

Use the launcher from the repository root:

```bash
./tbo.sh
./tbo.sh data/tut.tbo
```

The launcher configures `PYTHONPATH` automatically and can be invoked from any
directory.

The equivalent command without the launcher is:

```bash
cd tbo_next
PYTHONPATH=src python3 -m tbo ../data/tut.tbo
```

Omit the document path to create a new comic. The application can read and
render pages, panels, text, images, and SVG resources from the historical
format.

## Keyboard shortcuts

- `Ctrl+N`: create a comic with a title and dimensions;
- `Ctrl+O`: open a document;
- `Ctrl+S`: save atomically;
- `Ctrl+Shift+S`: save a copy;
- `PageUp` / `PageDown`: previous or next page;
- `Ctrl+Shift+N`: add a page after the current page;
- `Ctrl+Delete`: delete the current page;
- `Ctrl+PageUp` / `Ctrl+PageDown`: move the current page left or right;
- `+` / `-`: zoom in or out;
- `1`: return to actual size;
- `2`: fit the page to the window;
- `F`: add a panel;
- `T`: add text while editing a panel;
- drag a selected panel: move it;
- drag its yellow bottom-right handle: resize it;
- arrow keys: move the selection in 5-pixel increments;
- `Ctrl+D`: clone the selected panel or object;
- `Delete`: delete the selected panel or object;
- `Ctrl+Z` / `Ctrl+Shift+Z`: undo or redo.

Adding, cloning, moving, resizing, and deleting panels changes the document
model and is recorded in the undo history. Creating, deleting, and reordering
pages is reversible as well. An asterisk in the window title indicates unsaved
changes.

Double-click a panel to edit its contents. In this mode, you can select and drag
text, images, or SVGs, clone them with `Ctrl+D`, move them with the arrow keys,
and delete them with `Delete`. These operations support undo/redo and persist in
the `.tbo` file. The Edit menu also lets you add formatted text or import raster
images and SVG files. Press `Esc` to return to page editing; other panels are
dimmed while a panel is being edited.

TBO 2 currently writes the unversioned v1 format for compatibility with the
historical application. Use **Save As** while the new implementation remains in
development.

When there are pending changes, TBO asks whether to save, discard, or cancel
before creating another document, opening one, or closing the window. Canceling
never replaces the document or removes its undo/redo history.

## Exporting

Use **File ▸ Export…** (`Ctrl+E`) to render the document to image files. The same
renderer draws the on-screen canvas and the exported files, so the output matches
the editor.

- **PNG**: one file per page, named `name-1.png`, `name-2.png`, ….
- **PDF**: a single multi-page document.
- **SVG**: one vector file per page.

Missing raster or SVG resources are drawn as a dashed red rectangle rather than
aborting the export.

## Tests

```bash
cd tbo_next
QT_QPA_PLATFORM=offscreen python3 -m pytest
```

Editable development installation:

```bash
python3 -m pip install -e '.[dev]'
```

The `.tbo` format is treated as untrusted input. Do not relax its validation or
limits without adding a regression test first.
