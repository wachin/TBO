<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1" language="en_US" sourcelanguage="en">
 <context>
  <name>AboutDialog</name>
  <message>
   <location filename="../src/tbo/ui/about_dialog.py" line="87" />
   <source>About TBO</source>
   <translation>About TBO</translation>
  </message>
 </context>
 <context>
  <name>Application</name>
  <message>
   <location filename="../src/tbo/application.py" line="62" />
   <source>Untitled</source>
   <translation>Untitled</translation>
  </message>
 </context>
 <context>
  <name>AssetsDock</name>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="137" />
   <source>Asset Library</source>
   <translation>Asset Library</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="157" />
   <source>Doodles</source>
   <translation>Doodles</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="158" />
   <source>Character</source>
   <translation>Character</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="159" />
   <source>Accessories</source>
   <translation>Accessories</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="160" />
   <source>Bubbles</source>
   <translation>Bubbles</translation>
  </message>
 </context>
 <context>
  <name>ComicCanvas</name>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="529" />
   <source>Paste panels</source>
   <translation>Paste panels</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="539" />
   <source>Paste objects</source>
   <translation>Paste objects</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="552" />
   <source>Delete panels</source>
   <translation>Delete panels</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="600" />
   <source>Clone panel</source>
   <translation>Clone panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="637" />
   <source>Clone object</source>
   <translation>Clone object</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="665" />
   <source>Delete objects</source>
   <translation>Delete objects</translation>
  </message>
 </context>
 <context>
  <name>ExportDialog</name>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="29" />
   <source>Export Options</source>
   <translation>Export Options</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="37" />
   <source>All pages ({count})</source>
   <translation>All pages ({count})</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="39" />
   <source>Current page ({index} of {count})</source>
   <translation>Current page ({index} of {count})</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="48" />
   <source>Output resolution for PNG export</source>
   <translation>Output resolution for PNG export</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="52" />
   <source>Format:</source>
   <translation>Format:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="53" />
   <source>Range:</source>
   <translation>Range:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="54" />
   <source>Scale:</source>
   <translation>Scale:</translation>
  </message>
 </context>
 <context>
  <name>HelpDialog</name>
  <message>
   <location filename="../src/tbo/ui/help_dialog.py" line="15" />
   <source>TBO Help</source>
   <translation>TBO Help</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/help_dialog.py" line="33" />
   <source># TBO 2 — Help

## Where are the `.tbo` files?

TBO documents are complete comic files (pages, panels and objects). The
distribution includes two examples:

- `data/tut.tbo` — the tutorial.
- `doc/pres-final.tbo` — a presentation example.

## Where are the characters (doodles and speech bubbles)?

There is no `.tbo` file per character. Characters, decorations and speech
bubbles are **SVG files** shipped under the `doodle` directory, organised by
category (body, eyes, mouth, accessories, characters, etc.).

To use them:

1. **Double-click a panel** to enter its editing mode.
2. In the **Asset Library** dock on the right, choose the **Doodles** tab
   (decorations and characters), **Character** (buildable head parts),
   **Accessories** (actions, devices, emotes, pcs) or **Bubbles** (speech
   bubbles).
3. Type in the search box or browse the categories.
4. **Click or drag** a thumbnail to insert it into the panel.

Everything you insert can be moved, resized, rotated, flipped, cloned and
deleted, and is saved in the `.tbo` file.

## How does the last-folder memory work?

The program remembers the last folder you used. When you open, save, export or
import a file, that folder is saved. The next time you open **Open**, **Save
As**, **Export**, **Add Image** or **Add SVG**, the dialog starts in that
folder. The first time, with no history, it starts in your home directory
(`~`).

## Multi-selection, alignment and distribution

Hold **`Ctrl`** while clicking several panels or objects, or drag a rectangle
on the canvas, to select them at once. **`Ctrl+A`** selects all panels on a
page, or all objects inside a panel.

Hold the **space bar** and drag to pan the view without moving the selection
(Inkscape-style).

Use the **Flip** buttons on the toolbar (or `H` / `V`) to mirror a bubble or
object horizontally or vertically — for example, to point the bubble tail
toward the character's mouth.

With several items selected you can:

- Press **`Delete`** to remove them all in one step (reversible with undo).
- Use the **Edit ▸ Align** menu (left, center, right, top, etc.) to align the
  selected panels.
- Use **Edit ▸ Distribute** to space them evenly.

To **copy and paste** between pages use **`Ctrl+C`** and **`Ctrl+V`**: copy
panels (on the page) or objects (inside a panel) and paste them on the current
page or panel.

## Drag from the library

Besides clicking a thumbnail, you can **drag** it from the Asset Library and
**drop** it into the panel you are editing.

## Adding your own drawings (SVG)

You can create your own eyes, mouths, ears, noses, eyebrows, eyelashes, lips,
or any other element in **SVG** and the program will load them automatically.
No conversion is needed — the program uses SVGs directly.

Just place your **.svg** files in one of these folders (the program does not
create them, you must):

- `~/.tbo/doodle/` (e.g. `~/.tbo/doodle/head/eyes/my_eyes.svg`)
- `~/.local/share/tbo/doodle/`

Organise them by folder the same way as the example character (e.g.
`head/eyes/`, `head/mouths/`, `noses/`). The program will merge them with the
shipped resources and show them in the corresponding tab.

## Buildable character

The **Character** tab in the library contains an example buildable character
made of independent parts you can combine at will:

- **Head**: a blank face (no eyes, ears or mouth).
- **Eyes**: normal, happy, sad, closed, surprised…
- **Mouth**: smile, neutral, sad, open, tongue…
- **Ears**: normal, pointy.

Place the head first, then drag each part into position. You can use **Rotate**
(`[` / `]`), **Flip** (`H` / `V`), **Resize** (drag the bottom-right handle)
and mix any expressions you like.

## Presentation and export

- Press **`F5`** (View ▸ Presentation) to read the comic in full screen.
  Navigate with the arrow keys, `Space` or `Page Up`/`Page Down`; exit with
  `Esc`.
- **Export** (`Ctrl+E`) lets you choose the format, whether to export all pages
  or only the current one, and the output scale (up to 1000 %) for PNG.

## Theme, grid and session

- **View ▸ Theme**: choose **System**, **Dark** or **Light**. The choice is
  remembered between sessions.
- **View ▸ Snap to Grid**: when active, panels snap to a 10 px grid while
  moving or resizing, and the grid is shown on the canvas. Also remembered.
- The program **reopens the last document** you had open when you close it.

## Pages and search

- The **Pages** dock on the left shows a **thumbnail** of every page; click one
  to jump to it. Thumbnails refresh as the comic is edited.
- **Edit ▸ Find Text…** (`Ctrl+F`) searches every text object in the document
  and navigates to the page and panel containing a match.

## Useful shortcuts

| Shortcut | Action |
| -------- | ------ |
| `Ctrl+N` | New comic |
| `Ctrl+O` | Open |
| `Ctrl+S` | Save |
| `Ctrl+E` | Export |
| `Page Up` / `Page Down` | Previous / next page |
| `F` | Add panel (on the page) |
| Double-click panel | Edit its contents |
| `T` | Add text (while editing a panel) |
| `Esc` | Leave panel editing |
| `Ctrl+D` | Clone selected panel / object |
| `Ctrl+C` / `Ctrl+V` | Copy / paste panels or objects |
| `Ctrl` + click / drag | Multi-select |
| `Ctrl+A` | Select all |
| `Space` + drag | Pan the view |
| `Delete` | Delete selected panel(s) / object(s) |
| `[` / `]` | Rotate object left / right |
| `H` / `V` | Flip object horizontally / vertically |
| `Ctrl` + wheel, `+` / `-` / `1` / `2` | Zoom in / out / actual size / fit page |
| `F5` | Full-screen presentation |
| `Ctrl+F` | Find text in the document |
| `Ctrl+Z` / `Ctrl+Shift+Z` | Undo / redo |
</source>
   <translation># TBO 2 — Help

## Where are the `.tbo` files?

TBO documents are complete comic files (pages, panels and objects). The
distribution includes two examples:

- `data/tut.tbo` — the tutorial.
- `doc/pres-final.tbo` — a presentation example.

## Where are the characters (doodles and speech bubbles)?

There is no `.tbo` file per character. Characters, decorations and speech
bubbles are **SVG files** shipped under the `doodle` directory, organised by
category (body, eyes, mouth, accessories, characters, etc.).

To use them:

1. **Double-click a panel** to enter its editing mode.
2. In the **Asset Library** dock on the right, choose the **Doodles** tab
   (decorations and characters), **Character** (buildable head parts),
   **Accessories** (actions, devices, emotes, pcs) or **Bubbles** (speech
   bubbles).
3. Type in the search box or browse the categories.
4. **Click or drag** a thumbnail to insert it into the panel.

Everything you insert can be moved, resized, rotated, flipped, cloned and
deleted, and is saved in the `.tbo` file.

## How does the last-folder memory work?

The program remembers the last folder you used. When you open, save, export or
import a file, that folder is saved. The next time you open **Open**, **Save
As**, **Export**, **Add Image** or **Add SVG**, the dialog starts in that
folder. The first time, with no history, it starts in your home directory
(`~`).

## Multi-selection, alignment and distribution

Hold **`Ctrl`** while clicking several panels or objects, or drag a rectangle
on the canvas, to select them at once. **`Ctrl+A`** selects all panels on a
page, or all objects inside a panel.

Hold the **space bar** and drag to pan the view without moving the selection
(Inkscape-style).

Use the **Flip** buttons on the toolbar (or `H` / `V`) to mirror a bubble or
object horizontally or vertically — for example, to point the bubble tail
toward the character's mouth.

With several items selected you can:

- Press **`Delete`** to remove them all in one step (reversible with undo).
- Use the **Edit ▸ Align** menu (left, center, right, top, etc.) to align the
  selected panels.
- Use **Edit ▸ Distribute** to space them evenly.

To **copy and paste** between pages use **`Ctrl+C`** and **`Ctrl+V`**: copy
panels (on the page) or objects (inside a panel) and paste them on the current
page or panel.

## Drag from the library

Besides clicking a thumbnail, you can **drag** it from the Asset Library and
**drop** it into the panel you are editing.

## Adding your own drawings (SVG)

You can create your own eyes, mouths, ears, noses, eyebrows, eyelashes, lips,
or any other element in **SVG** and the program will load them automatically.
No conversion is needed — the program uses SVGs directly.

Just place your **.svg** files in one of these folders (the program does not
create them, you must):

- `~/.tbo/doodle/` (e.g. `~/.tbo/doodle/head/eyes/my_eyes.svg`)
- `~/.local/share/tbo/doodle/`

Organise them by folder the same way as the example character (e.g.
`head/eyes/`, `head/mouths/`, `noses/`). The program will merge them with the
shipped resources and show them in the corresponding tab.

## Buildable character

The **Character** tab in the library contains an example buildable character
made of independent parts you can combine at will:

- **Head**: a blank face (no eyes, ears or mouth).
- **Eyes**: normal, happy, sad, closed, surprised…
- **Mouth**: smile, neutral, sad, open, tongue…
- **Ears**: normal, pointy.

Place the head first, then drag each part into position. You can use **Rotate**
(`[` / `]`), **Flip** (`H` / `V`), **Resize** (drag the bottom-right handle)
and mix any expressions you like.

## Presentation and export

- Press **`F5`** (View ▸ Presentation) to read the comic in full screen.
  Navigate with the arrow keys, `Space` or `Page Up`/`Page Down`; exit with
  `Esc`.
- **Export** (`Ctrl+E`) lets you choose the format, whether to export all pages
  or only the current one, and the output scale (up to 1000 %) for PNG.

## Theme, grid and session

- **View ▸ Theme**: choose **System**, **Dark** or **Light**. The choice is
  remembered between sessions.
- **View ▸ Snap to Grid**: when active, panels snap to a 10 px grid while
  moving or resizing, and the grid is shown on the canvas. Also remembered.
- The program **reopens the last document** you had open when you close it.

## Pages and search

- The **Pages** dock on the left shows a **thumbnail** of every page; click one
  to jump to it. Thumbnails refresh as the comic is edited.
- **Edit ▸ Find Text…** (`Ctrl+F`) searches every text object in the document
  and navigates to the page and panel containing a match.

## Useful shortcuts

| Shortcut | Action |
| -------- | ------ |
| `Ctrl+N` | New comic |
| `Ctrl+O` | Open |
| `Ctrl+S` | Save |
| `Ctrl+E` | Export |
| `Page Up` / `Page Down` | Previous / next page |
| `F` | Add panel (on the page) |
| Double-click panel | Edit its contents |
| `T` | Add text (while editing a panel) |
| `Esc` | Leave panel editing |
| `Ctrl+D` | Clone selected panel / object |
| `Ctrl+C` / `Ctrl+V` | Copy / paste panels or objects |
| `Ctrl` + click / drag | Multi-select |
| `Ctrl+A` | Select all |
| `Space` + drag | Pan the view |
| `Delete` | Delete selected panel(s) / object(s) |
| `[` / `]` | Rotate object left / right |
| `H` / `V` | Flip object horizontally / vertically |
| `Ctrl` + wheel, `+` / `-` / `1` / `2` | Zoom in / out / actual size / fit page |
| `F5` | Full-screen presentation |
| `Ctrl+F` | Find text in the document |
| `Ctrl+Z` / `Ctrl+Shift+Z` | Undo / redo |
</translation>
  </message>
 </context>
 <context>
  <name>MainWindow</name>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="60" />
   <source>100%</source>
   <translation>100%</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="69" />
   <source>&amp;File</source>
   <translation>&amp;File</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="70" />
   <source>&amp;New…</source>
   <translation>&amp;New…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="73" />
   <source>New</source>
   <translation>New</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="77" />
   <source>&amp;Open…</source>
   <translation>&amp;Open…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="80" />
   <source>Open</source>
   <translation>Open</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="84" />
   <source>&amp;Save</source>
   <translation>&amp;Save</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="87" />
   <source>Save</source>
   <translation>Save</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="92" />
   <source>Save &amp;As…</source>
   <translation>Save &amp;As…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="95" />
   <source>Save As</source>
   <translation>Save As</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="100" />
   <source>&amp;Export…</source>
   <translation>&amp;Export…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="107" />
   <source>&amp;Recent Files</source>
   <translation>&amp;Recent Files</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="111" />
   <source>&amp;Edit</source>
   <translation>&amp;Edit</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="112" />
   <source>&amp;Undo</source>
   <translation>&amp;Undo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="115" />
   <source>Undo</source>
   <translation>Undo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="117" />
   <source>&amp;Redo</source>
   <translation>&amp;Redo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="120" />
   <source>Redo</source>
   <translation>Redo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="123" />
   <source>&amp;Copy</source>
   <translation>&amp;Copy</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="127" />
   <source>&amp;Paste</source>
   <translation>&amp;Paste</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="133" />
   <source>Select &amp;All</source>
   <translation>Select &amp;All</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="139" />
   <source>Add &amp;Panel</source>
   <translation>Add &amp;Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="142" />
   <source>Add Panel</source>
   <translation>Add Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="145" />
   <source>&amp;Delete Panel</source>
   <translation>&amp;Delete Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="150" />
   <source>&amp;Clone Panel</source>
   <translation>&amp;Clone Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="155" />
   <source>Leave Panel</source>
   <translation>Leave Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="160" />
   <source>Ali&amp;gn</source>
   <translation>Ali&amp;gn</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="161" />
   <source>Left</source>
   <translation>Left</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="164" />
   <source>Horizontal Center</source>
   <translation>Horizontal Center</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="167" />
   <source>Right</source>
   <translation>Right</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="171" />
   <source>Top</source>
   <translation>Top</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="174" />
   <source>Vertical Center</source>
   <translation>Vertical Center</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="177" />
   <source>Bottom</source>
   <translation>Bottom</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="181" />
   <source>&amp;Distribute</source>
   <translation>&amp;Distribute</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="182" />
   <source>Horizontally</source>
   <translation>Horizontally</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="185" />
   <source>Vertically</source>
   <translation>Vertically</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="190" />
   <source>Add &amp;Text…</source>
   <translation>Add &amp;Text…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="193" />
   <source>Add Text</source>
   <translation>Add Text</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="197" />
   <source>Add &amp;Image…</source>
   <translation>Add &amp;Image…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="201" />
   <source>Add &amp;SVG…</source>
   <translation>Add &amp;SVG…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="206" />
   <source>Rotate &amp;Left</source>
   <translation>Rotate &amp;Left</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="211" />
   <source>Rotate &amp;Right</source>
   <translation>Rotate &amp;Right</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="216" />
   <source>Flip &amp;Horizontally</source>
   <translation>Flip &amp;Horizontally</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="219" />
   <source>Flip Horizontally</source>
   <translation>Flip Horizontally</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="223" />
   <source>Flip &amp;Vertically</source>
   <translation>Flip &amp;Vertically</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="226" />
   <source>Flip Vertically</source>
   <translation>Flip Vertically</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="230" />
   <source>Edit &amp;Text…</source>
   <translation>Edit &amp;Text…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="236" />
   <source>&amp;Find Text…</source>
   <translation>&amp;Find Text…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="254" />
   <source>&amp;Page</source>
   <translation>&amp;Page</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="255" />
   <source>&amp;Previous Page</source>
   <translation>&amp;Previous Page</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="260" />
   <source>&amp;Next Page</source>
   <translation>&amp;Next Page</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="266" />
   <source>Add Page</source>
   <translation>Add Page</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="271" />
   <source>Delete Page</source>
   <translation>Delete Page</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="276" />
   <source>Move Page Left</source>
   <translation>Move Page Left</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="281" />
   <source>Move Page Right</source>
   <translation>Move Page Right</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="286" />
   <source>&amp;View</source>
   <translation>&amp;View</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="290" />
   <location filename="../src/tbo/ui/main_window.py" line="287" />
   <source>Fit Page</source>
   <translation>Fit Page</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="297" />
   <location filename="../src/tbo/ui/main_window.py" line="294" />
   <source>Zoom In</source>
   <translation>Zoom In</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="304" />
   <location filename="../src/tbo/ui/main_window.py" line="301" />
   <source>Zoom Out</source>
   <translation>Zoom Out</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="311" />
   <location filename="../src/tbo/ui/main_window.py" line="308" />
   <source>Actual Size</source>
   <translation>Actual Size</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="315" />
   <source>&amp;Presentation…</source>
   <translation>&amp;Presentation…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="320" />
   <source>S&amp;nap to Grid</source>
   <translation>S&amp;nap to Grid</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="326" />
   <source>&amp;Theme</source>
   <translation>&amp;Theme</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="331" />
   <source>System</source>
   <translation>System</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="332" />
   <source>Dark</source>
   <translation>Dark</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="333" />
   <source>Light</source>
   <translation>Light</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="344" />
   <source>&amp;Help</source>
   <translation>&amp;Help</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="345" />
   <source>&amp;Help Contents</source>
   <translation>&amp;Help Contents</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="350" />
   <source>&amp;About TBO</source>
   <translation>&amp;About TBO</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="371" />
   <source>Main Toolbar</source>
   <translation>Main Toolbar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="400" />
   <source>Open Comic</source>
   <translation>Open Comic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="402" />
   <source>TBO Files (*.tbo);;All Files (*)</source>
   <translation>TBO Files (*.tbo);;All Files (*)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="422" />
   <source>Could Not Open File</source>
   <translation>Could Not Open File</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="456" />
   <source>Save Comic</source>
   <translation>Save Comic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="456" />
   <source>TBO Files (*.tbo)</source>
   <translation>TBO Files (*.tbo)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="488" />
   <source>Export Comic</source>
   <translation>Export Comic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="514" />
   <source>Could Not Export</source>
   <translation>Could Not Export</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="519" />
   <source>Exported {count} file(s)</source>
   <translation>Exported {count} file(s)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="587" />
   <source>File Not Found</source>
   <translation>File Not Found</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="588" />
   <source>{filename} no longer exists.</source>
   <translation>{filename} no longer exists.</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="602" />
   <source>Could Not Save File</source>
   <translation>Could Not Save File</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="613" />
   <source>Saved to {filename}</source>
   <translation>Saved to {filename}</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="653" />
   <source>Unsaved Changes</source>
   <translation>Unsaved Changes</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="654" />
   <source>The document has unsaved changes. Do you want to save them before continuing?</source>
   <translation>The document has unsaved changes. Do you want to save them before continuing?</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="830" />
   <source>Add Image</source>
   <translation>Add Image</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="832" />
   <source>Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)</source>
   <translation>Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="841" />
   <source>Could Not Add Image</source>
   <translation>Could Not Add Image</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="842" />
   <source>The selected file is not a supported or readable image.</source>
   <translation>The selected file is not a supported or readable image.</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="848" />
   <source>Add SVG</source>
   <translation>Add SVG</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="850" />
   <source>SVG Files (*.svg);;All Files (*)</source>
   <translation>SVG Files (*.svg);;All Files (*)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="859" />
   <source>Could Not Add SVG</source>
   <translation>Could Not Add SVG</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="860" />
   <source>The selected file is not a valid SVG image.</source>
   <translation>The selected file is not a valid SVG image.</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="942" />
   <source>Delete Object</source>
   <translation>Delete Object</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="942" />
   <source>Delete Panel</source>
   <translation>Delete Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="945" />
   <source>Clone Object</source>
   <translation>Clone Object</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="945" />
   <source>Clone Panel</source>
   <translation>Clone Panel</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="982" />
   <source>{percent}%</source>
   <translation>{percent}%</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="1008" />
   <source>Editing panel — press Esc to return · Page {current} of {count}</source>
   <translation>Editing panel — press Esc to return · Page {current} of {count}</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="1013" />
   <source>Page {current} of {count}</source>
   <translation>Page {current} of {count}</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="1017" />
   <source>Document has no pages</source>
   <translation>Document has no pages</translation>
  </message>
 </context>
 <context>
  <name>NewComicDialog</name>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="19" />
   <source>New comic</source>
   <translation>New comic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="48" />
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="21" />
   <source>Untitled</source>
   <translation>Untitled</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="33" />
   <source>Title:</source>
   <translation>Title:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="34" />
   <source>Width:</source>
   <translation>Width:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="35" />
   <source>Height:</source>
   <translation>Height:</translation>
  </message>
 </context>
 <context>
  <name>PagesDock</name>
  <message>
   <location filename="../src/tbo/ui/pages_dock.py" line="30" />
   <source>Pages</source>
   <translation>Pages</translation>
  </message>
 </context>
 <context>
  <name>PresentationDialog</name>
  <message>
   <location filename="../src/tbo/ui/presentation.py" line="28" />
   <source>Presentation</source>
   <translation>Presentation</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/presentation.py" line="68" />
   <source>Presentation — Page {current} of {count}</source>
   <translation>Presentation — Page {current} of {count}</translation>
  </message>
 </context>
 <context>
  <name>SearchDialog</name>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="22" />
   <source>Find Text</source>
   <translation>Find Text</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="28" />
   <source>Search text in the document…</source>
   <translation>Search text in the document…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="39" />
   <source>Go to</source>
   <translation>Go to</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="63" />
   <source>Page {page}: {preview}</source>
   <translation>Page {page}: {preview}</translation>
  </message>
 </context>
 <context>
  <name>TextObjectDialog</name>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="22" />
   <source>Add Text</source>
   <translation>Add Text</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="26" />
   <source>Enter the text to place in the panel…</source>
   <translation>Enter the text to place in the panel…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="42" />
   <source>Font:</source>
   <translation>Font:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="43" />
   <source>Color:</source>
   <translation>Color:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="59" />
   <source>Choose Text Color</source>
   <translation>Choose Text Color</translation>
  </message>
 </context>
 <context>
  <name>_LibraryTab</name>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="51" />
   <source>Search…</source>
   <translation>Search…</translation>
  </message>
 </context>
</TS>