#!/usr/bin/env python3
"""Generate .ico (Windows) and .icns (macOS) icons from the application icon."""

import struct
import sys
from pathlib import Path

from PIL import Image


def build_ico(source: Path, target: Path) -> None:
    img = Image.open(source)
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        images.append(resized)
    images[0].save(target, format="ICO", sizes=[(i.width, i.height) for i in images])
    print(f"  ICO: {target}")


def build_iconset(source: Path, iconset_dir: Path) -> None:
    iconset_dir.mkdir(parents=True, exist_ok=True)
    names = {
        (16, 1): "icon_16x16.png",
        (32, 1): "icon_16x16@2x.png",
        (32, 1): "icon_32x32.png",
        (64, 1): "icon_32x32@2x.png",
        (128, 1): "icon_128x128.png",
        (256, 1): "icon_128x128@2x.png",
        (256, 1): "icon_256x256.png",
        (512, 1): "icon_256x256@2x.png",
        (512, 1): "icon_512x512.png",
        (1024, 1): "icon_512x512@2x.png",
    }
    img = Image.open(source)
    for (size, scale), filename in names.items():
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset_dir / filename)
    print(f"  iconset: {iconset_dir}")


def main() -> None:
    source = Path(sys.argv[1])
    if not source.is_file():
        sys.exit(f"Source file not found: {source}")
    mode = sys.argv[2] if len(sys.argv) > 2 else "all"
    if mode in ("ico", "all"):
        build_ico(source, source.with_suffix(".ico"))
    if mode in ("iconset", "all"):
        iconset_dir = source.with_suffix(".iconset")
        build_iconset(source, iconset_dir)


if __name__ == "__main__":
    main()