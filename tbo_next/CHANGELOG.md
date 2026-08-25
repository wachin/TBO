# Changelog

All notable changes to TBO 2 (the Python/PyQt6 reimplementation) are documented
in this file. It follows [Semantic Versioning](https://semver.org).

## Versioning policy

- **Major (X.0.0)**: format-incompatible changes, removal of features, or
  breaking CLI/API changes.
- **Minor (0.X.0)**: new functionality that remains backward compatible.
- **Patch (0.0.X)**: bug fixes that do not change behavior.

The `2.0.0.dev0` version in `pyproject.toml` marks the in-development release
toward the first stable TBO 2. Until `2.0.0` is published, the application never
overwrites the only copy of a user document without confirmation or a safe copy.

## Support policy

- Stable releases receive bug fixes for the current and previous minor versions.
- Only Linux is officially supported. Other platforms are experimental until a
  maintainer and CI are available.
- Security issues take priority over feature work.

## [Unreleased]

### Added

- Python/PyQt6 reimplementation of TBO (`tbo_next/`).
- Read and write the legacy `.tbo` v1 format with a safe XML parser, size
  limits, and contextual errors; atomic writes with fsync.
- Domain model (`Comic`, `Page`, `Frame`, text/image/SVG objects) independent
  of Qt widgets.
- Interactive canvas: pages, panels, objects, zoom, fit, page navigation, and
  panel editing mode.
- Full undo/redo through `QUndoStack` for pages, panels, and objects.
- Text, image, and SVG import; object rotate, flip, and resize.
- Asset library with searchable doodle and bubble categories.
- Export to PNG (per page), PDF (multi-page), and SVG (per page) through a
  shared renderer.
- Session recovery: `.bak` backups and a 30-second `.autosave`.
- Preferences via `QSettings`: window geometry, last directory, recent files.
- Main toolbar, HiDPI scaling, and Qt translator loading.
- Help menu with user documentation (Help Contents, F1).
- Mouse-wheel zoom centered on the cursor with a zoom percentage in the status bar.
- Multi-selection via `Ctrl`+click or rubber-band drag, with batch delete.
- Panel alignment and distribution actions (Edit ▸ Align / Distribute).
- Copy/paste of panels and objects across pages (`Ctrl+C`/`Ctrl+V`).
- Drag & drop of assets from the library into the editing panel.
- Full-screen presentation mode (F5) with keyboard navigation.
- Export dialog with format, page range (all/current), and PNG scale up to 1000 %.
- Theme selection (System/Dark/Light) with a persistent preference.
- Optional snap-to-grid (10 px) for panel movement and resizing, with a visible
  grid on the canvas.
- Session restore: the last opened document is reopened on startup.
- Pages dock with per-page thumbnails for quick navigation.
- Find text dialog (`Ctrl+F`) that locates matches and navigates to them.
- A buildable character asset set (blank head + eyes/mouth/ears with
  expressions) added under `data/doodle/head/`, with a generator script.
- The asset library is split into four tabs: Doodles (original assets),
  Character (the buildable head parts), Accessories (actions/devices/emotes/pcs)
  and Bubbles.
- The application icon is bundled inside the package (`tbo/resources/`) and set
  on the window and the application.
- Credits: Washington Indacochea Delgado added as the author of the PyQt6
  port and its improvements (AUTHORS, About dialog, pyproject.toml,
  debian/control, debian/copyright).
- Select All (`Ctrl+A`) and a default rubber-band selection mode.
- Space-bar hold to temporarily pan the view (Inkscape-style).
- Flip buttons added to the main toolbar for quick access.
- Flip toolbar buttons now show icons (from Inkscape, GPL-2.0-or-later) with
  tooltips; attribution in `resources/icons/NOTICE`.
- Icons and tooltips added to New, Open, Save, Save As, Undo and Redo
  (Inkscape icons, GPL-2.0-or-later).
- Icons added to Add Panel (own SVG), Add Text, Actual Size and Fit Page.
- Help dialog rewritten in English (source language) and translatable via Qt
  Linguist; `tbo_en.ts` and `tbo_en.qm` generated.
- Spanish translation added (`tbo_es.ts` / `tbo_es.qm`); the interface and the
  Help dialog follow the system language (or the saved preference).
- Speech bubbles from the Bubbles tab now insert an editable text object
  centred inside the bubble.
- The asset catalog scans user data directories (`~/.tbo/doodle`,
  `~/.local/share/tbo/doodle`) and merges custom SVG drawings into the shipped
  categories.
- GitHub Actions CI (`ci.yml`): lint, unit/integration tests under Xvfb, coverage.
- Manual build workflow (`build.yml`, `workflow_dispatch`) producing wheel, sdist,
  `.deb`, and Flatpak artifacts.
- Fixture corpus under `tests/fixtures/` and property-based parser tests
  (Hypothesis): fuzzing of arbitrary input and semantic round-trips.
- Fixed: the writer now rejects XML-invalid control characters instead of
  producing an unreadable file.
- Pytest suite (unit and integration tests).
