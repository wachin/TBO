from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

HELP_MARKDOWN = """\
# TBO 2 — Ayuda

## ¿Dónde están los archivos `.tbo`?

Los archivos `.tbo` son documentos de cómic completos (páginas, viñetas y
objetos). En la distribución solo se incluyen dos ejemplos:

- `data/tut.tbo` — el tutorial.
- `doc/pres-final.tbo` — un ejemplo de presentación.

## ¿Dónde están los personajes (doodles y bocadillos)?

No hay un archivo `.tbo` por personaje. Los personajes y adornos son archivos
**SVG** que se incluyen con el programa en el directorio `doodle`, organizados
por categorías (cuerpo, ojos, boca, personajes completos, accesorios, etc.).

Para usarlos:

1. **Entra en una viñeta** haciendo doble clic sobre ella.
2. En el panel **Biblioteca de recursos** (a la derecha) elige la pestaña
   **Doodles** (personajes y adornos) o **Bubbles** (bocadillos de diálogo).
3. Escribe en el buscador o navega por las categorías.
4. **Haz clic en una miniatura** para insertarla en la viñeta.

Todo lo insertado se puede mover, redimensionar, rotar, voltear, clonar y
eliminar, y queda guardado en el archivo `.tbo` al guardar.

## ¿Cómo funciona la última carpeta recordada?

El programa recuerda la última carpeta que utilizaste. Al abrir un archivo,
guardarlo, exportarlo o importar una imagen/SVG, la carpeta de ese archivo se
guarda como la última utilizada. La próxima vez que abras **Abrir**, **Guardar
como**, **Exportar**, **Añadir imagen** o **Añadir SVG**, el diálogo empezará en
esa carpeta. La primera vez, al no haber historial, empieza en tu carpeta
personal (`~`).

## Selección múltiple, alineación y distribución

Mantén **`Ctrl`** mientras haces clic en varias viñetas u objetos, o arrastra
un rectángulo sobre el lienzo, para seleccionarlos a la vez. **`Ctrl+A`**
selecciona todo (las viñetas de la página, o los objetos dentro de la viñeta).

Mantén la **barra espaciadora** y arrastra para desplazar la vista sin mover la
selección (como en Inkscape).

Usa los botones **Voltear** de la barra de herramientas (o `H` / `V`) para
reflejar un bocadillo u objeto horizontal o verticalmente; así puedes orientar
la cola del bocadillo hacia la boca del personaje.

Con varios seleccionados puedes:

- Pulsar **`Supr`** para eliminarlos todos en un solo paso (reversible con
  deshacer).
- Usar el menú **Editar ▸ Alinear** (izquierda, centro, derecha, arriba, etc.)
  para alinear las viñetas seleccionadas.
- Usar **Editar ▸ Distribuir** para repartir el espacio de forma uniforme.

Para **copiar y pegar** entre páginas usa **`Ctrl+C`** y **`Ctrl+V`**: copia las
viñetas (en la página) o los objetos (dentro de una viñeta) y pégalos en la
página o viñeta actual.

## Arrastrar desde la biblioteca

Además de hacer clic en una miniatura, puedes **arrastrarla** desde el panel
**Biblioteca de recursos** y soltarla dentro de la viñeta que estás editando.

## Añadir tus propios dibujos (SVG)

Puedes crear tus propios ojos, bocas, orejas, narices, cejas, pestañas,
labios, o cualquier otro elemento en **SVG** y el programa los cargará
automáticamente. No hay que convertir nada: el programa usa SVGs directamente.

Solo tienes que colocar tus archivos **.svg** en una de estas carpetas
(el programa no las crea, debes hacerlo tú):

- `~/.tbo/doodle/` (por ejemplo: `~/.tbo/doodle/head/eyes/mis_ojos.svg`)
- `~/.local/share/tbo/doodle/`

Organízalos por carpetas igual que el personaje de ejemplo (p. ej.
`cabeza/ojos/`, `cabeza/bocas/`, `narices/`). El programa los mezclará con los
recursos incluidos y los mostrará en la pestaña correspondiente.

## Personaje armable

En la pestaña **Character** de la biblioteca hay un personaje de ejemplo
formado por partes independientes que puedes combinar a tu gusto:

- **Cabeza**: un rostro vacío (sin ojos, orejas ni boca).
- **Ojos**: normal, alegre, triste, cerrado, sorprendido…
- **Boca**: sonrisa, neutra, triste, abierta, con lengua…
- **Orejas**: normales, puntiagudas…

Coloca primero la cabeza y luego arrastra cada parte hasta la posición deseada.
Puedes usar **Rotar** (`[` / `]`), **Voltear** (`H` / `V`), **Redimensionar**
(arrastra el asa inferior derecha) y las expresiones que quieras.

## Presentación y exportación

- Pulsa **`F5`** (menú **Ver ▸ Presentación**) para leer el cómic a pantalla
  completa. Navega con las flechas, `Espacio` o `Re Pág`/`Av Pág`, y sal con
  `Esc`.
- **Exportar** (`Ctrl+E`) ahora te deja elegir el formato, si quieres **todas
  las páginas** o **solo la página actual**, y la **escala** (resolución) para
  PNG (hasta 1000 %).

## Tema, rejilla y sesión

- **Ver ▸ Tema**: elige entre **Sistema**, **Oscuro** o **Claro**. La elección
  se recuerda entre sesiones.
- **Ver ▸ Ajustar a rejilla**: cuando está activo, las viñetas se alinean a una
  rejilla de 10 px al moverlas o redimensionarlas, y la rejilla se muestra en el
  lienzo. Útil para colocar viñetas con precisión. También se recuerda.
- El programa **reabre el último documento** que tenías abierto al cerrar.

## Páginas y búsqueda

- El panel **Páginas** (a la izquierda) muestra una **miniatura** de cada página;
  haz clic en una para ir a ella. Se actualiza al editar el cómic.
- **Editar ▸ Buscar texto** (`Ctrl+F`): busca en todos los objetos de texto del
  documento y te lleva a la página y la viñeta donde está la coincidencia.

## Atajos útiles

| Atajo | Acción |
| ----- | ------ |
| `Ctrl+N` | Nuevo cómic |
| `Ctrl+O` | Abrir |
| `Ctrl+S` | Guardar |
| `Ctrl+E` | Exportar |
| `PageUp` / `PageDown` | Página anterior / siguiente |
| `F` | Añadir viñeta (en la página) |
| Doble clic en viñeta | Editar su contenido |
| `T` | Añadir texto (editando viñeta) |
| `Esc` | Salir de la edición de viñeta |
| `Ctrl+D` | Clonar viñeta u objeto seleccionado |
| `Ctrl+C` / `Ctrl+V` | Copiar / pegar viñetas u objetos |
| `Ctrl` + clic / arrastre | Selección múltiple |
| `Ctrl+A` | Seleccionar todo (viñetas u objetos) |
| `Barra espaciadora` + arrastre | Desplazar la vista (pañuelo) |
| `Delete` | Eliminar viñeta u objeto seleccionado |
| `[` / `]` | Rotar objeto a la izquierda / derecha |
| `H` / `V` | Voltear objeto horizontal / vertical |
| `Ctrl` + rueda o `+` / `-` / `1` / `2` | Zoom in / out / tamaño real / ajustar página |
| `F5` | Modo presentación a pantalla completa |
| `Ctrl+F` | Buscar texto en el documento |
| `Ctrl+Z` / `Ctrl+Shift+Z` | Deshacer / rehacer |
"""


class HelpDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("TBO Help"))
        self.resize(680, 560)

        browser = QTextBrowser()
        browser.setMarkdown(HELP_MARKDOWN)
        browser.setOpenExternalLinks(True)
        browser.document().setDefaultStyleSheet("body { font-size: 13px; }")

        layout = QVBoxLayout(self)
        layout.addWidget(browser)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
            return
        super().keyPressEvent(event)
