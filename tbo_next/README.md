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
- `2`: ajustar la página a la ventana;
- `Ctrl+O`: abrir un documento;
- `Ctrl+S`: guardar de forma atómica;
- `Ctrl+Shift+S`: guardar una copia.

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
