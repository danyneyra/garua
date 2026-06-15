---
icon: lucide/files
tags:
  - Comparar estaciones
---

# Comparar periodos

## Qué resuelve

Compara dos o mas meses o años de una misma estación y calcula diferencias entre metricas disponibles.

## Cuándo usarlo

Úsalo para responder preguntas como que mes fue más lluvioso, que año fue mas cálido o como cambio el nivel de río entre periodos.

## Ejemplo rápido

MCP:

```text
Compara marzo 2025 vs marzo 2026 para la estacion Cabana
```

## Flujo recomendado

1. Busca la estación si solo tienes el nombre.
2. Descarga los periodos si no existen localmente.
3. Compara los periodos con deduplicación activa.
4. Revisa diferencias absolutas, cambios porcentuales y warnings.

## Resultado esperado

Métricas por periodo, diferencias entre periodos y un resumen interpretativo en español.

## Problemas comunes

- No uses comparación para un solo periodo; usa resumen.
- Si faltan datos locales, descarga primero.
- Algunos cambios porcentuales no aplican cuando el valor base es cero o nulo.

## Detalle técnico conservado

El sistema detecta automáticamente cuatro esquemas: meteorológica convencional, meteorológica automática, hidrológica convencional e hidrológica automática. Las métricas se calculan según el esquema detectado para evitar mezclar columnas incompatibles.
