# Roadmap de modernización de TBO

Este documento propone recuperar TBO como un editor de cómics mantenible, seguro y distribuible, sin perder los proyectos `.tbo` existentes. No es un calendario cerrado: cada fase tiene condiciones de salida verificables y la siguiente fase comienza únicamente cuando se cumplen.

## Punto de partida

La última revisión del repositorio es de abril de 2013 y la versión publicada es la 1.0. La aplicación contiene unas 8.800 líneas de C y utiliza GTK 3, GLib/GObject, Cairo, librsvg, gettext/intltool y Autotools.

La funcionalidad central sigue siendo valiosa: edición por páginas y viñetas, objetos SVG, imágenes y texto, deshacer/rehacer, biblioteca de dibujos y exportación a PNG, PDF y SVG. Sin embargo, hoy no existe una forma reproducible de compilarla ni una suite automática que permita cambiarla con confianza.

Hallazgos concretos de la auditoría inicial:

- `./autogen.sh` depende de `gnome-autogen.sh`/`gnome-common`, una herramienta ya ausente en muchos sistemas modernos.
- No hay integración continua, pruebas automáticas reales, análisis estático ni formato de código acordado. `typestest` y `undotest` son ejecutables auxiliares, no una suite integrada.
- La interfaz usa numerosas API obsoletas de GTK 3: `GtkUIManager`, `GtkAction`, iconos stock, `GtkHBox`, `GtkMisc`, `GdkColor`, dibujo directo sobre ventanas GDK y diálogos síncronos.
- El uso de librsvg corresponde a su API antigua (`rsvg_handle_get_dimensions` y `rsvg_handle_render_cairo`).
- El lector `.tbo` copia atributos XML a buffers fijos con `sprintf`; un archivo manipulado puede desbordarlos. También mantiene estado global durante el parseo y apenas informa errores al usuario.
- El guardado escribe directamente al destino con `fopen`, sin operación atómica, copia de recuperación ni propagación adecuada de errores.
- Las rutas se construyen con `strcpy`/`strcat`, incluso a partir del entorno, y varios recursos tienen límites fijos de 255 caracteres.
- El formato `.tbo` no declara versión, esquema, reglas de compatibilidad ni política para recursos externos.
- Los paquetes de Debian y Arch, el archivo `.desktop`, URLs, metadatos y documentación de colaboración están desactualizados.

## Principios de la recuperación

1. **No romper proyectos existentes.** Los archivos `.tbo` 1.0 forman parte de la API pública y se conservarán como fixtures de regresión.
2. **Estabilizar antes de migrar.** Primero se obtendrá una versión mantenible sobre GTK 3; la migración a GTK 4 será posterior y deliberada.
3. **Separar el documento de la interfaz.** Carga, guardado, modelo y renderizado deben poder probarse sin abrir una ventana.
4. **Cambios pequeños y reversibles.** Cada pull request debe compilar, probarse y tener un alcance acotado.
5. **Seguridad por defecto.** Un archivo corrupto debe producir un error útil, nunca un cierre inesperado, corrupción del archivo original o acceso arbitrario fuera de lo previsto.
6. **Distribución reproducible.** El proyecto debe poder construirse de forma documentada en una distribución soportada y en CI.

## Decisiones que deben quedar registradas

Las decisiones estructurales se documentarán en `docs/adr/` antes de implementarlas:

- ADR-001: mantener C y GLib/GObject durante la recuperación.
- ADR-002: Meson como sistema de construcción, sustituyendo Autotools.
- ADR-003: estabilización temporal en GTK 3 y criterios para pasar a GTK 4.
- ADR-004: evolución versionada y compatible del formato `.tbo`.
- ADR-005: estrategia para incluir, enlazar o empaquetar imágenes y SVG externos.

Reescribir la aplicación en otro lenguaje no forma parte del rescate inicial. Solo se reconsiderará con datos obtenidos después de separar y probar el núcleo.

## Fase 0 — Gobernanza y conservación

**Objetivo:** evitar que la modernización pierda historia, alcance o compatibilidad.

- [ ] Confirmar mantenedores activos, canal de contacto, licencia GPL-3.0-or-later y procedencia/licencia de cada biblioteca de dibujos.
- [ ] Publicar `CONTRIBUTING.md`, código de conducta, política de seguridad y plantillas de issues/pull requests.
- [ ] Definir ramas protegidas, revisión obligatoria y etiquetas `bug`, `security`, `format`, `gtk4`, `packaging` y `good first issue`.
- [ ] Etiquetar el estado histórico como `v1.0-legacy` si la etiqueta `1.0` existente no basta para las herramientas actuales.
- [ ] Reunir un corpus de archivos `.tbo`: ejemplos del repositorio, archivos reales anonimizados, entradas mínimas, corruptas y casos con Unicode/rutas largas.
- [ ] Documentar el comportamiento visible actual con una lista de comprobación manual y capturas de referencia.

**Criterio de salida:** responsables y alcance publicados; artefactos históricos preservados; corpus de compatibilidad disponible en `tests/fixtures/`.

## Fase 1 — Volver a compilar y observar

**Objetivo:** disponer de una construcción reproducible sin modificar aún la experiencia de usuario.

- [ ] Añadir Meson con opciones de desarrollo (`warning_level`, sanitizers y tests) y mantener Autotools solo durante una ventana de transición.
- [ ] Declarar versiones mínimas probadas de GCC/Clang, Meson, GTK 3, GLib, Cairo y librsvg.
- [ ] Crear un entorno de desarrollo reproducible —contenedor o configuración equivalente— y documentar `meson setup`, `meson compile` y `meson test`.
- [ ] Corregir los errores de compilación con toolchains actuales y elevar advertencias gradualmente; no activar `-Werror` global hasta limpiar el legado.
- [ ] Integrar CI para al menos GCC y Clang, compilación debug/release, `meson test` y generación del paquete fuente.
- [ ] Añadir `clang-format`, EditorConfig y comprobaciones de formato sin mezclar un reformateo masivo con cambios funcionales.
- [ ] Ejecutar análisis estático (`clang-tidy`/scan-build) y ASan/UBSan sobre pruebas y corpus.
- [ ] Registrar en issues los warnings GTK/librsvg y defectos encontrados, separando bloqueo de compilación de migración futura.

**Criterio de salida:** un clon limpio compila mediante instrucciones documentadas; CI está verde con dos compiladores; los binarios auxiliares se ejecutan desde `meson test`.

## Fase 2 — Blindar datos y comportamiento

**Objetivo:** poder abrir, guardar y exportar sin comprometer archivos ni memoria.

### Formato y persistencia

- [ ] Extraer carga/guardado del estado global de la UI a una API de documento con errores `GError` y ownership explícito.
- [ ] Sustituir `sprintf`, `strcpy`, `strcat` y buffers de ruta fijos por funciones GLib con memoria dinámica y validación de límites.
- [ ] Validar tipos, rangos, jerarquía, campos requeridos, codificación UTF-8 y tamaño máximo antes de crear objetos.
- [ ] Rechazar de forma segura XML truncado, elementos fuera de contexto y recursos inválidos; mostrar mensajes accionables.
- [ ] Implementar guardado atómico en el mismo sistema de archivos, comprobación de errores y recuperación ante fallo.
- [ ] Hacer que el separador decimal del formato sea independiente de la configuración regional.
- [ ] Formalizar `.tbo` v1 y añadir una versión de formato para futuras escrituras, manteniendo lectura de archivos históricos.
- [ ] Decidir cómo tratar rutas absolutas, relativas y recursos faltantes; impedir escapes de directorio cuando se abra contenido empaquetado.

### Pruebas

- [ ] Convertir undo/redo y tipos en pruebas GLib reales.
- [ ] Añadir pruebas unitarias del modelo, transformaciones, selección, serialización y exportación.
- [ ] Añadir pruebas de ida y vuelta: `abrir -> guardar -> abrir` debe conservar el documento de forma semántica.
- [ ] Crear imágenes de referencia para render PNG con una tolerancia explícita y pruebas estructurales para PDF/SVG.
- [ ] Incorporar fuzzing del parser `.tbo` y conservar cada crash como regresión.
- [ ] Probar nombres Unicode, rutas largas, cero páginas, dimensiones límite, recursos ausentes y errores de disco.

**Criterio de salida:** el corpus histórico abre correctamente; las entradas inválidas fallan de forma controlada; no hay hallazgos conocidos de ASan/UBSan en carga, guardado o exportación; cobertura del núcleo medida y con umbral inicial acordado (objetivo orientativo: 70 % de líneas).

## Fase 3 — Versión de rescate en GTK 3

**Objetivo:** publicar una versión útil antes de asumir el riesgo de GTK 4.

- [ ] Actualizar librsvg a su API soportada y eliminar API GTK 3 obsoleta donde sea posible sin cambiar de toolkit.
- [ ] Adoptar `GtkApplication`, `GAction`/`GMenu`, recursos GResource y nombres de iconos del tema.
- [ ] Sustituir colores y tipografía antiguas por `GdkRGBA` y APIs actuales de Pango.
- [ ] Corregir pérdidas de memoria, ownership ambiguo, crashes y todos los warnings GTK reproducibles.
- [ ] Implementar aviso de cambios sin guardar, guardado seguro, recuperación y mensajes de error visibles.
- [ ] Completar undo/redo para mover, redimensionar y rotar, deuda ya marcada en el código.
- [ ] Mejorar navegación por teclado, foco, nombres accesibles, contraste y escalado HiDPI.
- [ ] Actualizar traducciones y automatizar comprobaciones de catálogos gettext.
- [ ] Renovar README, ayuda, capturas, metadatos AppStream y `.desktop`.
- [ ] Producir al menos un paquete instalable y verificable; Flatpak es el candidato preferido para aislar diferencias entre distribuciones.

**Criterio de salida:** release `1.1.0` instalable; funciones del README verificadas; cero crashes conocidos de severidad alta; apertura y guardado compatibles con v1.0; checklist manual completada en Wayland y X11.

## Fase 4 — Separar núcleo, renderizado e interfaz

**Objetivo:** reducir el coste y el riesgo de la migración de toolkit.

- [ ] Definir módulos explícitos: `document`, `io`, `render`, `commands/undo`, `assets` y `ui`.
- [ ] Eliminar dependencias GTK del modelo y del parser; permitir pruebas completamente headless.
- [ ] Encapsular Cairo/librsvg detrás de una API de renderizado usada tanto por pantalla como por exportación.
- [ ] Reemplazar acceso directo a campos y singletons por APIs con invariantes claras.
- [ ] Centralizar las operaciones editables como comandos para que undo/redo sea completo y consistente.
- [ ] Introducir una API de recursos que resuelva biblioteca, imágenes del usuario y recursos faltantes de manera uniforme.
- [ ] Medir rendimiento y memoria con documentos grandes; fijar presupuestos antes de optimizar.

**Criterio de salida:** modelo, I/O y render se compilan y prueban sin GTK; ninguna operación de documento depende de widgets; pruebas de regresión visual estables.

## Fase 5 — Migración a GTK 4

**Objetivo:** eliminar la dependencia de GTK 3 sin reescribir simultáneamente el núcleo.

- [ ] Crear un inventario de cada API sin equivalente directo y un prototipo que valide lienzo, zoom, selección y drag-and-drop.
- [ ] Migrar dibujo y eventos a los mecanismos de GTK 4, evitando acceso directo a `GdkWindow`.
- [ ] Migrar menús/atajos a acciones, controladores de eventos y shortcuts de GTK 4.
- [ ] Sustituir los árboles y barras de herramientas con widgets/modelos GTK 4 mantenidos.
- [ ] Convertir diálogos de archivo y flujos modales a operaciones asíncronas donde corresponda.
- [ ] Validar portapapeles, drag-and-drop, tablet/ratón, escalado, temas claro/oscuro y Wayland.
- [ ] Mantener los mismos fixtures y pruebas de render para demostrar que la migración no altera documentos.
- [ ] Retirar GTK 3 y Autotools solo después de que la nueva interfaz alcance paridad.

**Criterio de salida:** release `2.0.0` sobre GTK 4 con paridad funcional documentada, sin dependencias GTK 3 y con compatibilidad de lectura/escritura declarada.

## Fase 6 — Evolución posterior

Estas mejoras se priorizarán después del rescate, según demanda demostrable:

- [ ] Formato empaquetado autocontenido para incrustar recursos con manifest y checksums.
- [ ] Recuperación automática de sesión y copias versionadas.
- [ ] Gestión de capas, agrupación completa, alineación y guías.
- [ ] Plantillas de página y bibliotecas de recursos instalables.
- [ ] Mejor edición de texto y soporte de fuentes incrustadas cuando su licencia lo permita.
- [ ] Exportación multipágina mejorada y perfiles de impresión.
- [ ] API o herramienta de línea de comandos para renderizar y convertir en modo headless.
- [ ] Paquetes nativos adicionales solo si existe una persona responsable de mantenerlos.

## Matriz de prioridad inicial

| Prioridad | Trabajo | Motivo |
| --- | --- | --- |
| P0 | Construcción reproducible y CI | Sin una señal automática no es seguro aceptar cambios. |
| P0 | Parser con límites y guardado atómico | Protege memoria y proyectos del usuario. |
| P0 | Fixtures `.tbo` y pruebas de ida y vuelta | Define la compatibilidad antes de refactorizar. |
| P1 | Errores, ownership y sanitizers | Reduce crashes y deuda invisible. |
| P1 | Release de rescate GTK 3 | Devuelve valor sin bloquearse por la migración completa. |
| P1 | Separación modelo/UI/render | Hace viable GTK 4 y el testing headless. |
| P2 | GTK 4 | Garantiza mantenimiento a largo plazo una vez estabilizado el núcleo. |
| P3 | Funciones nuevas | No deben desplazar seguridad, compatibilidad ni distribución. |

## Política de compatibilidad del formato

- TBO 1.1 debe leer todos los `.tbo` válidos producidos por 1.0.
- Un archivo abierto y guardado no debe perder páginas, objetos, texto, transformaciones, colores ni referencias a recursos.
- Las extensiones nuevas serán versionadas. Los lectores deben ignorar extensiones opcionales desconocidas solo cuando hacerlo no cambie el significado del documento.
- No se sobrescribirá silenciosamente un documento que requiera funciones que esta versión no comprende.
- Toda migración tendrá fixtures de antes/después y se documentará en `docs/file-format.md`.
- Los errores incluirán archivo y contexto, sin filtrar datos sensibles ni abortar el proceso.

## Flujo de entrega y calidad

Cada cambio deberá:

1. Referenciar un issue y explicar el comportamiento afectado.
2. Incluir pruebas o justificar por qué solo admite verificación manual.
3. Compilar sin nuevas advertencias y pasar CI, sanitizers y análisis estático aplicables.
4. Actualizar documentación, traducciones y fixtures cuando corresponda.
5. Evitar mezclar cambios funcionales, migraciones mecánicas y reformateos masivos.

Antes de cada release se verificará:

- instalación, primera ejecución y desinstalación limpia;
- apertura de todo el corpus histórico;
- guardado, reapertura y recuperación frente a errores;
- exportación PNG/PDF/SVG de una y varias páginas;
- operaciones de selección, texto, imágenes, SVG, zoom y undo/redo;
- teclado, accesibilidad básica, HiDPI, Wayland y X11;
- traducciones, metadatos, licencias y artefactos firmados/checksums.

## Indicadores de salud

- CI verde en la rama principal y releases reproducibles.
- Tiempo medio de resolución de vulnerabilidades y crashes críticos.
- Número de warnings de compilación, GTK, sanitizers y análisis estático: tendencia hasta cero.
- Cobertura del núcleo y número de fixtures históricos sin regresión.
- Porcentaje de operaciones editables cubiertas por undo/redo.
- Issues sin clasificar y antigüedad de pull requests.
- Al menos dos personas capaces de realizar una release documentada.

## Riesgos principales

| Riesgo | Mitigación |
| --- | --- |
| Migrar a GTK 4 y cambiar la arquitectura a la vez | Publicar primero 1.1 en GTK 3 y desacoplar el núcleo. |
| Romper `.tbo` históricos | Corpus, especificación y pruebas de ida y vuelta desde la fase 0. |
| Recursos SVG o imágenes no disponibles | Política explícita de rutas y futuro formato autocontenido. |
| Trabajo de infraestructura sin release visible | Hitos cortos y una versión de rescate antes de GTK 4. |
| Dependencia de una sola persona | Proceso de release documentado, revisión y rotación de responsables. |
| Bibliotecas gráficas con licencia dudosa | Auditoría de procedencia antes de redistribuir paquetes. |

## Próximos issues recomendados

Los primeros cambios deben poder revisarse por separado:

1. Añadir corpus inicial y pruebas GLib para el undo existente.
2. Introducir Meson en paralelo con Autotools.
3. Añadir CI con GCC/Clang y build debug.
4. Integrar ASan/UBSan y capturar la línea base de fallos.
5. Reemplazar copias sin límite en `comic-load.c` y `tbo-files.c`.
6. Añadir pruebas de parser inválido y rutas largas.
7. Implementar guardado atómico con propagación de `GError`.
8. Especificar `.tbo` v1 y añadir pruebas de ida y vuelta.
9. Actualizar librsvg sin cambiar todavía de GTK.
10. Preparar y publicar `1.1.0-alpha.1` como primera evidencia del rescate.

La modernización se considerará exitosa no cuando todo el código parezca nuevo, sino cuando TBO vuelva a aceptar cambios con confianza, proteja los proyectos existentes y tenga un camino sostenible de releases.
