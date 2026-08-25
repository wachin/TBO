#!/usr/bin/env python3
"""Translate tbo_es.ts from English to Spanish."""

import xml.etree.ElementTree as ET

TRANSLATIONS = {
    "&About TBO": "&Acerca de TBO",
    "&Clone Panel": "&Clonar viñeta",
    "&Copy": "&Copiar",
    "&Delete Panel": "&Eliminar viñeta",
    "&Distribute": "&Distribuir",
    "&Edit": "&Editar",
    "&Export…": "&Exportar…",
    "&File": "&Archivo",
    "&Find Text…": "&Buscar texto…",
    "&Help": "&Ayuda",
    "&Help Contents": "&Contenido de ayuda",
    "&New…": "&Nuevo…",
    "&Next Page": "&Página siguiente",
    "&Open…": "&Abrir…",
    "&Page": "&Página",
    "&Paste": "&Pegar",
    "&Presentation…": "&Presentación…",
    "&Previous Page": "&Página anterior",
    "&Recent Files": "&Archivos recientes",
    "&Redo": "&Rehacer",
    "&Save": "&Guardar",
    "&Theme": "&Tema",
    "&Undo": "&Deshacer",
    "&View": "&Ver",
    "100%": "100%",
    "About TBO": "Acerca de TBO",
    "Accessories": "Accesorios",
    "Actual Size": "Tamaño real",
    "Add &Image…": "Añadir &imagen…",
    "Add &Panel": "Añadir &viñeta",
    "Add &SVG…": "Añadir &SVG…",
    "Add &Text…": "Añadir &texto…",
    "Add Image": "Añadir imagen",
    "Add Page": "Añadir página",
    "Add Panel": "Añadir viñeta",
    "Add SVG": "Añadir SVG",
    "Add Text": "Añadir texto",
    "Ali&gn": "Ali&near",
    "All pages ({count})": "Todas las páginas ({count})",
    "Asset Library": "Biblioteca de recursos",
    "Bottom": "Inferior",
    "Bubbles": "Bocadillos",
    "Character": "Personaje",
    "Choose Text Color": "Elegir color de texto",
    "Clone Object": "Clonar objeto",
    "Clone Panel": "Clonar viñeta",
    "Clone object": "Clonar objeto",
    "Clone panel": "Clonar viñeta",
    "Color:": "Color:",
    "Could Not Add Image": "No se pudo añadir la imagen",
    "Could Not Add SVG": "No se pudo añadir el SVG",
    "Could Not Export": "No se pudo exportar",
    "Could Not Open File": "No se pudo abrir el archivo",
    "Could Not Save File": "No se pudo guardar el archivo",
    "Current page ({index} of {count})": "Página actual ({index} de {count})",
    "Dark": "Oscuro",
    "Delete Object": "Eliminar objeto",
    "Delete Page": "Eliminar página",
    "Delete Panel": "Eliminar viñeta",
    "Delete objects": "Eliminar objetos",
    "Delete panels": "Eliminar viñetas",
    "Document has no pages": "El documento no tiene páginas",
    "Doodles": "Doodles",
    "Edit &Text…": "Editar &texto…",
    "Editing panel — press Esc to return · Page {current} of {count}": "Editando viñeta — pulse Esc para volver · Página {current} de {count}",
    "Enter the text to place in the panel…": "Introduzca el texto para colocar en la viñeta…",
    "Export Comic": "Exportar cómic",
    "Export Options": "Opciones de exportación",
    "Exported {count} file(s)": "{count} archivo(s) exportado(s)",
    "File Not Found": "Archivo no encontrado",
    "Find Text": "Buscar texto",
    "Fit Page": "Ajustar página",
    "Flip &Horizontally": "Voltear &horizontalmente",
    "Flip &Vertically": "Voltear &verticalmente",
    "Flip Horizontally": "Voltear horizontalmente",
    "Flip Vertically": "Voltear verticalmente",
    "Font:": "Fuente:",
    "Format:": "Formato:",
    "Go to": "Ir a",
    "Height:": "Altura:",
    "Horizontal Center": "Centro horizontal",
    "Horizontally": "Horizontalmente",
    "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)": "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;Todos los archivos (*)",
    "Leave Panel": "Salir de viñeta",
    "Left": "Izquierda",
    "Light": "Claro",
    "Main Toolbar": "Barra de herramientas",
    "Move Page Left": "Mover página a la izquierda",
    "Move Page Right": "Mover página a la derecha",
    "New": "Nuevo",
    "New comic": "Nuevo cómic",
    "Open": "Abrir",
    "Open Comic": "Abrir cómic",
    "Output resolution for PNG export": "Resolución de salida para exportación PNG",
    "Page {current} of {count}": "Página {current} de {count}",
    "Page {page}: {preview}": "Página {page}: {preview}",
    "Pages": "Páginas",
    "Paste objects": "Pegar objetos",
    "Paste panels": "Pegar viñetas",
    "Presentation": "Presentación",
    "Presentation — Page {current} of {count}": "Presentación — Página {current} de {count}",
    "Range:": "Rango:",
    "Redo": "Rehacer",
    "Right": "Derecha",
    "Rotate &Left": "Rotar a la &izquierda",
    "Rotate &Right": "Rotar a la &derecha",
    "S&nap to Grid": "A&justar a rejilla",
    "SVG Files (*.svg);;All Files (*)": "Archivos SVG (*.svg);;Todos los archivos (*)",
    "Save": "Guardar",
    "Save &As…": "Guardar &como…",
    "Save As": "Guardar como",
    "Save Comic": "Guardar cómic",
    "Saved to {filename}": "Guardado en {filename}",
    "Scale:": "Escala:",
    "Search text in the document…": "Buscar texto en el documento…",
    "Search…": "Buscar…",
    "Select &All": "Seleccionar &todo",
    "System": "Sistema",
    "TBO Files (*.tbo)": "Archivos TBO (*.tbo)",
    "TBO Files (*.tbo);;All Files (*)": "Archivos TBO (*.tbo);;Todos los archivos (*)",
    "TBO Help": "Ayuda de TBO",
    "The document has unsaved changes. Do you want to save them before continuing?": "El documento tiene cambios sin guardar. ¿Desea guardarlos antes de continuar?",
    "The selected file is not a supported or readable image.": "El archivo seleccionado no es una imagen compatible o legible.",
    "The selected file is not a valid SVG image.": "El archivo seleccionado no es una imagen SVG válida.",
    "Title:": "Título:",
    "Top": "Superior",
    "Undo": "Deshacer",
    "Unsaved Changes": "Cambios sin guardar",
    "Untitled": "Sin título",
    "Vertical Center": "Centro vertical",
    "Vertically": "Verticalmente",
    "Width:": "Ancho:",
    "Zoom In": "Acercar",
    "Zoom Out": "Alejar",
    "{filename} no longer exists.": "{filename} ya no existe.",
    "{percent}%": "{percent}%",
}

# También hay que traducir el bloque grande de ayuda
HELP_ES = """\
# TBO 2 — Ayuda

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

Al insertar un **bocadillo de diálogo** (pestaña Bubbles), se coloca
automáticamente un **objeto de texto** editable en su interior, centrado y listo
para editar. Haga **doble clic** en el texto para editarlo en su lugar
(Ctrl+Enter acepta, Esc cancela), o selecciónelo y pulse `E` / use
**Editar ▸ Editar texto**.

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
"""


def translate() -> None:
    tree = ET.parse("translations/tbo_es.ts")
    root = tree.getroot()
    count = 0
    for message in root.iter("message"):
        source_el = message.find("source")
        trans_el = message.find("translation")
        if source_el is None or source_el.text is None or trans_el is None:
            continue
        source = source_el.text
        if source == HELP_ES:  # already translated? skip
            continue
        if source in TRANSLATIONS:
            trans_el.text = TRANSLATIONS[source]
            if "type" in trans_el.attrib:
                del trans_el.attrib["type"]
            count += 1
        elif source.startswith("# TBO 2 — Help"):
            trans_el.text = HELP_ES
            if "type" in trans_el.attrib:
                del trans_el.attrib["type"]
            count += 1
    ET.indent(tree, space=" ")
    tree.write("translations/tbo_es.ts", encoding="utf-8", xml_declaration=True)
    print(f"Traducidas: {count} cadenas")


if __name__ == "__main__":
    translate()