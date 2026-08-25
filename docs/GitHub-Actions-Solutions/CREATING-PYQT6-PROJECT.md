# Creating a PyQt6 project that passes GitHub Actions CI (agent instructions)

This file is meant to be read by an AI agent **before** it starts writing a
PyQt6 project. Following these instructions **exactly and in order** will avoid
the most common CI failures: missing system libraries, wrong build backend,
coverage thresholds, and QGraphicsView teardown aborts.

---

## 1. Project structure

```
my-project/
├── pyproject.toml          # <-- REQUIRED. Do NOT create setup.py.
├── src/
│   └── my_project/         # package name (use underscores, not hyphens)
│       ├── __init__.py     # with __version__
│       ├── __main__.py     # entry point
│       └── application.py
├── tests/
│   ├── unit/
│   └── integration/
├── data/                   # assets (SVG, icons, etc.)
├── packaging/              # .desktop, appdata, Flatpak manifest
├── debian/                 # only if building a .deb
├── translations/           # .ts / .qm files
├── .github/workflows/      # CI and build workflows
├── .gitignore
└── README.md
```

**Rules**:
- Use `src/` layout (package inside `src/`).
- The entry point is `src/my_project/__main__.py` with `-m my_project`.
- Do **NOT** create `setup.py`. Only `pyproject.toml` (PEP 517).
- Do **NOT** create `setup.cfg`.
- `__init__.py` must contain `__version__ = "x.y.z.dev0"`.
- **Nuitka (Windows build)**: with a `src/` layout, set `$env:PYTHONPATH`
  before running Nuitka so the package can be imported. Nuitka has no
  `--python-path` option. A flat `main.py` at the root does not need this;
  a `src/` layout does. See the Windows build script in `packaging/`.

---

## 2. pyproject.toml (the single most important file)

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "my_project"
version = "0.1.0.dev0"
description = "A PyQt6 application"
readme = "README.md"
requires-python = ">=3.11"
license = { file = "COPYING" }          # <-- use file format, NOT string
# license = "SPDX-id" will FAIL on older setuptools (CI runners)
authors = [
    { name = "Your Name", email = "you@example.com" },
]
keywords = ["pyqt6", "qt6", "gui"]
dependencies = ["PyQt6>=6.6"]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-cov>=5",
    "pytest-qt>=4.4",
    "ruff>=0.9",
    "hypothesis>=6.0",         # <-- REQUIRED by CI if you have fuzz tests
]

[project.urls]
Homepage = "https://github.com/you/my-project"

[project.scripts]
my_project = "my_project.application:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"my_project" = ["resources/*.svg", "resources/*.png", "translations/*.qm"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.coverage.run]
source = ["src/my_project"]

[tool.coverage.report]
show_missing = true
# Do NOT set fail_under here; CI sets it per-module.

[tool.pytest.ini_options]
addopts = "-ra --strict-markers"
testpaths = ["tests"]
pythonpath = ["src"]
```

---

## 3. Ruff (lint)

Apply in order:

```bash
pip install ruff
ruff check src tests --fix
ruff format src tests
ruff check src tests --fix --unsafe-fixes   # optional SIM* rules
```

CI will fail if `ruff check src tests` has errors. Run it locally before
every push.

---

## 4. Coverage

On CI, measure only the **critical modules** (not the UI, which is only
covered by integration tests):

```yaml
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/unit \
  --cov=src/my_project/document --cov=src/my_project/formats \
  --cov=src/my_project/assets \
  --cov=src/my_project/ui/commands --cov=src/my_project/ui/preferences \
  --cov-report=term-missing --cov-fail-under=80
```

Do NOT measure the whole package (`--cov=src/my_project`). It will fail
because the UI modules are not exercised by unit tests.

---

## 5. Debian packaging (`.deb`)

If you build a `.deb`, follow these rules:

### `debian/control`
```text
Build-Depends: debhelper-compat (= 13),
               dh-python,
               pybuild-plugin-pyproject,   # <-- REQUIRED
               python3,
               python3-setuptools
```

### `debian/rules`
```makefile
#!/usr/bin/make -f
export PYBUILD_NAME = my_project
# Do NOT set PYBUILD_SYSTEM = distutils

%:
	dh $@ --with python3 --buildsystem=pybuild
```

### Do NOT create `setup.py`
The `setup.py` file will cause pybuild to use the legacy `distutils` plugin,
which will fail on the CI runner because the apt-provided setuptools is too
old for the `license = "SPDX"` string format.

If you already have a `setup.py`, **delete it**.

### `pyproject.toml` license
Use `license = { file = "COPYING" }` instead of `license = "SPDX-id"`.
The old setuptools on the runner rejects the string format.

---

## 6. GitHub Actions CI (automatic on push/PR)

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb libegl1 libxcb-cursor0 libgl1 libxkbcommon-x11-0

      - name: Install project
        run: python3 -m pip install -e '.[dev]'

      - name: Lint
        run: ruff check src tests

      - name: Unit tests
        run: QT_QPA_PLATFORM=offscreen python3 -m pytest tests/unit

      # Integration tests (QGraphicsView) are NOT run in CI.
      # They abort on headless runners. Run them locally:
      #   xvfb-run -a python3 -m pytest tests/integration

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y xvfb libegl1 libxcb-cursor0 libgl1 libxkbcommon-x11-0
      - name: Install project
        run: python3 -m pip install -e '.[dev]'
      - name: Coverage report (critical modules)
        run: |
          QT_QPA_PLATFORM=offscreen python3 -m pytest tests/unit \
            --cov=src/my_project/document --cov=src/my_project/formats \
            --cov=src/my_project/assets \
            --cov=src/my_project/ui/commands --cov=src/my_project/ui/preferences \
            --cov-report=term-missing --cov-fail-under=80
```

---

## 7. GitHub Actions build.yml (manual workflow)

For distributing executables, create a **manual** workflow (`workflow_dispatch`)
that produces the artifacts. Key points:

- **Windows** (Nuitka): no UPX, no admin, embedded metadata, icon, no console
  window. Generate `.ico` with Pillow.
- **macOS** (PyInstaller): `-w -D`, `--osx-bundle-identifier`, hidden-imports
  for all PyQt6 submodules, `.icns` icon generated with `iconutil`.
- **Linux**: wheel + `.deb` (Debian packaging) + optional Flatpak.
- **Flatpak**: manifest at `packaging/`, with `"path": ".."` for the project
  source and `"../data/doodle"` for assets.

Reference the exact scripts in `packaging/`:
- `packaging/build_windows.ps1` (Nuitka)
- `packaging/build_macos.sh` (PyInstaller)
- `packaging/requirements-windows.txt`
- `packaging/requirements-macos.txt`

---

## 8. .gitignore

```gitignore
__pycache__/
*.py[cod]
.coverage
.pytest_cache/
.ruff_cache/
.mypy_cache/
.hypothesis/
build/
dist/
*.egg-info/

# Compiled translation catalogs
translations/*.qm

# Debian package build artefacts
debian/.debhelper/
debian/tbo/
debian/files
debian/*.debhelper.log
debian/*.substvars

# pybuild temporary directory
.pybuild/

# Debian package build artefacts (generated in the repository root)
*.deb
*.buildinfo
*.changes
```

---

## 9. Summary of what NOT to do

| ❌ Do not | ✅ Do instead |
|-----------|-------------|
| Create `setup.py` | Use only `pyproject.toml` |
| Add `license = "GPL-3.0-or-later"` (string) | Add `license = { file = "COPYING" }` |
| Set `PYBUILD_SYSTEM = distutils` | Let pybuild auto-detect pyproject |
| Omit `pybuild-plugin-pyproject` from Build-Depends | Add it to `debian/control` |
| Omit `libegl1 libxcb-cursor0 libgl1 libxkbcommon-x11-0` | Install them in CI |
| Run `pytest tests/unit` without `QT_QPA_PLATFORM=offscreen` | Prefix with env var |
| Run integration tests in CI (QGraphicsView) | Keep them local-only |
| Measure `--cov=src/my_project` globally | Measure only critical modules |
| Use `fail-under` in `pyproject.toml` | Set it only in CI per-module |
| Omit `hypothesis` from dev deps | Add it if you have fuzz tests |

---

Follow these instructions in order. If a CI job fails, copy the exact error
log from the failing job and ask the agent to fix it.