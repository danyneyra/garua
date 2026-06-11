# Calidad de datos

Garua trata los datos SENAMHI con reglas explicitas para evitar conclusiones incorrectas.

## Valores faltantes

`S/D` significa sin datos. En resumenes, comparaciones y validaciones se trata como valor faltante, no como `0`.

## Trazas de precipitación

`T` representa traza de precipitación. La política configurable puede tratarla como:

- `as_0_05`: usa `0.05`.
- `as_0`: usa `0`.
- `as_null`: la trata como faltante.

## Duplícados

Las herramientas de análisis pueden deduplicar registros por fecha u hora antes de calcular métricas. Esto es especialmente importante en comparaciones.

## Fechas u horas faltantes

En estaciones convencionales se revisan días faltantes. En estaciones automáticas se revisan registros horarios faltantes cuando el esquema lo permite.

## Rangos inválidos

La validación puede detectar valores fuera de rango, precipitación negativa y consistencia entre temperatura máxima y mínima cuando aplica.
