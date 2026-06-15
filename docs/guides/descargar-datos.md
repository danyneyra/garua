---
icon: lucide/download
tags:
  - Descargar
  - CSV
  - Datos
---

# Descargar datos

## Qué resuelve

Descarga datos históricos del SENAMHI y los guarda como CSV para análisis local.

## Cuándo usarlo

Úsalo cuando ya conoces la estación y necesitas obtener un mes, un año completo o un rango de años.

## Importante

La descarga abre un navegador local para acceder al sitio de SENAMHI, resolver o superar la verificación Cloudflare Turnstile cuando aparece, y capturar los datos necesarios para generar el CSV. Durante ese proceso el navegador puede permanecer abierto unos minutos.

## Ejemplo rápido

```bash
garua --station 108047 --mode month --year 2025 --month 7
```

MCP:

```text
Descarga julio 2025 de la estación 108047
```

## Flujo recomendado

1. Busca la estación si no tienes código.
2. Revisa disponibilidad histórica para el periodo.
3. Descarga el período solicitado.
4. Abre una vista previa del CSV si necesitas confirmar columnas o filas.
5. Resume, compara o válida calidad.

## Resultado esperado

Uno o más archivos CSV con nombres descriptivos por estación y período.

## Problemas comunes

- El sitio de SENAMHI puede tardar o fallar temporalmente; reintenta si el error parece de red.
- Para el mes actual, considera forzar una descarga nueva si ya tenías un CSV parcial.
- Si no hay datos en el período, confirma la disponibilidad histórica de la estación.
