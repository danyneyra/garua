# Validar calidad de datos

## Qué resuelve

Detecta problemas de calidad en datos descargados: duplicados, fechas u horas faltantes, valores `S/D`, trazas `T`, no numéricos, rangos inválidos y precipitación negativa.

## Cuándo usarlo

Úsalo antes de reportes técnicos, comparaciones importantes o decisiones donde la confiabilidad del dato importe.

## Ejemplo rápido

MCP:

```text
Valida la calidad de datos de julio 2025 para la estación 108047
```

## Flujo recomendado

1. Descarga o confirma el archivo local.
2. Ejecuta validación para el período.
3. Filtra por severidad si necesitas concentrarte en advertencias o críticos.
4. Decíde si el periodo sirve para tu análisis o si necesitas otra estación.

## Resultado esperado

Listado de anomálias o problemas, severidad, conteos y advertencias útiles para interpretar el CSV.

## Problemas comunes

- `S/D` no equivale a cero.
- `T` representa traza de precipitación y puede tratarse como `0.05`, `0` o nulo.
- En estaciones automáticas, las horas faltantes pueden afectar acumulados y promedios.
