# TBO

TBO es un editor de cómics libre basado en páginas, viñetas, textos, imágenes
y dibujos SVG. Este repositorio contiene el programa histórico en C/GTK 3 y
**TBO 2**, una reimplementación activa en Python y PyQt6.

> [!IMPORTANT]
> TBO 2 está en desarrollo. Ya permite abrir, editar y guardar documentos
> históricos, pero todavía no alcanza la paridad completa con TBO 1.0. Conserva
> una copia de tus proyectos y utiliza **Guardar como** durante las pruebas.

## Estado del proyecto

TBO 1.0 llevaba sin mantenimiento desde 2013. En lugar de trasladar directamente
las API obsoletas de GTK, TBO 2 reconstruye la aplicación con una arquitectura
comprobable y mantiene compatibilidad con el formato `.tbo` original.

Actualmente TBO 2 permite:

- crear, abrir y guardar documentos `.tbo`;
- leer números y proyectos generados por TBO 1.0;
- guardar de forma atómica para evitar archivos parcialmente escritos;
- crear, eliminar, navegar y reordenar páginas;
- crear, seleccionar, mover, redimensionar, clonar y eliminar viñetas;
- entrar en una viñeta y mover, clonar o eliminar sus textos, imágenes y SVG;
- deshacer y rehacer las operaciones de edición implementadas;
- navegar, ajustar la página y controlar el zoom;
- detectar cambios pendientes antes de crear, abrir o cerrar;
- representar recursos ausentes sin cerrar abruptamente la aplicación.

Todavía están pendientes, entre otras funciones:

- añadir nuevos textos, imágenes y SVG desde la interfaz;
- redimensionar, rotar y voltear objetos;
- editar propiedades de texto y color;
- exportar a PNG, PDF y SVG;
- recuperación automática, traducciones y paquetes para distribución.

Consulta [ROADMAP.md](ROADMAP.md) para ver las fases, prioridades y criterios de
salida de la modernización.

## Requisitos

- Python 3.11 o posterior;
- PyQt6 6.6 o posterior;
- pytest y pytest-qt para ejecutar las pruebas.

La implementación histórica tiene dependencias diferentes y se conserva como
referencia; no es necesaria para ejecutar TBO 2.

## Ejecutar TBO 2

Sin instalar el paquete:

```bash
cd tbo_next
PYTHONPATH=src python3 -m tbo
```

Para abrir directamente un proyecto histórico:

```bash
cd tbo_next
PYTHONPATH=src python3 -m tbo ../data/tut.tbo
```

También puedes realizar una instalación editable desde la raíz del repositorio:

```bash
python3 -m pip install -e './tbo_next[dev]'
tbo data/tut.tbo
```

## Uso básico

- `Ctrl+N`, `Ctrl+O`, `Ctrl+S`: nuevo, abrir y guardar.
- `PageUp` / `PageDown`: navegar entre páginas.
- `Ctrl+Shift+N`, `Ctrl+Supr`: crear o eliminar páginas.
- `F`, `Ctrl+D`, `Supr`: crear, clonar o eliminar la viñeta seleccionada.
- Flechas: mover la selección en pasos de 5 píxeles.
- `Ctrl+Z` / `Ctrl+Shift+Z`: deshacer o rehacer.
- `+`, `-`, `1`, `2`: acercar, alejar, tamaño real y ajustar a la ventana.
- Doble clic sobre una viñeta: editar sus objetos.
- `Esc`: regresar de la edición de objetos a la página.

La guía detallada y todos los atajos están en
[tbo_next/README.md](tbo_next/README.md).

## Pruebas

Desde la raíz del repositorio:

```bash
cd tbo_next
QT_QPA_PLATFORM=offscreen python3 -m pytest
```

La suite incluye pruebas unitarias del modelo y los comandos, casos inválidos
del parser, round-trip del tutorial histórico, guardado atómico e integración
headless de la interfaz Qt.

## Organización del repositorio

```text
.
├── tbo_next/        # Implementación activa en Python/PyQt6
├── src/             # Implementación histórica en C/GTK 3
├── data/            # Doodles, iconos, tutorial y otros recursos
├── po/              # Traducciones históricas
├── doc/             # Documentación histórica
├── test/            # Experimentos y pruebas del programa original
└── ROADMAP.md       # Plan de recuperación y modernización
```

Dentro de `tbo_next`, el modelo del documento es independiente de los widgets.
El lienzo representa ese modelo mediante `QGraphicsScene`, mientras que las
mutaciones se registran como comandos en `QUndoStack`. El parser trata cada
archivo `.tbo` como entrada no confiable y aplica límites antes de construir el
documento.

## Colaborar

Las contribuciones más útiles en esta etapa son cambios pequeños acompañados de
pruebas. Antes de modificar persistencia o compatibilidad:

1. añade un fixture o caso que describa el comportamiento esperado;
2. mantén el modelo como fuente de verdad, no los elementos gráficos;
3. verifica que abrir, guardar y volver a abrir conserva el documento;
4. ejecuta toda la suite en modo headless;
5. actualiza el roadmap o la documentación si cambia el alcance.

No mezcles en un mismo cambio reformateos masivos, refactorizaciones y funciones
nuevas. Esto mantiene revisable la recuperación de una base de código histórica.

## Licencia

TBO se distribuye bajo la **GNU General Public License, versión 3 o posterior**.
Consulta [COPYING](COPYING) para leer el texto completo de la licencia.
