# Recomendar estación

## Que resuelve

Recomienda estaciones SENAMHI para un punto geográfico considerando distancia, historial disponible, estado operativo y similitud altitudinal opcional.

## Cuándo usarlo

Úsalo para proyectos ambientales, mineros, agrícolas, hidrológicos o estudios que requieren justificar la selección de estaciones.

## Ejemplo rápido

MCP:

```text
Recomienda estaciones meteorologicas para lat -7.6133, lon -77.8204, con altitud 3000 msnm y al menos 5 anos de datos.
```

## Flujo recomendado

1. Define coordenadas del punto de intéres.
2. Indica tipo de estación: meteorológica, hidrológica o ambas.
3. Agrega altitud objetivo si es relevante.
4. Define años mínimos de historial si el proyecto lo exige.
5. Revisa recomendación principal, alternativas y desglose del score.

## Resultado esperado

Una estación recomendada, alternativas ordenadas y una explicación en español del score.

## Problemas comunes

- Si no hay resultados, aumenta el radio de búsqueda.
- Si la altitud importa, inclúyela; cambia el ranking.
- Para análisis histórico, pide un mínimo de años disponibles.

## Detalle técnico conservado

El score pondera distancia, historial, estado operativo y altitud cuando se proporciona. La recomendación busca ser defendible en contextos técnicos, no solo encontrar la estación mas cercana.
