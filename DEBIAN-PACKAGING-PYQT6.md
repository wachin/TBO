# Debian packaging for a PyQt6 application (TBO 2) — agent notes

This file documents the packaging fixes applied to TBO 2 so the resulting
`.deb` builds cleanly, ships the translations and icons, and installs with a
proper menu icon. It is meant to be handed to an AI agent as-is.

Repository: `https://github.com/wachin/TBO`

---

## 1. What changed and why

| File | Fix | Reason |
|------|-----|--------|
| `debian/rules` | Removed `export PYBUILD_SYSTEM = distutils` | The legacy `distutils` backend fails on CI because the apt setuptools is too old for PEP 639 `license` strings. |
| `debian/rules` | Install the icon as SVG (scalable) + PNG resized to 48×48 | So the menu icon is found at every size. The PNG is **resized** with Pillow because the source PNG is 60×60; installing it as-is in `hicolor/48x48/` triggers the Lintian warning `icon-size-and-directory-name-mismatch`. |
| `debian/rules` | Copy `data/doodle` into `/usr/share/tbo/doodle` | Ship the asset library. |
| `packaging/tbo.desktop` | `Icon=org.tbo.TBO` (was `Icon=tbo`) | The icon name must match the installed file, or the system shows a generic icon. |
| `debian/control` | `pybuild-plugin-pyproject` in Build-Depends | Required by the pybuild pyproject backend. |
| `pyproject.toml` | `license = { file = "COPYING" }` (was a SPDX string) | Old setuptools rejects the PEP 639 string format. |
| `pyproject.toml` | `package-data` includes translations `.qm` and the icon `NOTICE` | They must be shipped inside the package. |
| `translations/` + `src/tbo/translations/` | Compiled `.ts` → `.qm` and copied into the package | Packages ship compiled catalogs; `.qm` are tracked in git. |
| `packaging/update_translations.sh` | Copies `.qm` into `src/tbo/translations/` | Keeps the packaged catalogs fresh. |

---

## 2. `debian/control`

```text
Source: tbo
Section: graphics
Priority: optional
Maintainer: Washington Indacochea Delgado <linuxfrontier@proton.me>
Build-Depends: debhelper-compat (= 13),
               dh-python,
               pybuild-plugin-pyproject,
               python3,
               python3-setuptools
Standards-Version: 4.6.2
Homepage: https://github.com/wachin/TBO
Vcs-Git: https://github.com/wachin/TBO.git
Vcs-Browser: https://github.com/wachin/TBO

Package: tbo
Architecture: all
Depends: ${python3:Depends},
         ${misc:Depends},
         python3-pyqt6,
         python3-pyqt6.qtsvg
Recommends: python3-pyqt6.qtpdf
Description: Modern comic editor compatible with legacy TBO documents
 ...
```

Notes:
- Build-Depends must include **`pybuild-plugin-pyproject`**.
- Do NOT add `python3-pyqt6` to Build-Depends (it is a runtime `Depends`, not
  needed to build).

---

## 3. `debian/rules`

```makefile
#!/usr/bin/make -f

export PYBUILD_NAME = tbo
# Do NOT set PYBUILD_SYSTEM = distutils; let pybuild use the pyproject backend.

%:
	dh $@ --with python3 --buildsystem=pybuild

override_dh_auto_install:
	dh_auto_install
	install -d debian/tbo/usr/share/tbo
	cp -r data/doodle debian/tbo/usr/share/tbo/doodle
	install -d debian/tbo/usr/share/applications
	install -m644 packaging/tbo.desktop debian/tbo/usr/share/applications/org.tbo.TBO.desktop
	install -d debian/tbo/usr/share/metainfo
	install -m644 packaging/org.tbo.TBO.appdata.xml debian/tbo/usr/share/metainfo/org.tbo.TBO.appdata.xml
	install -d debian/tbo/usr/share/icons/hicolor/scalable/apps
	install -m644 packaging/org.tbo.TBO.svg debian/tbo/usr/share/icons/hicolor/scalable/apps/org.tbo.TBO.svg
	install -d debian/tbo/usr/share/icons/hicolor/48x48/apps
	python3 -c "from PIL import Image; im = Image.open('src/tbo/resources/icon.png').resize((48, 48), Image.Resampling.LANCZOS); im.save('debian/tbo/usr/share/icons/hicolor/48x48/apps/org.tbo.TBO.png')"

override_dh_clean:
	dh_clean
	rm -rf ../build ../dist
```

- `python3-pil` must be in Build-Depends so Pillow is available to resize the
  icon to 48×48.

---

## 4. `packaging/tbo.desktop` (icon must match the installed file)

```text
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=TBO
GenericName=Comic Editor
Comment=Create and edit comics
Exec=tbo %F
Icon=org.tbo.TBO
Terminal=false
Categories=Graphics;VectorGraphics;Qt;2DGraphics;
Keywords=comic;comics;editor;drawing;graphic;novel;
StartupNotify=true
MimeType=application/x-tbo;
X-GNOME-UsesNotifications=false
```

- The `Icon=` value **must equal the base name** of the installed icon file
  (`org.tbo.TBO` → `org.tbo.TBO.svg` / `org.tbo.TBO.png`).
- Installing both an SVG (scalable) and a 48×48 PNG guarantees the icon appears
  in menus and launchers at any size.

---

## 5. System packages required to build the `.deb`

```bash
sudo apt install build-essential debhelper dh-python python3 python3-setuptools \
    pybuild-plugin-pyproject python3-build python3-installer \
    python3-pyqt6 python3-pyqt6.qtsvg python3-pyqt6.qtpdf
```

- `pybuild-plugin-pyproject`, `python3-build`, `python3-installer`: required by
  the pybuild pyproject backend.
- `python3-pyqt6.qtpdf`: only a recommendation (PDF export).
- Translations tools (optional): `qt6-base-dev-tools` (provides `lrelease`/`lupdate`).

---

## 6. Translations must be shipped compiled

- Sources: `translations/*.ts` (tracked).
- Compiled: `translations/*.qm` **and** `src/tbo/translations/*.qm` (both
  tracked, because `.qm` are excluded from nothing — they ARE committed).
- `pyproject.toml` package-data includes `translations/*.qm` (resolved inside
  the package at `src/tbo/translations/`).

```bash
# Compile and copy into the package:
lrelease translations/tbo_en.ts -qm translations/tbo_en.qm
lrelease translations/tbo_es.ts -qm translations/tbo_es.qm
mkdir -p src/tbo/translations
cp translations/*.qm src/tbo/translations/
```

The script `packaging/update_translations.sh` does all of this automatically.

---

## 7. `pyproject.toml` package-data (ship everything)

```toml
[tool.setuptools.package-data]
"tbo" = [
    "resources/*.svg",
    "resources/*.png",
    "resources/icons/*.svg",
    "resources/icons/NOTICE",
    "translations/*.qm",
]
```

- The `NOTICE` file (icon attribution, GPL-2.0-or-later for Inkscape icons)
  must be shipped with the icons.

---

## 8. Audit the package before installing (Lintian + other tools)

Run these checks **before** installing with gdebi, so problems are caught early
instead of seeing Lintian warnings only in gdebi.

### 8.1 Lintian

```bash
lintian tbo_2.0.0.dev0-1_all.deb
```

`dpkg-buildpackage` already runs Lintian at the end, but running it explicitly
lets you iterate without a full rebuild. Use `lintian --info` for the full
explanation of each tag.

Common warnings for this project (all harmless, exit `0`):

- `initial-upload-closes-no-bugs`: the changelog references no bug number.
- `no-manual-page`: `/usr/bin/tbo` is a GUI app without a man page. To silence
  it, add a minimal man page and list it in `debian/tbo.manpages`.
- `icon-size-and-directory-name-mismatch`: fixed by resizing the icon to 48×48
  (see section 3). If it appears, the PNG size does not match its hicolor
  directory.

### 8.2 Inspect metadata and content

```bash
dpkg-deb --info tbo_2.0.0.dev0-1_all.deb     # metadata, dependencies
dpkg-deb --contents tbo_2.0.0.dev0-1_all.deb # what will be installed
```

### 8.3 Verify dependencies without installing

```bash
apt install --dry-run ./tbo_2.0.0.dev0-1_all.deb
```

This resolves the dependency tree and reports what would be pulled in, without
changing the system.

### 8.4 Verify installed-file checksums (after install)

```bash
sudo apt install debsums
debsums tbo
```

`debsums` checks the MD5 checksums of installed files against the package, to
detect corruption.

### 8.5 Full checklist before releasing

```bash
# 1. Build
dpkg-buildpackage -b -uc -us

# 2. Lintian (explicit)
lintian tbo_2.0.0.dev0-1_all.deb

# 3. Content + metadata
dpkg-deb --contents tbo_2.0.0.dev0-1_all.deb | less
dpkg-deb --info tbo_2.0.0.dev0-1_all.deb

# 4. Dry-run install (deps)
apt install --dry-run ./tbo_2.0.0.dev0-1_all.deb

# 5. Install and smoke test
sudo apt install ./tbo_2.0.0.dev0-1_all.deb
tbo --help    # or launch the app
debsums tbo   # after installing debsums
```

---

## 9. Build commands

```bash
# Build the .deb
dpkg-buildpackage -b -uc -us

# Install locally
sudo apt install ./tbo_2.0.0.dev0-1_all.deb

# Refresh icon caches after install if the icon does not appear
sudo update-icon-caches /usr/share/icons/*
```

---

Follow these steps in order. If a build fails, copy the exact error log from
the failing step and fix that one thing.
