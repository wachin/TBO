# Creating your own characters and assets

TBO 2 loads **SVG files directly** — there is no conversion step. Anything you
drop into an asset folder is scanned automatically and appears in the Asset
Library, ready to be dragged into your comics.

This guide explains where to put files, what layout to use, and the design
policies that make a buildable character look right.

---

## 1. Where to put your SVG files

### Portable / development mode (running from the repository)

The repository ships a `doodle` tree at the top level:

```text
<repository>/data/doodle/
```

Anything you add there is picked up on the next launch. Because this folder is
part of the source tree, it is the right place when you want the assets to be
**distributed with the application**.

### User data (without touching the repository)

If you do not want to modify the project (for example because you installed the
package), put your files in one of the user data directories:

```text
~/.tbo/doodle/
~/.local/share/tbo/doodle/
```

Both are scanned automatically. The application does **not** create these
folders; you must create them yourself.

> Custom files are **merged** with the shipped ones: if you add an SVG under
> `~/.tbo/doodle/head/eyes/`, it appears in the same **eyes** category as the
> bundled eyes.

---

## 2. Folder layout

The first-level directory under a `doodle` root becomes a **category** (shown as
a toolbox page inside a tab). Subdirectories become **parts** of that category.

```text
doodle/
├── bubble/            # speech bubbles (always a separate "Bubbles" tab)
│   ├── square/
│   ├── ellipse/
│   └── misc/
├── head/              # the buildable character
│   ├── head.svg       #   the face with NO features
│   ├── eyes/          #   the eye set
│   │   ├── normal.svg
│   │   └── happy.svg
│   ├── mouth/         #   mouths
│   ├── ears/          #   ears
│   ├── noses/         #   you can add these yourself
│   ├── eyebrows/
│   ├── eyelashes/
│   └── lips/
└── my_character/      # a fully custom category you create
    ├── character.svg
    └── accessories/
```

The Asset Library tabs map to:

| Tab            | Content                                          |
|----------------|--------------------------------------------------|
| Doodles        | every first-level category except `head` and `accesories` |
| Character      | the `head` category, split into its parts        |
| Accessories    | the `accesories` category, split into its parts  |
| Bubbles        | the `bubble` category                            |

So if you create a brand-new character, name its top-level folder something
other than `head` and it will appear under **Doodles**; its subfolders (eyes,
mouth, ...) will be listed as parts inside that category.

---

## 3. File policies

### Format

- Files must be valid **SVG** (`*.svg`). Use a `viewBox` (not just `width` /
  `height`) so the renderer can scale them to any size.
- The XML must be well formed. An unreadable file is drawn as a dashed red
  rectangle instead of crashing the application.

### Sizes and the viewBox

The application scales every SVG to fit its target object, keeping the
`viewBox` aspect ratio. For a buildable character the important rule is:

> **All parts of the same character must share the same viewBox width**
> (or use matching proportions), so the eyes, mouth, ears, etc. align with the
> head when inserted at the same size.

The shipped example uses these coordinates:

| Part       | viewBox        | Notes                                     |
|------------|----------------|-------------------------------------------|
| head       | `0 0 200 200`  | square; the face is a centered shape      |
| ears       | `0 0 200 200`  | same box as the head, placed at the sides |
| eyes       | `0 0 200 80`   | width equals the head width               |
| mouth      | `0 0 200 80`   | width equals the head width               |
| noses      | `0 0 200 60`   | recommended                               |
| eyebrows   | `0 0 200 60`   | recommended                               |
| eyelashes  | `0 0 200 80`   | recommended                               |
| lips       | `0 0 200 70`   | recommended                               |

Using `200` as the width for every part of a character makes them interchangeable:
you can mix and match eyes, mouths and ears freely.

### Colors

Keep the skin color consistent across the head and the ears of a character. The
shipped example uses `#f2c9a0` with a `#c9a97a` outline.

### A blank head

The head must **not** contain eyes, mouth, nose or ears — those are separate
parts the user drags on top. Only draw the face outline (and optional hair,
cheeks, etc.).

---

## 4. Creating a character from scratch

If none of the shipped characters appeal to you, build your own with any SVG
editor (Inkscape, Illustrator, or a text editor):

1. Create the **head**: a `200 × 200` box with just the face outline.
2. Create the **parts**, each `200` wide:
   - eyes (one SVG containing both eyes, centered);
   - one mouth per expression;
   - ears (both ears in a single `200 × 200` SVG);
   - noses, eyebrows, eyelashes, lips — one file per variant.
3. Put them in a folder, e.g. `~/.tbo/doodle/my_character/eyes/`.
4. Launch TBO 2. The folder appears in the Asset Library automatically.

Alternatively, copy the shipped character:

```bash
mkdir -p ~/.tbo/doodle
cp -r <repository>/data/doodle/head ~/.tbo/doodle/
```

and edit the SVGs to your liking — your copies will be merged with the originals.

---

## 5. Using the parts in a comic

1. Double-click a panel to enter its editing mode.
2. In the Asset Library, click (or drag) the **head** first, then the parts.
3. Position the eyes, mouth, ears, nose, etc. over the head.
4. Rotate with `[` / `]`, flip with `H` / `V`, resize by dragging the yellow
   handle, and arrange with the Align/Distribute menu.

Everything is saved in the `.tbo` file and exported to PNG/PDF/SVG as-is.
