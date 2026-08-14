# TBO 2 (en desarrollo)

Esta carpeta contiene la reimplementación de TBO en Python y PyQt6. El código
C/GTK del directorio raíz se conserva como referencia de compatibilidad.

## Ejecutar desde el repositorio

Desde la raíz del repositorio puedes utilizar el launcher:

```bash
./tbo.sh
./tbo.sh data/tut.tbo
```

El script configura automáticamente `PYTHONPATH` y también funciona al
invocarlo desde otro directorio.

La ejecución equivalente sin el launcher es:

```bash
cd tbo_next
PYTHONPATH=src python -m tbo ../data/tut.tbo
```

Para abrir el lienzo vacío, omite la ruta. La aplicación ya puede leer y
representar las páginas, viñetas, textos y recursos SVG del formato histórico.

Controles disponibles:

- `Ctrl+N`: crear un cómic indicando título y dimensiones;
- `PageUp` / `PageDown`: página anterior o siguiente;
- `Ctrl+Shift+N`: añadir una página después de la actual;
- `Ctrl+Supr`: eliminar la página actual;
- `Ctrl+PageUp` / `Ctrl+PageDown`: mover la página actual a izquierda o derecha;
- `+` / `-`: acercar o alejar;
- `1`: volver al tamaño real;
- `2`: ajustar la página a la ventana;
- `Ctrl+O`: abrir un documento;
- `Ctrl+S`: guardar de forma atómica;
- `Ctrl+Shift+S`: guardar una copia;
- `F`: añadir una viñeta;
- arrastrar una viñeta seleccionada: moverla;
- arrastrar el tirador amarillo inferior derecho: redimensionarla;
- flechas: mover la viñeta seleccionada en pasos de 5 píxeles;
- `Ctrl+D`: clonar la viñeta seleccionada;
- `Supr`: eliminar la viñeta seleccionada;
- `Ctrl+Z` / `Ctrl+Shift+Z`: deshacer o rehacer.

Las operaciones de añadir, clonar, mover, redimensionar y eliminar viñetas
modifican el modelo del documento y quedan registradas en el historial de
deshacer. Crear, eliminar y reordenar páginas también es reversible. Un `*` en
el título indica que existen cambios sin guardar.

Para editar el contenido de una viñeta, haz doble clic sobre ella. En este modo
puedes seleccionar y arrastrar textos, imágenes o SVG, clonarlos con `Ctrl+D`,
moverlos con las flechas y eliminarlos con `Supr`. Todas esas operaciones admiten
undo/redo y se guardan en el `.tbo`. Pulsa `Esc` para regresar a la edición de
página; las demás viñetas aparecen atenuadas mientras editas una.

TBO 2 escribe por ahora el formato v1 sin versión para mantener compatibilidad
con el programa histórico. Conviene utilizar **Guardar como** mientras la nueva
implementación siga en desarrollo.

Si hay cambios pendientes al crear, abrir otro documento o cerrar la ventana,
TBO pregunta si deben guardarse, descartarse o si se desea cancelar la acción.
Cancelar nunca sustituye el documento ni elimina su historial de undo/redo.

## Pruebas

```bash
cd tbo_next
QT_QPA_PLATFORM=offscreen python -m pytest
```

Instalación editable para desarrollo:

```bash
python -m pip install -e '.[dev]'
```

El formato `.tbo` se trata como entrada no confiable. No se deben relajar sus
límites ni validaciones sin añadir primero un caso de prueba.
