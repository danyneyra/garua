# Resumir un período

## Qué resuelve

Calcula métricas de un período individual para una estación: precipitacion, dias con lluvia, temperatura, humedad, viento o nivel de río según el tipo de estación.

## Cuándo usarlo

Úsalo cuando quieres saber como fue un mes, un año o un rango continuo para una sola estación.

## Ejemplo rápido

MCP:

```text
Resume julio 2025 para la estación 108047 e incluye calidad general
```

## Flujo recomendado

1. Confirma que el CSV del periodo exista localmente.
2. Usa resumen para un único periodo.
3. Pide comparación solo si hay dos o más periodos.
4. Revisa warnings sobre duplicados, faltantes o trazas.

## Resultado esperado

Métricas compatibles con el esquema detectado, cantidad de registros usados, advertencias y un resumen narrativo.

## Problemas comunes

- Si no hay archivo local, descarga el período primero.
- Si el período tiene muchos `S/D`, las métricas pueden ser parciales.
- Las trazas `T` de precipitación usan una política configurable.
