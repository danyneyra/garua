---
icon: lucide/sheet
tags:
  - Archivos
  - CSV
---


# Explorar CSV

## Qué resuelve

Permite revisar archivos descargados, confirmar períodos disponibles y ver una muestra tabular antes de analizar.

## Cuándo usarlo

Úsalo despúes de descargar datos o cuando quieres saber que archivos locales ya existen.

## Ejemplo rápido

MCP:

```text
Lista los archivos descargados para la estación 108047 en 2025
Muestra una vista previa del CSV de julio 2025 para la estación 108047
```

## Flujo recomendado

1. Lista archivos locales por estación, año o mes.
2. Identifica si hay un CSV mensual, anual o multianual que cubra el período.
3. Abre una vista previa con filas y columnas limitadas.
4. Extrae un mes desde un consolidado si necesitas un archivo mensual independiente.

## Resultado esperado

Rutas de archivos, período detectado, nombre del CSV y una muestra legible de columnas y filas.

## Problemas comunes

- Si un mes no aparece como archivo individual, puede estar dentro de un CSV anual o multianual.
- Si hay columnas inesperadas, identifica si la estación es convencional o automatica.
- No confundas `S/D` con cero; significa sin datos.
