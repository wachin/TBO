<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1">
 <context>
  <name>AboutDialog</name>
  <message>
   <location filename="../src/tbo/ui/about_dialog.py" line="87" />
   <source>About TBO</source>
   <translation>Acerca de TBO</translation>
  </message>
 </context>
 <context>
  <name>Application</name>
  <message>
   <location filename="../src/tbo/application.py" line="62" />
   <source>Untitled</source>
   <translation>Sin título</translation>
  </message>
 </context>
 <context>
  <name>AssetsDock</name>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="137" />
   <source>Asset Library</source>
   <translation>Biblioteca de recursos</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="157" />
   <source>Doodles</source>
   <translation>Doodles</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="158" />
   <source>Character</source>
   <translation>Personaje</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="159" />
   <source>Accessories</source>
   <translation>Accesorios</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="160" />
   <source>Bubbles</source>
   <translation>Bocadillos</translation>
  </message>
 </context>
 <context>
  <name>ComicCanvas</name>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="529" />
   <source>Paste panels</source>
   <translation>Pegar viñetas</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="539" />
   <source>Paste objects</source>
   <translation>Pegar objetos</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="552" />
   <source>Delete panels</source>
   <translation>Eliminar viñetas</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="600" />
   <source>Clone panel</source>
   <translation>Clonar viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="637" />
   <source>Clone object</source>
   <translation>Clonar objeto</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/canvas.py" line="665" />
   <source>Delete objects</source>
   <translation>Eliminar objetos</translation>
  </message>
 </context>
 <context>
  <name>ExportDialog</name>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="29" />
   <source>Export Options</source>
   <translation>Opciones de exportación</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="37" />
   <source>All pages ({count})</source>
   <translation>Todas las páginas ({count})</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="39" />
   <source>Current page ({index} of {count})</source>
   <translation>Página actual ({index} de {count})</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="48" />
   <source>Output resolution for PNG export</source>
   <translation>Resolución de salida para exportación PNG</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="52" />
   <source>Format:</source>
   <translation>Formato:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="53" />
   <source>Range:</source>
   <translation>Rango:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/export_dialog.py" line="54" />
   <source>Scale:</source>
   <translation>Escala:</translation>
  </message>
 </context>
 <context>
  <name>HelpDialog</name>
  <message>
   <location filename="../src/tbo/ui/help_dialog.py" line="15" />
   <source>TBO Help</source>
   <translation>Ayuda de TBO</translation>
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
   <translation># TBO 2 — Ayuda

## ¿Dónde están los archivos `.tbo`?

Los archivos `.tbo` son documentos de cómic completos (páginas, viñetas y
objetos). En la distribución solo se incluyen dos ejemplos:

- `data/tut.tbo` — el tutorial.
- `doc/pres-final.tbo` — un ejemplo de presentación.

## ¿Dónde están los personajes (doodles y bocadillos)?

No hay un archivo `.tbo` por personaje. Los personajes, adornos y bocadillos
son archivos **SVG** que se incluyen con el programa en el directorio `doodle`,
organizados por categorías (cuerpo, ojos, boca, accesorios, personajes, etc.).

Para usarlos:

1. **Entre en una viñeta** haciendo doble clic sobre ella.
2. En el panel **Biblioteca de recursos** (a la derecha) elija la pestaña
   **Doodles** (personajes y adornos), **Character** (personaje armable),
   **Accessories** (acciones, dispositivos, emotes, pcs) o **Bubbles**
   (bocadillos de diálogo).
3. Escriba en el buscador o navegue por las categorías.
4. **Haga clic o arrastre** una miniatura para insertarla en la viñeta.

Todo lo insertado se puede mover, redimensionar, rotar, voltear, clonar y
eliminar, y queda guardado en el archivo `.tbo`.

## ¿Cómo funciona la última carpeta recordada?

El programa recuerda la última carpeta que utilizó. Al abrir, guardar, exportar
o importar un archivo, esa carpeta se guarda. La próxima vez que use **Abrir**,
**Guardar como**, **Exportar**, **Añadir imagen** o **Añadir SVG**, el diálogo
empezará en esa carpeta. La primera vez, al no haber historial, empieza en su
directorio personal (`~`).

## Selección múltiple, alineación y distribución

Mantenga **`Ctrl`** mientras hace clic en varias viñetas u objetos, o arrastre
un rectángulo sobre el lienzo, para seleccionarlos a la vez. **`Ctrl+A`**
selecciona todas las viñetas de la página, o todos los objetos dentro de una
viñeta.

Mantenga la **barra espaciadora** y arrastre para desplazar la vista sin mover
la selección (como Inkscape).

Use los botones **Voltear** de la barra de herramientas (o `H` / `V`) para
reflejar un bocadillo u objeto horizontal o verticalmente — por ejemplo, para
orientar la cola del bocadillo hacia la boca del personaje.

Con varios elementos seleccionados puede:

- Pulsar **`Supr`** para eliminarlos todos en un solo paso (reversible con
  deshacer).
- Usar el menú **Editar ▸ Alinear** (izquierda, centro, derecha, arriba, etc.)
  para alinear las viñetas seleccionadas.
- Usar **Editar ▸ Distribuir** para repartir el espacio de forma uniforme.

Para **copiar y pegar** entre páginas use **`Ctrl+C`** y **`Ctrl+V`**: copie
viñetas (en la página) u objetos (dentro de una viñeta) y péguelos en la
página o viñeta actual.

## Arrastrar desde la biblioteca

Además de hacer clic en una miniatura, puede **arrastrarla** desde la
Biblioteca de recursos y **soltarla** dentro de la viñeta que está editando.

## Añadir sus propios dibujos (SVG)

Puede crear sus propios ojos, bocas, orejas, narices, cejas, pestañas, labios,
o cualquier otro elemento en **SVG** y el programa los cargará automáticamente.
No hay que convertir nada: el programa usa SVGs directamente.

Solo tiene que colocar sus archivos **.svg** en una de estas carpetas (el programa
no las crea, debe hacerlo usted):

- `~/.tbo/doodle/` (p.ej. `~/.tbo/doodle/head/eyes/mis_ojos.svg`)
- `~/.local/share/tbo/doodle/`

Organícelos por carpeta igual que el personaje de ejemplo (p.ej.
`head/eyes/`, `head/mouths/`, `noses/`). El programa los fusionará con los
recursos incluidos y los mostrará en la pestaña correspondiente.

## Personaje armable

En la pestaña **Character** de la biblioteca hay un personaje de ejemplo
formado por partes independientes que puede combinar a su gusto:

- **Cabeza**: un rostro vacío (sin ojos, orejas ni boca).
- **Ojos**: normal, alegre, triste, cerrado, sorprendido…
- **Boca**: sonrisa, neutra, triste, abierta, con lengua…
- **Orejas**: normales, puntiagudas.

Coloque primero la cabeza y luego arrastre cada parte hasta la posición
deseada. Puede usar **Rotar** (`[` / `]`), **Voltear** (`H` / `V`),
**Redimensionar** (arrastre el asa inferior derecha) y las expresiones que
quiera.

## Presentación y exportación

- Pulse **`F5`** (Ver ▸ Presentación) para leer el cómic a pantalla completa.
  Navegue con las flechas, `Espacio` o `Re Pág`/`Av Pág`; salga con `Esc`.
- **Exportar** (`Ctrl+E`) le permite elegir el formato, si quiere exportar todas
  las páginas o solo la actual, y la escala (hasta 1000 %) para PNG.

## Tema, rejilla y sesión

- **Ver ▸ Tema**: elija **Sistema**, **Oscuro** o **Claro**. La elección se
  recuerda entre sesiones.
- **Ver ▸ Ajustar a rejilla**: cuando está activo, las viñetas se alinean a una
  rejilla de 10 px al moverlas o redimensionarlas, y la rejilla se muestra en
  el lienzo. También se recuerda.
- El programa **reabre el último documento** que tenía abierto al cerrar.

## Páginas y búsqueda

- El panel **Páginas** (a la izquierda) muestra una **miniatura** de cada
  página; haga clic en una para ir a ella. Se actualiza al editar el cómic.
- **Editar ▸ Buscar texto** (`Ctrl+F`): busca en todos los objetos de texto
  del documento y le lleva a la página y la viñeta donde está la coincidencia.

## Atajos útiles

| Atajo | Acción |
| ----- | ------ |
| `Ctrl+N` | Nuevo cómic |
| `Ctrl+O` | Abrir |
| `Ctrl+S` | Guardar |
| `Ctrl+E` | Exportar |
| `Re Pág` / `Av Pág` | Página anterior / siguiente |
| `F` | Añadir viñeta (en la página) |
| Doble clic en viñeta | Editar su contenido |
| `T` | Añadir texto (editando viñeta) |
| `Esc` | Salir de la edición de viñeta |
| `Ctrl+D` | Clonar viñeta u objeto seleccionado |
| `Ctrl+C` / `Ctrl+V` | Copiar / pegar viñetas u objetos |
| `Ctrl` + clic / arrastre | Selección múltiple |
| `Ctrl+A` | Seleccionar todo |
| `Espacio` + arrastre | Desplazar la vista |
| `Supr` | Eliminar viñeta(s) u objeto(s) seleccionado(s) |
| `[` / `]` | Rotar objeto a la izquierda / derecha |
| `H` / `V` | Voltear objeto horizontal / vertical |
| `Ctrl` + rueda, `+` / `-` / `1` / `2` | Acercar / alejar / tamaño real / ajustar página |
| `F5` | Presentación a pantalla completa |
| `Ctrl+F` | Buscar texto en el documento |
| `Ctrl+Z` / `Ctrl+Shift+Z` | Deshacer / rehacer |
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
   <translation>&amp;Archivo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="70" />
   <source>&amp;New…</source>
   <translation>&amp;Nuevo…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="73" />
   <source>New</source>
   <translation>Nuevo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="77" />
   <source>&amp;Open…</source>
   <translation>&amp;Abrir…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="80" />
   <source>Open</source>
   <translation>Abrir</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="84" />
   <source>&amp;Save</source>
   <translation>&amp;Guardar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="87" />
   <source>Save</source>
   <translation>Guardar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="92" />
   <source>Save &amp;As…</source>
   <translation>Guardar &amp;como…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="95" />
   <source>Save As</source>
   <translation>Guardar como</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="100" />
   <source>&amp;Export…</source>
   <translation>&amp;Exportar…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="107" />
   <source>&amp;Recent Files</source>
   <translation>&amp;Archivos recientes</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="111" />
   <source>&amp;Edit</source>
   <translation>&amp;Editar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="112" />
   <source>&amp;Undo</source>
   <translation>&amp;Deshacer</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="115" />
   <source>Undo</source>
   <translation>Deshacer</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="117" />
   <source>&amp;Redo</source>
   <translation>&amp;Rehacer</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="120" />
   <source>Redo</source>
   <translation>Rehacer</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="123" />
   <source>&amp;Copy</source>
   <translation>&amp;Copiar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="127" />
   <source>&amp;Paste</source>
   <translation>&amp;Pegar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="133" />
   <source>Select &amp;All</source>
   <translation>Seleccionar &amp;todo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="139" />
   <source>Add &amp;Panel</source>
   <translation>Añadir &amp;viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="142" />
   <source>Add Panel</source>
   <translation>Añadir viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="145" />
   <source>&amp;Delete Panel</source>
   <translation>&amp;Eliminar viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="150" />
   <source>&amp;Clone Panel</source>
   <translation>&amp;Clonar viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="155" />
   <source>Leave Panel</source>
   <translation>Salir de viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="160" />
   <source>Ali&amp;gn</source>
   <translation>Ali&amp;near</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="161" />
   <source>Left</source>
   <translation>Izquierda</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="164" />
   <source>Horizontal Center</source>
   <translation>Centro horizontal</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="167" />
   <source>Right</source>
   <translation>Derecha</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="171" />
   <source>Top</source>
   <translation>Superior</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="174" />
   <source>Vertical Center</source>
   <translation>Centro vertical</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="177" />
   <source>Bottom</source>
   <translation>Inferior</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="181" />
   <source>&amp;Distribute</source>
   <translation>&amp;Distribuir</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="182" />
   <source>Horizontally</source>
   <translation>Horizontalmente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="185" />
   <source>Vertically</source>
   <translation>Verticalmente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="190" />
   <source>Add &amp;Text…</source>
   <translation>Añadir &amp;texto…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="193" />
   <source>Add Text</source>
   <translation>Añadir texto</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="197" />
   <source>Add &amp;Image…</source>
   <translation>Añadir &amp;imagen…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="201" />
   <source>Add &amp;SVG…</source>
   <translation>Añadir &amp;SVG…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="206" />
   <source>Rotate &amp;Left</source>
   <translation>Rotar a la &amp;izquierda</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="211" />
   <source>Rotate &amp;Right</source>
   <translation>Rotar a la &amp;derecha</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="216" />
   <source>Flip &amp;Horizontally</source>
   <translation>Voltear &amp;horizontalmente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="219" />
   <source>Flip Horizontally</source>
   <translation>Voltear horizontalmente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="223" />
   <source>Flip &amp;Vertically</source>
   <translation>Voltear &amp;verticalmente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="226" />
   <source>Flip Vertically</source>
   <translation>Voltear verticalmente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="230" />
   <source>Edit &amp;Text…</source>
   <translation>Editar &amp;texto…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="236" />
   <source>&amp;Find Text…</source>
   <translation>&amp;Buscar texto…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="254" />
   <source>&amp;Page</source>
   <translation>&amp;Página</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="255" />
   <source>&amp;Previous Page</source>
   <translation>&amp;Página anterior</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="260" />
   <source>&amp;Next Page</source>
   <translation>&amp;Página siguiente</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="266" />
   <source>Add Page</source>
   <translation>Añadir página</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="271" />
   <source>Delete Page</source>
   <translation>Eliminar página</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="276" />
   <source>Move Page Left</source>
   <translation>Mover página a la izquierda</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="281" />
   <source>Move Page Right</source>
   <translation>Mover página a la derecha</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="286" />
   <source>&amp;View</source>
   <translation>&amp;Ver</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="290" />
   <location filename="../src/tbo/ui/main_window.py" line="287" />
   <source>Fit Page</source>
   <translation>Ajustar página</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="297" />
   <location filename="../src/tbo/ui/main_window.py" line="294" />
   <source>Zoom In</source>
   <translation>Acercar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="304" />
   <location filename="../src/tbo/ui/main_window.py" line="301" />
   <source>Zoom Out</source>
   <translation>Alejar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="311" />
   <location filename="../src/tbo/ui/main_window.py" line="308" />
   <source>Actual Size</source>
   <translation>Tamaño real</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="315" />
   <source>&amp;Presentation…</source>
   <translation>&amp;Presentación…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="320" />
   <source>S&amp;nap to Grid</source>
   <translation>A&amp;justar a rejilla</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="326" />
   <source>&amp;Theme</source>
   <translation>&amp;Tema</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="331" />
   <source>System</source>
   <translation>Sistema</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="332" />
   <source>Dark</source>
   <translation>Oscuro</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="333" />
   <source>Light</source>
   <translation>Claro</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="344" />
   <source>&amp;Help</source>
   <translation>&amp;Ayuda</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="345" />
   <source>&amp;Help Contents</source>
   <translation>&amp;Contenido de ayuda</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="350" />
   <source>&amp;About TBO</source>
   <translation>&amp;Acerca de TBO</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="371" />
   <source>Main Toolbar</source>
   <translation>Barra de herramientas</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="400" />
   <source>Open Comic</source>
   <translation>Abrir cómic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="402" />
   <source>TBO Files (*.tbo);;All Files (*)</source>
   <translation>Archivos TBO (*.tbo);;Todos los archivos (*)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="422" />
   <source>Could Not Open File</source>
   <translation>No se pudo abrir el archivo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="456" />
   <source>Save Comic</source>
   <translation>Guardar cómic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="456" />
   <source>TBO Files (*.tbo)</source>
   <translation>Archivos TBO (*.tbo)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="488" />
   <source>Export Comic</source>
   <translation>Exportar cómic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="514" />
   <source>Could Not Export</source>
   <translation>No se pudo exportar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="519" />
   <source>Exported {count} file(s)</source>
   <translation>{count} archivo(s) exportado(s)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="587" />
   <source>File Not Found</source>
   <translation>Archivo no encontrado</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="588" />
   <source>{filename} no longer exists.</source>
   <translation>{filename} ya no existe.</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="602" />
   <source>Could Not Save File</source>
   <translation>No se pudo guardar el archivo</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="613" />
   <source>Saved to {filename}</source>
   <translation>Guardado en {filename}</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="653" />
   <source>Unsaved Changes</source>
   <translation>Cambios sin guardar</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="654" />
   <source>The document has unsaved changes. Do you want to save them before continuing?</source>
   <translation>El documento tiene cambios sin guardar. ¿Desea guardarlos antes de continuar?</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="830" />
   <source>Add Image</source>
   <translation>Añadir imagen</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="832" />
   <source>Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)</source>
   <translation>Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Todos los archivos (*)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="841" />
   <source>Could Not Add Image</source>
   <translation>No se pudo añadir la imagen</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="842" />
   <source>The selected file is not a supported or readable image.</source>
   <translation>El archivo seleccionado no es una imagen compatible o legible.</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="848" />
   <source>Add SVG</source>
   <translation>Añadir SVG</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="850" />
   <source>SVG Files (*.svg);;All Files (*)</source>
   <translation>Archivos SVG (*.svg);;Todos los archivos (*)</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="859" />
   <source>Could Not Add SVG</source>
   <translation>No se pudo añadir el SVG</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="860" />
   <source>The selected file is not a valid SVG image.</source>
   <translation>El archivo seleccionado no es una imagen SVG válida.</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="942" />
   <source>Delete Object</source>
   <translation>Eliminar objeto</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="942" />
   <source>Delete Panel</source>
   <translation>Eliminar viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="945" />
   <source>Clone Object</source>
   <translation>Clonar objeto</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="945" />
   <source>Clone Panel</source>
   <translation>Clonar viñeta</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="982" />
   <source>{percent}%</source>
   <translation>{percent}%</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="1008" />
   <source>Editing panel — press Esc to return · Page {current} of {count}</source>
   <translation>Editando viñeta — pulse Esc para volver · Página {current} de {count}</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="1013" />
   <source>Page {current} of {count}</source>
   <translation>Página {current} de {count}</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/main_window.py" line="1017" />
   <source>Document has no pages</source>
   <translation>El documento no tiene páginas</translation>
  </message>
 </context>
 <context>
  <name>NewComicDialog</name>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="19" />
   <source>New comic</source>
   <translation>Nuevo cómic</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="48" />
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="21" />
   <source>Untitled</source>
   <translation>Sin título</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="33" />
   <source>Title:</source>
   <translation>Título:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="34" />
   <source>Width:</source>
   <translation>Ancho:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/new_comic_dialog.py" line="35" />
   <source>Height:</source>
   <translation>Altura:</translation>
  </message>
 </context>
 <context>
  <name>PagesDock</name>
  <message>
   <location filename="../src/tbo/ui/pages_dock.py" line="30" />
   <source>Pages</source>
   <translation>Páginas</translation>
  </message>
 </context>
 <context>
  <name>PresentationDialog</name>
  <message>
   <location filename="../src/tbo/ui/presentation.py" line="28" />
   <source>Presentation</source>
   <translation>Presentación</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/presentation.py" line="68" />
   <source>Presentation — Page {current} of {count}</source>
   <translation>Presentación — Página {current} de {count}</translation>
  </message>
 </context>
 <context>
  <name>SearchDialog</name>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="22" />
   <source>Find Text</source>
   <translation>Buscar texto</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="28" />
   <source>Search text in the document…</source>
   <translation>Buscar texto en el documento…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="39" />
   <source>Go to</source>
   <translation>Ir a</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/search_dialog.py" line="63" />
   <source>Page {page}: {preview}</source>
   <translation>Página {page}: {preview}</translation>
  </message>
 </context>
 <context>
  <name>TextObjectDialog</name>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="22" />
   <source>Add Text</source>
   <translation>Añadir texto</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="26" />
   <source>Enter the text to place in the panel…</source>
   <translation>Introduzca el texto para colocar en la viñeta…</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="42" />
   <source>Font:</source>
   <translation>Fuente:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="43" />
   <source>Color:</source>
   <translation>Color:</translation>
  </message>
  <message>
   <location filename="../src/tbo/ui/text_object_dialog.py" line="59" />
   <source>Choose Text Color</source>
   <translation>Elegir color de texto</translation>
  </message>
 </context>
 <context>
  <name>_LibraryTab</name>
  <message>
   <location filename="../src/tbo/ui/assets_dock.py" line="51" />
   <source>Search…</source>
   <translation>Buscar…</translation>
  </message>
 </context>
</TS>