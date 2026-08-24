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
- Pytest suite (unit and integration tests).
