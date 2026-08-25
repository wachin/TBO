#!/usr/bin/env python3
"""Generate a small, geometric 'build-a-character' set of SVG parts.

Creates a plain head and separate eyes/mouth/ears with a few expressions so the
user can drag and combine them in their comics.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data" / "doodle" / "head"

SKIN = "#f2c9a0"
DARK = "#3a2a1a"
MOUTH = "#c0392b"

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>'


def write(name: str, vb: str, body: str) -> None:
    target = ROOT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(SVG.format(vb=vb, body=body), encoding="utf-8")
    print(f"  {target.relative_to(ROOT.parent.parent)}")


def main() -> None:
    write("head.svg", "0 0 200 200", f'<circle cx="100" cy="100" r="85" fill="{SKIN}" '
        'stroke="#c9a97a" stroke-width="3"/>')

    eyes_vb = "0 0 200 80"
    write("eyes/normal.svg", eyes_vb,
          f'<circle cx="60" cy="40" r="12" fill="{DARK}"/><circle cx="140" cy="40" r="12" fill="{DARK}"/>')
    write("eyes/happy.svg", eyes_vb,
          f'<path d="M 42 48 Q 60 24 78 48" stroke="{DARK}" stroke-width="6" fill="none" stroke-linecap="round"/>'
          f'<path d="M 122 48 Q 140 24 158 48" stroke="{DARK}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    write("eyes/sad.svg", eyes_vb,
          f'<circle cx="60" cy="44" r="11" fill="{DARK}"/><circle cx="140" cy="44" r="11" fill="{DARK}"/>'
          f'<path d="M 46 30 L 76 36" stroke="{DARK}" stroke-width="6" stroke-linecap="round"/>'
          f'<path d="M 124 36 L 154 30" stroke="{DARK}" stroke-width="6" stroke-linecap="round"/>')
    write("eyes/closed.svg", eyes_vb,
          f'<path d="M 42 40 Q 60 52 78 40" stroke="{DARK}" stroke-width="6" fill="none" stroke-linecap="round"/>'
          f'<path d="M 122 40 Q 140 52 158 40" stroke="{DARK}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    write("eyes/surprised.svg", eyes_vb,
          f'<circle cx="60" cy="40" r="18" fill="white" stroke="{DARK}" stroke-width="4"/>'
          f'<circle cx="60" cy="40" r="8" fill="{DARK}"/>'
          f'<circle cx="140" cy="40" r="18" fill="white" stroke="{DARK}" stroke-width="4"/>'
          f'<circle cx="140" cy="40" r="8" fill="{DARK}"/>')

    mouth_vb = "0 0 200 80"
    write("mouth/smile.svg", mouth_vb,
          f'<path d="M 55 30 Q 100 62 145 30" stroke="{MOUTH}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    write("mouth/neutral.svg", mouth_vb,
          f'<path d="M 55 40 L 145 40" stroke="{MOUTH}" stroke-width="7" stroke-linecap="round"/>')
    write("mouth/sad.svg", mouth_vb,
          f'<path d="M 55 50 Q 100 18 145 50" stroke="{MOUTH}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    write("mouth/open.svg", mouth_vb,
          f'<ellipse cx="100" cy="42" rx="26" ry="24" fill="#7a1f16" stroke="{MOUTH}" stroke-width="5"/>')
    write("mouth/tongue.svg", mouth_vb,
          f'<path d="M 55 30 Q 100 62 145 30" stroke="{MOUTH}" stroke-width="7" fill="none" stroke-linecap="round"/>'
          f'<ellipse cx="100" cy="52" rx="12" ry="14" fill="#e8779a"/>')

    ears_vb = "0 0 200 200"
    write("ears/normal.svg", ears_vb,
          f'<ellipse cx="6" cy="100" rx="14" ry="26" fill="{SKIN}" stroke="#c9a97a" stroke-width="3"/>'
          f'<ellipse cx="194" cy="100" rx="14" ry="26" fill="{SKIN}" stroke="#c9a97a" stroke-width="3"/>')
    write("ears/pointy.svg", ears_vb,
          f'<path d="M 10 96 L 4 60 L 30 92 Z" fill="{SKIN}" stroke="#c9a97a" stroke-width="3"/>'
          f'<path d="M 190 96 L 196 60 L 170 92 Z" fill="{SKIN}" stroke="#c9a97a" stroke-width="3"/>')


if __name__ == "__main__":
    main()
