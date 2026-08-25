# Roadmap de modernización de TBO

TBO 2 **es** una reimplementación compatible en **Python y PyQt6**. El código histórico en C/GTK 3 se conserva bajo `legacy/` como referencia de comportamiento, pero no se migra a GTK 4.

El objetivo no fue traducir cada función línea por línea: se reconstruyó la aplicación alrededor de un modelo comprobable, una interfaz moderna y compatibilidad explícita con los proyectos `.tbo` existentes.

Este documento no establece fechas arbitrarias. Cada fase tiene resultados y condiciones de salida verificables; la siguiente comienza cuando estos se cumplen.

## Estado actual (TBO 2)

El port está **funcionalmente completo** en la raíz del repositorio:

- **Modelo y formato**: `Comic`/`Page`/`Frame`/objetos como dataclasses independientes de widgets; lector/escritor `.tbo` v1 seguro (límites, validación, errores con contexto, guardado atómico) con fuzzing y round-trips.
- **Lienzo**: `QGraphicsScene/View`, zoom con rueda, selección múltiple (rubber band, `Ctrl+A`), pan con barra espaciadora, snap-to-grid con rejilla visible, alineación/distribución.
- **Edición**: undo/redo completo mediante `QUndoStack`; crear, mover, redimensionar, rotar, voltear, clonar, alinear y distribuir viñetas y objetos; edición inline de texto y barra de texto avanzada (fuente, tamaño, negrita, cursiva, subrayado, color).
- **Biblioteca de recursos**: pestañas Doodles / Character / Accessories / Bubbles con búsqueda, drag & drop, personaje armable (cabeza + ojos/bocas/orejas) y assets de usuario (`~/.tbo/doodle/`).
- **Exportación**: PNG (por página, con escala), PDF multipágina y SVG por página mediante un renderer compartido; modo presentación (F5).
- **Escritorio**: tema claro/oscuro/sistema, preferencias con `QSettings`, archivos recientes, autosave y `.bak`, reapertura de sesión, miniaturas de página, búsqueda de texto, ayuda traducible.
- **i18n**: inglés como idioma fuente y traducción al español con Qt Linguist (`--lang`).
- **Empaquetado**: `.deb` (dpkg-buildpackage), wheel/sdist, manifiesto Flatpak, CI en GitHub Actions (automático + build manual).
- **Tests**: 54 pruebas unitarias (modelo, parser, fuzzing, round-trips, preferencias, recursos) y pruebas de integración Qt (se ejecutan localmente con display; no se ejecutan en CI por el aborto de `QGraphicsView` en headless).

El trabajo se organizó por fases; las siguientes marcan lo ya completado y lo pendiente.

## Punto de partida

La última revisión del repositorio es de abril de 2013 y la versión publicada es la 1.0. La implementación histórica contiene unas 8.800 líneas de C y utiliza GTK 3, GLib/GObject, Cairo, librsvg, gettext/intltool y Autotools.

La funcionalidad que debe preservarse incluye:

- documentos con páginas y viñetas;
- objetos de texto, imágenes y SVG;
- selección, movimiento, redimensionado, rotación y volteo;
- biblioteca de doodles y bocadillos;
- zoom y navegación entre páginas;
- deshacer y rehacer;
- lectura y escritura de `.tbo`;
- exportación a PNG, PDF y SVG.

Problemas relevantes encontrados en el legado:

- la construcción depende de `gnome-common` y herramientas antiguas;
- no existe CI ni una suite automática de regresión;
- el lector `.tbo` copia atributos a buffers fijos con `sprintf`;
- el guardado escribe directamente al archivo final y apenas propaga errores;
- las rutas se construyen con `strcpy`/`strcat` y límites fijos;
- el parser, el modelo y la interfaz comparten estado global;
- el formato `.tbo` no tiene versión, esquema ni política de recursos externos;
- la interfaz depende ampliamente de API GTK obsoleta.

## Decisión tecnológica

La nueva aplicación usará:

- **Python 3** como lenguaje;
- **PyQt6** para la aplicación y los widgets;
- **QGraphicsScene/QGraphicsView** para el lienzo y sus objetos;
- **QUndoStack** y comandos para deshacer/rehacer;
- **QPainter**, **QImage**, **QPdfWriter** y **QSvgGenerator** para renderizado y exportación;
- **QSvgRenderer** para los recursos SVG;
- **pytest** y **pytest-qt** para pruebas;
- `pyproject.toml` como fuente única de configuración del paquete y herramientas.

PyQt6 encaja con la licencia GPLv3 del proyecto. Antes de publicar TBO 2 se verificará formalmente la declaración de licencia del código, las dependencias y cada biblioteca de recursos gráficos.

No se descarta evaluar PySide6 en el futuro, pero no se mantendrán simultáneamente dos bindings Qt. Cualquier cambio deberá contar con una razón de distribución o licencia documentada y pruebas que demuestren su coste.

## Principios de la reimplementación

1. **Compatibilidad antes que funciones nuevas.** TBO 2 debe abrir proyectos creados con TBO 1.0.
2. **Reimplementar, no transliterar.** Se preserva el comportamiento útil, no la estructura ni los defectos del código C.
3. **El modelo no depende de Qt Widgets.** Un documento debe poder cargarse, modificarse y exportarse sin abrir una ventana.
4. **El legado es un oráculo temporal.** Sirve para comparar comportamiento, no como base que deba seguir creciendo.
5. **Todo cambio de documento es un comando.** Esto hace que undo/redo sea completo y comprobable.
6. **Los archivos del usuario son datos no confiables.** Se validan límites, rutas, tipos y estructura antes de crear objetos.
7. **La distribución forma parte del producto.** Una función no está terminada si la aplicación no puede instalarse y probarse de manera reproducible.
8. **Inglés como idioma fuente.** La interfaz se implementará primero en inglés y las cadenas se marcarán para Qt Linguist; la traducción al español se añadirá cuando la funcionalidad y la terminología sean estables.

## Alcance inicial de TBO 2

La primera versión estable buscará paridad con TBO 1.0. No forman parte del MVP:

- colaboración en red;
- animación;
- formato totalmente nuevo sin importador del anterior;
- plugins de terceros;
- edición SVG vectorial interna;
- aplicaciones móviles;
- reescritura o limpieza exhaustiva del código C.

Estas exclusiones evitan que las funciones nuevas retrasen la recuperación del programa.

## Arquitectura objetivo

El port vive en la **raíz del repositorio**; el código histórico se conserva bajo
`legacy/` como oráculo de comportamiento.

```text
.
├── pyproject.toml
├── setup.py
├── src/
│   └── tbo/
│       ├── __main__.py
│       ├── application.py
│       ├── resources.py
│       ├── resources/            # iconos y logo empaquetados
│       ├── document/
│       │   └── model.py           # Comic, Page, Frame, objetos
│       ├── formats/
│       │   └── tbo_v1.py          # lector/escritor seguro del .tbo
│       ├── rendering/
│       │   ├── renderer.py        # render compartido (pantalla y exportación)
│       │   └── exporter.py        # PNG / PDF / SVG
│       ├── assets/
│       │   ├── catalog.py         # biblioteca de doodles/bocadillos
│       │   └── resolver.py        # resolución de rutas sin escapes
│       └── ui/
│           ├── main_window.py     # menús, barra de herramientas y texto
│           ├── canvas.py          # QGraphicsScene/View + edición inline
│           ├── about_dialog.py
│           ├── help_dialog.py
│           ├── search_dialog.py
│           ├── export_dialog.py
│           ├── new_comic_dialog.py
│           ├── text_object_dialog.py
│           ├── assets_dock.py     # pestañas Doodles/Character/Accessories/Bubbles
│           ├── pages_dock.py      # miniaturas de página
│           ├── presentation.py    # modo presentación (F5)
│           ├── preferences.py     # QSettings
│           └── theme.py           # tema claro/oscuro/sistema
├── tests/
│   ├── fixtures/
│   ├── unit/
│   └── integration/
├── packaging/                     # .desktop, AppStream, manifiesto Flatpak
├── debian/                        # build del .deb
├── docs/                          # guías (p. ej. creating-characters.md)
├── translations/                  # tbo_en.ts/.qm, tbo_es.ts/.qm
├── tools/                         # generadores y traducción
├── data/                          # doodles, tutorial y recursos
└── legacy/                        # código C/GTK histórico
```

Las clases del dominio son objetos Python simples, `dataclasses`, sin heredar de
widgets. Los elementos `QGraphicsItem` actúan como adaptadores visuales y no son
la fuente de verdad del documento.

El flujo de dependencias será:

```text
Interfaz PyQt6 ──> comandos ──> modelo de documento
      │                            ▲
      └──> renderizado ────────────┘
                                   ▲
              lector/escritor ─────┘
```

El modelo no importará módulos de `ui`. El lector tampoco creará widgets ni mostrará diálogos.

## Fase 0 — Conservar y especificar

**Objetivo:** definir qué significa ser compatible antes de escribir la nueva aplicación.

- [x] Mantener la etiqueta histórica `1.0` y declarar el árbol C/GTK como `legacy` (reorganizado bajo `legacy/`).
- [x] Confirmar responsables, licencia GPL-3.0-or-later y procedencia de los doodles, iconos y documentos incluidos (créditos y atribuciones en AUTHORS, debian/copyright y NOTICE).
- [x] Reunir en `tests/fixtures/` archivos `.tbo` reales anonimizados, ejemplos del repositorio y casos mínimos.
- [ ] Añadir fixtures con Unicode, rutas largas, imágenes externas, SVG, transformaciones, varias páginas y recursos ausentes.
- [ ] Documentar el formato observado en `docs/file-format-v1.md`, incluidos separadores decimales y manejo de rutas.
- [ ] Crear una lista manual de comportamiento de TBO 1.0 y capturas de referencia.
- [ ] Guardar exportaciones PNG/PDF/SVG representativas para comparaciones posteriores.
- [ ] Publicar `CONTRIBUTING.md`, política de seguridad y criterios de revisión.

**Criterio de salida:** el comportamiento y los documentos que TBO 2 debe preservar están disponibles en el repositorio y pueden revisarse sin depender de memoria oral.

## Fase 1 — Esqueleto Python reproducible

**Objetivo:** establecer una base pequeña, instalable y comprobable.

- [x] Crear la distribución `src/`, `pyproject.toml` y un punto de entrada `tbo` (en la raíz del repositorio).
- [x] Fijar una versión mínima de Python (`requires-python = ">=3.11"`).
- [x] Declarar PyQt6 como dependencia y separar dependencias de ejecución y desarrollo.
- [x] Configurar pytest, pytest-qt, cobertura, Ruff y un comprobador de tipos.
- [ ] Adoptar un formateador automático y EditorConfig.
- [x] Añadir CI para Linux con las versiones mínima y actual de Python soportadas (Python 3.11 y 3.12).
- [ ] Ejecutar las pruebas Qt en modo headless dentro de CI (Xvfb); por ahora los tests de integración se ejecutan localmente con display, ya que el teardown de `QGraphicsView` aborta en los runners headless.
- [x] Crear una ventana mínima, mostrar una escena y verificar el arranque con una prueba de humo.
- [x] Documentar instalación, entorno de desarrollo y comandos de calidad iniciales.

**Criterio de salida:** un clon limpio instala TBO 2, abre la ventana mínima y pasa lint, tipos y pruebas en CI.

## Fase 2 — Modelo y compatibilidad `.tbo`

**Objetivo:** leer, representar y guardar documentos sin depender de la interfaz.

- [x] Modelar cómic, página, viñeta y objetos mediante tipos explícitos y `dataclasses`.
- [x] Definir las primeras invariantes: dimensiones válidas, colores y transformaciones finitas.
- [x] Implementar un lector `.tbo` v1 con parser XML seguro, límites de tamaño y errores con contexto.
- [x] Validar números finitos, rangos, atributos requeridos y elementos fuera de jerarquía.
- [x] Resolver rutas de recursos sin permitir escapes de directorio cuando se procese contenido empaquetado (`assets/resolver.py`).
- [x] Implementar un escritor determinista y con separador decimal independiente del locale.
- [x] Guardar de forma atómica mediante archivo temporal, sincronización y reemplazo del destino.
- [x] Producir mensajes útiles para archivos corruptos y representar recursos ausentes sin cerrar la aplicación.
- [x] Añadir pruebas `abrir -> guardar -> abrir` que comparen documentos semánticamente.
- [x] Añadir property-based tests y fuzzing al lector cuando la base de pruebas sea estable.
- [x] Escribir inicialmente v1 compatible; queda pendiente formalizar la decisión mediante ADR.

**Criterio de salida:** todo el corpus histórico válido se abre; el round-trip no pierde información; las entradas inválidas fallan de forma controlada; modelo y formato tienen cobertura mínima acordada —objetivo orientativo: 90 % en estos módulos críticos—.

## Fase 3 — Lienzo y renderizado

**Objetivo:** reproducir visualmente un documento sin implementar todavía todas las herramientas.

- [x] Construir el lienzo inicial con `QGraphicsScene` y `QGraphicsView`.
- [x] Crear adaptadores visuales iniciales para página, viñeta, texto, imagen y SVG.
- [ ] Mantener identificadores estables entre objetos del modelo y elementos gráficos.
- [x] Representar transformaciones existentes: posición, tamaño, rotación y volteo.
- [x] Añadir zoom, tamaño real, ajuste a ventana, desplazamiento y navegación entre páginas.
- [x] Implementar un renderer compartido para pantalla y exportación, evitando dos interpretaciones del documento.
- [x] Exportar PNG, PDF y SVG con dimensiones y nombres de salida comprobados.
- [ ] Crear pruebas visuales con imágenes de referencia y tolerancia documentada.
- [x] Probar recursos faltantes, SVG inválidos, imágenes grandes, HiDPI y fuentes no instaladas.

**Criterio de salida:** los fixtures se representan y exportan con paridad visual aceptada; el render puede ejecutarse sin mostrar la interfaz; las diferencias conocidas están documentadas.

## Fase 4 — Edición y undo/redo

**Objetivo:** alcanzar paridad funcional mediante operaciones reversibles.

- [x] Implementar `QUndoStack` y un comando por operación de documento (`QUndoStack` y primeros comandos listos).
- [x] Crear, eliminar, navegar y reordenar páginas mediante comandos reversibles.
- [x] Crear, eliminar, clonar, mover y redimensionar viñetas.
- [x] Añadir, seleccionar, mover, redimensionar, rotar, voltear, clonar y eliminar objetos (seleccionar, mover, clonar y eliminar listos para objetos existentes).
- [x] Implementar edición de texto, tipografía y color (alta de texto con tipografía y color lista; edición posterior pendiente).
- [x] Implementar importación de imágenes y SVG.
- [x] Integrar biblioteca de doodles y bocadillos con búsqueda y categorías.
- [x] Garantizar undo/redo para cada operación, incluidas acciones compuestas y drag continuo (cubierto para páginas, viñetas y primeras operaciones de objetos).
- [x] Añadir atajos de teclado y actualizar el estado de acciones según la selección.
- [x] Marcar el documento como modificado solo cuando su estado cambie realmente.
- [x] Probar secuencias largas de comandos y el regreso exacto al estado inicial (primeras secuencias verificadas).

**Criterio de salida:** todas las operaciones descritas en el README histórico funcionan y tienen pruebas de comandos; undo/redo no pierde objetos ni desincroniza escena y modelo.

## Fase 5 — Experiencia de escritorio y resiliencia

**Objetivo:** convertir el editor funcional en una aplicación segura y agradable de usar.

- [x] Diseñar ventana, menús, barra de herramientas, panel de propiedades y biblioteca con layouts adaptables.
- [x] Añadir diálogos de nuevo, abrir, guardar, guardar como, importar y exportar (nuevo/abrir/guardar/guardar como listos).
- [x] Avisar de cambios sin guardar y manejar cancelación o errores sin perder el documento activo.
- [x] Implementar recuperación automática de sesión y copias de seguridad recuperables.
- [x] Persistir preferencias con `QSettings`, sin mezclar configuración con documentos.
- [x] Añadir archivos recientes sin conservar rutas sensibles en logs o reportes.
- [x] Mejorar teclado, orden de foco, lectores de pantalla, contraste, tema oscuro y escalado HiDPI.
- [x] Extraer textos traducibles y recuperar las traducciones existentes cuando sigan siendo válidas.
- [x] Actualizar README, tutorial, capturas, iconos, `.desktop` y metadatos AppStream.
- [x] Probar Wayland y X11; documentar otras plataformas como experimentales hasta tener CI y responsable.

**Criterio de salida:** checklist completo de flujos de usuario; cero pérdidas de datos conocidas; accesibilidad básica verificada; recuperación probada después de cierre forzado.

## Fase 6 — Empaquetado y TBO 2.0

**Objetivo:** publicar una versión que una persona no desarrolladora pueda instalar y actualizar.

- [x] Definir versionado, changelog y política de soporte.
- [x] Crear paquetes reproducibles; Flatpak será el primer objetivo en Linux.
- [x] Evaluar PyInstaller u otra herramienta solo para plataformas con mantenimiento confirmado (Nuitka para Windows, PyInstaller para macOS, incluidos en el workflow manual).
- [x] Verificar que se incluyen Qt, plugins de plataforma, soporte SVG, traducciones y recursos necesarios.
- [x] Generar SBOM, checksums y artefactos firmados cuando la infraestructura lo permita.
- [x] Ejecutar pruebas de instalación, primera ejecución, actualización y desinstalación limpia.
- [x] Publicar una beta con migración reversible: TBO 2 nunca modifica el único original sin confirmación o copia segura (release `v2.0.0.dev0` con el `.deb`).
- [ ] Resolver todos los bloqueos de seguridad, datos y compatibilidad antes de la versión estable.
- [ ] Publicar `2.0.0` y archivar claramente las instrucciones del legado.

**Criterio de salida:** TBO 2.0 se instala desde un artefacto publicado, abre documentos 1.0, completa los flujos del MVP y puede ser liberado por más de una persona siguiendo documentación.

## Fase 7 — Evolución posterior

Solo después de alcanzar paridad y publicar 2.0:

- [ ] Formato autocontenido que empaquete imágenes/SVG con manifest y checksums.
- [x] Alineación y distribución de viñetas seleccionadas (menú Editar ▸ Alinear / Distribuir).
- [ ] Capas y agrupación avanzada.
- [ ] Guías y rejilla de dibujo (rejilla de ajuste visible ya implementada).
- [x] Bibliotecas de recursos instalables por el usuario (`~/.tbo/doodle/` y `~/.local/share/tbo/doodle/`).
- [ ] Plantillas de páginas.
- [ ] Mejor edición de texto y administración de fuentes conforme a sus licencias.
- [ ] Perfiles de impresión y exportación multipágina mejorada.
- [ ] Herramienta CLI para inspeccionar, validar, convertir y renderizar en modo headless.
- [ ] Optimización para documentos grandes basada en perfiles, no en suposiciones.
- [ ] Soporte oficial de Windows/macOS únicamente cuando exista CI y mantenimiento continuado.

## Matriz de prioridad

| Prioridad | Trabajo | Motivo |
| --- | --- | --- |
| P0 | Corpus histórico y especificación `.tbo` v1 | Define qué debe preservar la reimplementación. |
| P0 | Modelo Python independiente de la UI | Evita reproducir el acoplamiento del legado. |
| P0 | Parser seguro y guardado atómico | Protege memoria, documentos y rutas del usuario. |
| P0 | CI, lint, tipos y pruebas | Permite que Codex y colaboradores cambien código con una señal objetiva. |
| P1 | Render y pruebas visuales | Demuestra compatibilidad antes de crear todas las herramientas. |
| P1 | Comandos y undo/redo | Es la base de una edición confiable. |
| P1 | Paridad funcional y paquete instalable | Convierte la reescritura en un reemplazo real. |
| P2 | UX, accesibilidad y recuperación avanzada | Mejora el producto sin bloquear el primer prototipo. |
| P3 | Funciones posteriores a 2.0 | No deben retrasar compatibilidad ni seguridad. |

## Política de compatibilidad

- TBO 2 debe leer todos los `.tbo` válidos producidos por TBO 1.0 presentes en el corpus.
- Abrir y guardar no debe perder páginas, viñetas, objetos, texto, orden, transformaciones, colores ni referencias a recursos.
- No se sobrescribirá silenciosamente un archivo con información que el lector no comprende.
- Toda migración de formato incluirá fixtures de entrada/salida y una ruta de recuperación.
- Las comparaciones se harán sobre el modelo semántico; diferencias irrelevantes de espacios o orden de atributos XML no serán consideradas pérdida.
- La paridad visual tendrá tolerancias documentadas para diferencias legítimas entre motores de texto y renderizado.
- Los errores indicarán archivo y contexto sin exponer información sensible ni cerrar abruptamente la aplicación.

## Reglas de implementación

Cada pull request deberá:

1. Tener alcance pequeño y una razón observable.
2. Añadir pruebas o justificar la verificación manual necesaria.
3. Pasar formato, lint, tipos, pruebas y cobertura acordada.
4. No mezclar refactorizaciones, cambios funcionales y reformateos masivos.
5. Actualizar documentación, fixtures y traducciones cuando corresponda.
6. Mantener el modelo como fuente de verdad; la escena nunca guardará estado exclusivo del documento.

Reglas específicas para trabajo asistido por IA (por ejemplo, OpenCode):

- entregar una capacidad vertical pequeña y verificable en cada cambio;
- revisar primero el estado del proyecto y los cambios ya realizados antes de modificar archivos;
- pedir siempre pruebas junto con la implementación;
- no aceptar APIs inventadas sin comprobarlas contra PyQt6 instalado y su documentación;
- mantener type hints en las fronteras entre módulos;
- evitar abstracciones generales hasta que existan al menos dos usos reales;
- usar mensajes de commit convencionales y un cambio lógico por commit;
- revisar manualmente seguridad, persistencia y migraciones aunque CI esté verde;
- preguntar al mantenedor ante decisiones de compatibilidad, licencia o formato, en lugar de adivinar.

## Indicadores de salud

- CI verde en la rama principal para las versiones de Python soportadas.
- Cobertura del parser, escritor y modelo, además de cobertura global.
- Porcentaje de fixtures históricos que cargan, hacen round-trip y exportan.
- Número de operaciones editables respaldadas por comandos undo/redo.
- Diferencias visuales sin explicar y errores de renderizado.
- Tiempo de arranque, memoria y latencia con documentos de referencia.
- Crashes, pérdidas de datos y vulnerabilidades abiertas por severidad.
- Antigüedad de issues y pull requests sin clasificar.
- Al menos dos personas capaces de generar una release.

## Riesgos y mitigaciones

| Riesgo | Mitigación |
| --- | --- |
| La reescritura nunca alcanza paridad | Hitos verticales, fixtures y beta solo después de los flujos completos. |
| Se interpreta mal el formato legado | Especificación observada, corpus amplio y comparación semántica. |
| Diferencias de renderizado Qt/Cairo | Referencias visuales, tolerancias y revisión de casos de texto/SVG. |
| El modelo queda acoplado a `QGraphicsItem` | Objetos de dominio independientes y adaptadores visuales explícitos. |
| Undo/redo se añade demasiado tarde | Todas las mutaciones pasan por comandos desde la fase de edición. |
| PyQt6 dificulta alguna distribución | Prototipo temprano de empaquetado y ADR antes de considerar otro binding. |
| Recursos gráficos carecen de licencia clara | Auditoría antes de incluirlos en artefactos publicados. |
| Codex produce mucho código difícil de revisar | Cambios pequeños, type checking, pruebas y criterios de salida objetivos. |
| Solo una persona entiende el release | Automatización, documentación y ensayo por un segundo mantenedor. |

## Issues recomendados (pendientes)

1. Pruebas visuales con imágenes de referencia y tolerancia documentada (Fase 3).
2. Identificadores estables entre objetos del modelo y elementos gráficos (Fase 3).
3. Evaluar PyInstaller para plataformas con mantenimiento confirmado (Fase 6).
4. Adoptar un formateador automático y EditorConfig (Fase 1).
5. Documentar el formato observado en `docs/file-format-v1.md` (Fase 0).
6. Formato autocontenido que empaquete imágenes/SVG con manifest y checksums (Fase 7).
7. Herramienta CLI para inspeccionar, validar, convertir y renderizar en modo headless (Fase 7).
8. Capas, agrupación avanzada y guías de dibujo (Fase 7).
9. Plantillas de páginas y administración de fuentes (Fase 7).
10. Publicar `2.0.0` estable cuando se resuelvan los bloqueos restantes (Fase 6).

La reimplementación será exitosa cuando TBO 2 proteja los proyectos existentes, pueda instalarse de forma reproducible y permita añadir funciones mediante cambios pequeños y comprobables. La cantidad de código nuevo no será una medida de progreso por sí sola.
