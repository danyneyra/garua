---
icon: lucide/file-output
tags:
  - Salida de Archivos
  - Archivos CSV
---

# Archivos de salida

Garúa guarda archivos CSV con nombres descriptivos por estación y período.

## Patrones comunes

```text
Estacion-YYYYMM.csv
Estacion-YYYY.csv
Estacion-YYYY-YYYY.csv
```

Ejemplos:

```text
Cabana-202507.csv
Cabana-2025.csv
Cabana-2020-2025.csv
```

## Carpetas

!!! info "Carpeta de salida"
    Por defecto, los archivos se guardan en la carpeta Documentos del usuario. En Windows, la ruta es `C:\Users\TuUsuario\Documents\Garua\csv`.

    Si deseas cambiar la carpeta de salida, define la variable de entorno `GARUA_OUTPUT_DIR` con la ruta que quieras usar. Para más detalles de la configuración de variables de entorno en [Variables de Entorno](../reference/environment.md){data-preview}

Los archivos se organizan por estación cuando el flujo incluye metadatos suficientes. La estructura puede incluir nombre, código, tipo y categoria para evitar ambiguedades entre estaciones con nombres similares.

## CSV mensuales y consolidados

- Un CSV mensual contiene un mes específico.
- Un CSV anual contiene los meses disponibles de un año.
- Un CSV multianual cubre un rango de años.

Si necesitas compartir o procesar un mes independiente desde un consolidado, usa el flujo de extracción mensual desde MCP.

## Valores especiales

- `S/D`: sin datos; no debe interpretarse como cero.
- `T`: traza de precipitación; precipitación < 0.1 mm/día.
