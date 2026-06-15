---
icon: lucide/list-checks
tags:
  - Ejemplos
---


# Ejemplos completos

## Encontrar una estación y descargar un mes

CLI:

```bash
garua --search Cabana
garua --station 108047 --mode month --year 2025 --month 7
```

MCP:

```text
Busca estaciones llamadas Cabana y descarga julio 2025 de la mejor coincidencia.
```

## Comparar dos meses

MCP:

```text
Compara la precipitacion de marzo 2025 y marzo 2026 para la estación Cabana.
```

Flujo esperado:

1. Buscar la estación si el código no esta claro.
2. Descargar los meses si no existen localmente.
3. Comparar metricas disponibles para el tipo de estación.
4. Entregar diferencias y advertencias de calidad si aparecen.

## Recomendar estación para un proyecto

MCP:

```text
Recomienda estaciones meteorologicas para un proyecto en lat -7.6133, lon -77.8204, 
con altitud objetivo de 3000 msnm y al menos 5 anos de historial.
```

Resultado esperado:

- Estación recomendada.
- Alternativas ordenadas.
- Score explicable por distancia, historial, estado operativo y altitud.

## Validar calidad antes de usar datos

MCP:

```text
Valida los datos de julio 2025 para la estación 108047 y dime si hay duplicados, S/D, 
trazas o fechas faltantes.
```

Usa este flujo antes de reportes técnicos o análisis sensibles.
