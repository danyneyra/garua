---
icon: lucide/history
tags:
  - Changelog
  - Releases
  - Versiones

title: "Novedades y versiones de Garúa"
description: "Consulta las novedades de Garúa: versiones publicadas, cambios del catálogo de estaciones, mejoras del servidor MCP y actualizaciones de instalación."
---

# Changelog

Esta página resume los cambios visibles para usuarios de Garúa. Las versiones
publicadas también pueden consultarse en las
[publicaciones de GitHub](https://github.com/danyneyra/garua/releases).

## v0.31.0 - 2026-10-28

### Servidor MCP

- Nuevos **prompts** para guiar análisis, comparaciones, revisión de calidad y
  selección de estaciones.
- Nuevos **resources** para consultar el catálogo, fichas, esquemas y archivos locales.
- Migración a **FastMCP 4.1.4 y MCP 2.3**, con respuestas y enlaces a archivos nativos.
- Corregido el error que impedía devolver archivos después de completar una descarga.
- Progreso de scraping mediante MCP: estación, periodo actual, reintentos,
  pausas y resultado final, cuando el cliente solicita notificaciones.
- Un único bloque JSON completo en Results, con los mismos datos que Structured
  Output, para clientes que solo utilizan el contenido de texto.
- Guía de descarga múltiple con `periods` para obtener varios meses de la misma
  estación en una sola llamada, con hasta una sesión de navegador.
- URI MCP para leer CSV descargados y exportados sin acceso directo al disco,
  conservando sus rutas locales. Los CSV pequeños se incluyen como recursos
  embebidos, con límites configurables por archivo y respuesta.
- Guía condicional para entregar archivos mediante Filesystem y las herramientas
  de adjuntos del cliente. La presentación como archivo descargable depende del cliente.

### Catálogo de estaciones

- **19 estaciones agregadas** y metadatos actualizados en **8 estaciones**;
  el catálogo reúne **1.029 estaciones**.
- Identificadas **53 estaciones ausentes del listado SENAMHI consultado**,
  conservadas para consultas históricas; su ausencia no confirma una baja oficial.
- Nuevos estados, fechas y notas para distinguir presencia en el listado y
  periodos anunciados, sin emitir juicios sobre la calidad de los datos descargados.
- Scripts para comparar, enriquecer y preparar actualizaciones del catálogo con informes y respaldos.

??? info "Ver las 19 estaciones agregadas"

    | Código | Estación |
    | --- | --- |
    | `106145` | TINGO DE PONAZA |
    | `106146` | CHUMBEMENIQUE |
    | `107142` | BELLAVISTA |
    | `110149` | ENTAZ |
    | `111293` | APATA |
    | `112283` | CHAQUICOCHA |
    | `114136` | PALPA |
    | `115153` | ILLPA |
    | `200203` | CABO INGA |
    | `212600` | HUAYABAMBA |
    | `240504` | LPO PUCALLPA |
    | `472210B6` | RIO GRANDE |
    | `4723C424` | BOCATOMA ZAMBA |
    | `4723D752` | CHIVAY |
    | `4724D566` | CIRATO |
    | `4726706A` | SAN IGNACIO |
    | `47284198` | CHALLACA |
    | `472A0766` | VILLA MARIA DEL TRIUNFO |
    | `472C57D4` | BAGUA |

??? info "Ver las 53 estaciones ausentes del listado SENAMHI"

    Listado consultado del 27 de octubre de 2026. Se conservan para consultas
    históricas; su ausencia del listado no confirma una baja oficial.

    | Código | Estación |
    | --- | --- |
    | `100128` | SAN RAMON |
    | `103012` | BELLAVISTA |
    | `105145` | SANTO DOMINGO |
    | `106067` | QUEROCOTILLO |
    | `106139` | POTRERILLO |
    | `107143` | OTUZCO |
    | `108106` | RS_TRUJILLO |
    | `109017` | RECUAY |
    | `110145` | OYON |
    | `110147` | SAN PEDRO DE MATIHUACA |
    | `111292` | PUENTE MAGDALENA II |
    | `112233` | VILLA MARIA DEL TRIUNFO |
    | `112268` | OXAPATA |
    | `113261` | LARAPA |
    | `113262` | PACHACUTEQ |
    | `113263` | PICCHU ALTO |
    | `114137` | CRUCERO |
    | `114139` | COPARA |
    | `115158` | SANTA LUCIA |
    | `116076` | SANTA RITA DE SIGUAS |
    | `116079` | HUASACACHE |
    | `116080` | TAHUACO |
    | `116084` | CAMANA |
    | `116086` | LAS SALINAS |
    | `116087` | BELLA ESPERANZA |
    | `210006` | SHANAO |
    | `210007` | PAUCARTAMBO |
    | `210503` | PUENTE EGUIGUREN |
    | `212500` | AGUA AZUL BOCATOMA |
    | `212900` | LA CAPILLA SENAMHI |
    | `213101` | PACARAN |
    | `213507` | RAMADILLAS |
    | `214400` | HUATIAPA |
    | `250310` | SHAPI |
    | `250311` | TULLUMAYO |
    | `250314` | PUMAC CHUPAN |
    | `250315` | CCARI GRANDE |
    | `250317` | HUANCARO |
    | `250318` | UNSAAC |
    | `250319` | REGIONAL |
    | `250320` | HILARIO MENDIVIL |
    | `250321` | QUISPIQUILLA |
    | `4722B04E` | MARCAPATA |
    | `4722F344` | LA TRANCA |
    | `4724E0FC` | REQUENA |
    | `4725B27A` | PAUCARAY |
    | `47262016` | CORA CORA |
    | `4727B78E` | AYAVIRI |
    | `47283708` | HUALLPOCA |
    | `4729867C` | QORIHUAYRACHINA |
    | `472AE494` | SANTA ROSA CHAPIMARCA GORE APU |
    | `472B16EA` | HUACULLO |
    | `472D1624` | PUENTE PEREZ |

??? info "Ver las 8 estaciones actualizadas"

    | Código | Estación | Cambios |
    | --- | --- | --- |
    | `100043` | FONAGRO (CHINCHA) | Coordenadas: latitud y longitud |
    | `112124` | ANTIOQUIA | Coordenadas: latitud y longitud |
    | `113058` | LAS VIÃ±AS (TACAMA) | Nombre: TACAMA → LAS VIÃ±AS (TACAMA) |
    | `116011` | PUNTA ATICO | Coordenadas: latitud y longitud |
    | `116082` | SAN FRANCISCO | Categoría: PLU → EMA |
    | `116083` | CAYMA | Categoría: PLU → EMA; Coordenadas: longitud |
    | `4728B11C` | FONAGRO | Coordenadas: latitud y longitud |
    | `472F00A6` | CABO INGA M | Coordenadas: latitud y longitud |

### Instalación y mantenimiento

- Mejoras SEO en la documentación: títulos y descripciones por página y un
  encabezado principal visible en la portada.
- **uv como instalación recomendada**, con guía previa para instalarlo y un
  prompt que permite solicitar ayuda a un asistente de IA.
- Límites de dependencias, instalación reproducible y pruebas automatizadas para
  reducir incompatibilidades en futuras actualizaciones.
- Instrucciones para citar Garúa en trabajos y publicaciones.

!!! note "Actualización del servidor MCP"
    Actualiza Garúa como paquete y reinicia el cliente MCP. Esta versión adopta
    FastMCP 4; evita actualizar FastMCP o MCP por separado en instalaciones anteriores.

## v0.30.0 - 2026-06-15

### Nueva etapa como Garúa

- El proyecto adopta el nombre **Garúa** y deja atrás la etapa inicial como
  `senamhi-scraper`.
- Se consolida como una herramienta para usar desde terminal, scripts y clientes de IA
  compatibles con MCP.
- Se actualizan los metadatos del paquete para publicación en PyPI.

### CLI

- `garua` abre la aplicación interactiva de terminal.
- Se mantienen opciones por parámetros para flujos automatizados.
- `garua --doctor` y `garua --health` ayudan a validar Python, sistema operativo,
  carpeta de salida y navegador disponible.

### Servidor MCP

- `garua-mcp` inicia el servidor MCP local por `stdio`.
- La referencia de herramientas MCP se genera desde el código para reducir
  diferencias entre implementación y documentación.
- Se agregan ejemplos de configuración para VS Code, Codex, Claude Desktop y
  otros clientes compatibles.

### Documentación

- Nueva documentación con Zensical.
- Guías por tarea para buscar estaciones, descargar datos, explorar CSV, resumir,
  comparar, validar calidad y recomendar estaciones.
- Referencias para herramientas MCP, CLI, variables de entorno, archivos de
  salida y criterios de calidad de datos.
- Instrucciones de instalación y actualización con `pip` y `pipx`.

### Empaquetado

- El paquete fuente mantiene un `sdist` liviano: incluye código, README,
  changelog, contributing, licencia y metadatos.
- Las dependencias de documentación quedan como extra opcional y no se instalan
  al usar `pip install garua`.

## Historia del Proyecto

Garúa nació como una herramienta CLI para descargar datos hidrometeorológicos del
SENAMHI. Con el tiempo evolucionó hacia una librería modular y un servidor MCP
para que asistentes de IA compatibles puedan buscar estaciones, descargar datos,
resumir, comparar y validar información sin escribir scripts manuales.
