# TBO 2 (en desarrollo)

Esta carpeta contiene la reimplementación de TBO en Python y PyQt6. El código
C/GTK del directorio raíz se conserva como referencia de compatibilidad.

## Ejecutar desde el repositorio

```bash
cd tbo_next
PYTHONPATH=src python -m tbo ../data/tut.tbo
```

Para abrir el lienzo vacío, omite la ruta. La aplicación ya puede leer y
representar las páginas, viñetas, textos y recursos SVG del formato histórico.

Controles disponibles:

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

TBO 2 escribe por ahora el formato v1 sin versión para mantener compatibilidad
con el programa histórico. Conviene utilizar **Guardar como** mientras la nueva
implementación siga en desarrollo.

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
