# VirusTotal results

Screenshots of the VirusTotal reports for the four release artifacts, taken on
**2026-10-14**. They are published here so that anyone can check the binaries
before running them, and so the scans can be cited rather than described.

Every artifact scored **zero detections**.

| Artifact | Platform | Result | VirusTotal report |
|---|---|---|---|
| `TBO-2.0.0.dev0-x86_64.AppImage` | Linux (AppImage) | **0 / 64** | [report](https://www.virustotal.com/gui/file/c065c1c388dc82d02b1ea4354b478d6d5dc0c12caf41e7588a541eb11fdba70e) |
| `tbo_2.0.0.dev0-1_all.deb` | Linux (Debian package) | **0 / 61** | [report](https://www.virustotal.com/gui/file/444c47fdededcf5bfa98e5c482fc794b4985b023dc234e335a41375bc4580d02) |
| `tbo-macos.zip` | macOS | **0 / 73** | [report](https://www.virustotal.com/gui/file/22d5d093df1989e28e45071d9a551e19e62a83a1c252bebeee09ec4eb1bd6275) |
| `TBO-2.0.0.dev0-Windows-x64-portable.zip` | Windows | **0 / 66** | [report](https://www.virustotal.com/gui/file/1dc53738c2096ec94acbddac6a3e3c40950bd004d894b27bfd9f58d4a649feac) |

The screenshots in this directory are the source for those rows:

| Screenshot | Artifact |
|---|---|
| [`linux-appimage-0-of-64.png`](linux-appimage-0-of-64.png) | AppImage |
| [`linux-deb-0-of-61.png`](linux-deb-0-of-61.png) | `.deb` |
| [`macos-0-of-73.png`](macos-0-of-73.png) | macOS |
| [`windows-portable-0-of-66.png`](windows-portable-0-of-66.png) | Windows portable |

## Verify it yourself

A screenshot is a claim. The point of the SHA-256 column below is that you do not
have to trust one: download the release asset, hash it, and open the report for
that exact hash.

```bash
sha256sum TBO-2.0.0.dev0-x86_64.AppImage
# c065c1c388dc82d02b1ea4354b478d6d5dc0c12caf41e7588a541eb11fdba70e
# then open https://www.virustotal.com/gui/file/<that hash>
```

| Artifact | SHA-256 |
|---|---|
| `TBO-2.0.0.dev0-x86_64.AppImage` | `c065c1c388dc82d02b1ea4354b478d6d5dc0c12caf41e7588a541eb11fdba70e` |
| `tbo_2.0.0.dev0-1_all.deb` | `444c47fdededcf5bfa98e5c482fc794b4985b023dc234e335a41375bc4580d02` |
| `tbo-macos.zip` | `22d5d093df1989e28e45071d9a551e19e62a83a1c252bebeee09ec4eb1bd6275` |
| `TBO-2.0.0.dev0-Windows-x64-portable.zip` | `1dc53738c2096ec94acbddac6a3e3c40950bd004d894b27bfd9f58d4a649feac` |

The SHA-256 values above were recomputed from the release assets, so the hash and
the report refer to the same bytes.

## Read the numbers honestly

Two caveats, because a scan that overstates its own strength is worthless:

- **VirusTotal aggregates other vendors' verdicts; it produces none of its own.**
  It says so in its documentation. A zero here means that no engine *currently*
  has a signature matching this file — not that the file has been audited.
- **Some engines never judged these files.** Scanning an AppImage or a `.deb`
  leaves several Windows-only engines at "Unable to process this file type", and
  the `.zip` submissions show "Timeout" for some engines. The totals above are
  therefore smaller than the number of engines listed on the page. Look at the
  screenshots: a clean row is one that says **Undetected**, not one that says
  Timeout.

A scan is a **point-in-time signal**. Engines update, and results drift, in both
directions; these screenshots record 2026-10-14 and nothing more.

## How these artifacts were built

All four come from the same tagged source, built by GitHub Actions on the
project's own runners. The build is reproducible from the public workflow in
[`.github/workflows/build.yml`](../../.github/workflows/build.yml):

| Platform | Tool | Job |
|---|---|---|
| Windows | Nuitka | `build-windows` |
| macOS | PyInstaller | `build-macos` |
| Linux AppImage | PyInstaller + appimagetool | `build-appimage` |
| Linux `.deb` | debhelper / pybuild | `build-deb` |

Source, workflow and artifacts are all public: the binaries can be rebuilt from
this repository, which is a stronger statement than any scan result.

## If a detection appears

Engines do occasionally flag legitimate software — a shared compiler stub or an
unusual archive shape is enough. If you see a detection on a later build, please
report it in the [issue tracker](https://github.com/wachin/TBO/issues) with the
report link. False positives are reported to the vendor concerned, which is the
only way they get fixed; rebuilding or altering the binary to silence a scanner
is not something this project does.
