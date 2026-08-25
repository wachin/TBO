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
- `Ctrl+E`: export;
- `PageUp` / `PageDown`: previous or next page;
- `Ctrl+Shift+N`: add a page after the current page;
- `Ctrl+Delete`: delete the current page;
- `Ctrl+PageUp` / `Ctrl+PageDown`: move the current page left or right;
- `Ctrl+wheel`, `+` / `-`: zoom in / out (centered on cursor);
- `1`: return to actual size;
- `2`: fit the page to the window;
- `F`: add a panel;
- `T`: add text while editing a panel;
- drag a selected panel: move it;
- drag its yellow bottom-right handle: resize it;
- arrow keys: move the selection in 5-pixel increments;
- `Ctrl+D`: clone the selected panel or object;
- `Ctrl+C` / `Ctrl+V`: copy / paste panels or objects;
- `Ctrl` + click / drag: multi-select;
- `Delete`: delete the selected panel or objects;
- `Ctrl+Z` / `Ctrl+Shift+Z`: undo or redo;
- `Esc`: leave panel editing mode;
- `[` / `]`: rotate selected object left / right;
- `H` / `V`: flip selected object horizontally / vertically;
- `F5`: full-screen presentation mode;
- `Ctrl+F`: find text in the document.

## Preferences, theme and session

- **Theme** (View ▸ Theme): System / Dark / Light, remembered between runs.
- **Snap to Grid** (View ▸ Snap to Grid): aligns panels to a 10 px grid while
  moving or resizing them, and shows the grid on the canvas.
- The application **reopens the last document** it had open when it exits, so
  you can pick up where you left off.

## Pages and search

- The **Pages** dock on the left shows a thumbnail of every page; click one to
  jump to it. Thumbnails refresh as the comic is edited.
- **Edit ▸ Find Text…** (`Ctrl+F`) searches every text object in the document
  and navigates to the page and panel containing a match.
- The **Character** tab of the asset library contains a buildable character
  made of separate SVG parts: a blank head plus `eyes`, `mouth` and `ears`
  categories with several expressions. Drop each part onto a panel and arrange
  them freely. The generator script is `tools/generate_character_parts.py`.

### Custom assets

The library also scans user data directories, so you can add your own SVG
drawings without converting anything. Place your files under `~/.tbo/doodle/`
or `~/.local/share/tbo/doodle/`, organized by folder (e.g.
`head/eyes/my_eyes.svg`), and they are merged into the matching categories.

See **[docs/creating-characters.md](docs/creating-characters.md)** for the full
guide: where to put files, the folder layout, size/viewBox policies, and how to
build a character from scratch when the bundled ones are not what you want.

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

While editing a panel, the **Asset Library** dock on the right offers the SVG
doodles and speech bubbles shipped with the application. The **Doodles** and
**Bubbles** tabs group assets by category with a search box; clicking a preview
inserts the asset into the current panel as an `SvgObject` that is undoable and
persists in the `.tbo` file. The dock is disabled outside panel editing mode.

TBO 2 currently writes the unversioned v1 format for compatibility with the
historical application. Use **Save As** while the new implementation remains in
development.

When there are pending changes, TBO asks whether to save, discard, or cancel
before creating another document, opening one, or closing the window. Canceling
never replaces the document or removes its undo/redo history.

## Session recovery and preferences

- **Recovery**: saving a file keeps a `.bak` copy of the previous version. A
  background timer also writes an `.autosave` copy of a modified document every
  30 seconds; the copy is removed as soon as the file is saved. The original
  document is never overwritten without an explicit save.
- **Preferences** are persisted with `QSettings` and kept separate from `.tbo`
  documents: window geometry, the last directory used, and the list of recent
  files (**File ▸ Recent Files**). No sensitive paths are written to logs.
- **HiDPI**: the application enables high-DPI scaling and loads Qt translations
  for the configured locale. Interface strings are already marked for Qt
  Linguist; translation catalogs will be added once the terminology stabilizes.

## Exporting

Use **File ▸ Export…** (`Ctrl+E`) to render the document to image files. The same
renderer draws the on-screen canvas and the exported files, so the output matches
the editor. The export dialog lets you choose the format, whether to export all
pages or only the current page, and the output scale (up to 1000 %) for PNG.

- **PNG**: one file per page, named `name-1.png`, `name-2.png`, ….
- **PDF**: a single multi-page document.
- **SVG**: one vector file per page.

Missing raster or SVG resources are drawn as a dashed red rectangle rather than
aborting the export.

## Presentation mode

Press **`F5`** (View ▸ Presentation) to read the comic in full screen. Navigate
with the arrow keys, `Space`, or `PageUp`/`PageDown`; press `Esc` to leave.

## Tests

The unit tests run without a display. The integration tests drive a real
`QGraphicsView`, so they need a working Qt platform plugin. A virtual display
such as `xvfb-run` is the most reliable option:

```bash
cd tbo_next
xvfb-run -a python3 -m pytest
```

`QT_QPA_PLATFORM=offscreen` also works, but it can abort when the graphics view
is torn down, depending on the Qt build. The unit tests (`tests/unit`) never
touch the view and always run headless.

### Platform support

Tested with:

| Plugin    | Environment            | Status          |
|-----------|------------------------|-----------------|
| xcb       | X11 (`DISPLAY=:0`)     | Working         |
| wayland   | Wayland compositor     | Plugin available |
| offscreen | Headless (CI/tests)    | Working         |

Run `./test_platforms.sh` in the source checkout to verify the available
backends start and exit cleanly.

Editable development installation:

```bash
python3 -m pip install -e '.[dev]'
```

## Continuous integration

GitHub Actions workflows live in `.github/workflows/`:

- **`ci.yml`** runs automatically on every push/PR: lint (`ruff`), unit tests,
  integration tests under `xvfb`, and a coverage report (threshold 80 %) for
  Python 3.11 and 3.12.
- **`build.yml`** is **manual** (`workflow_dispatch`, triggered from the Actions
  tab) and produces the distributable executables as artifacts: Python
  wheel/sdist, a Debian `.deb`, and a Flatpak bundle.

Coverage locally:

```bash
cd tbo_next
python3 -m pytest tests/unit --cov=src/tbo --cov-report=term-missing
```

## Resources and packaging

The application resolves its asset library through `tbo.resources`. In a source
checkout it uses `data/doodle` from the repository root. When installed as a
package, it also looks in `share/tbo/doodle` under the installation prefix; the
Flatpak/deb build is expected to install the doodle tree there.

- Versioning, changelog, and support policy are defined in `CHANGELOG.md`.
- `pyproject.toml` declares the package, its `tbo` entry point, dev
  dependencies, and `package-data` for future `translations/*.qm` catalogs.

### Packaging helpers (`packaging/`)

- `tbo.desktop` and `org.tbo.TBO.appdata.xml`: freedesktop metadata.
- `org.tbo.TBO.json`: Flatpak manifest (installs the app, desktop entry,
  AppStream data, icon, and the doodle tree under `share/tbo/doodle`).
- `org.tbo.TBO.svg`: application icon.
- `build.sh`: builds the sdist/wheel, runs lint and unit tests, generates
  checksums and a dependency list, and verifies a clean install.
- `update_translations.sh`: extracts strings to `translations/*.ts` with
  `pylupdate6`/`lupdate` and compiles `.qm` files with `lrelease`.

### Building the Debian package

The `debian/` directory in the source root produces a binary `.deb`:

```bash
cd tbo_next
dpkg-buildpackage -b -uc -us
```

Build dependencies: `debhelper-compat (= 13)`, `dh-python`, `pybuild-plugin-pyproject`,
`python3`, `python3-setuptools`, `python3-pyqt6`. The generated package installs the
application, the doodle library under `/usr/share/tbo/doodle`, the desktop entry,
AppStream metadata, and the application icon.

```bash
./packaging/build.sh
./packaging/update_translations.sh
cd packaging && flatpak-builder build org.tbo.TBO.json --force-clean
```

The `.tbo` format is treated as untrusted input. Do not relax its validation or
limits without adding a regression test first.
