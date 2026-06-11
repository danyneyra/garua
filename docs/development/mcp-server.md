# Servidor MCP

El servidor MCP se ejecuta con:

```bash
garua-mcp
```

Internamente registra tools por modulo:

- Estaciones y filtros.
- Estadísticas.
- Archivos CSV.
- Descarga.
- Recomendación.
- Comparación.
- Anomalías.
- Resúmenes.

## Principio operativo

El cliente MCP debe usar la tool más específica para la intención del usuario. No debe recalcular manualmente métricas que Garua ya cálcula.

## Agregar una tool

1. Implementa la lógica en `services/` cuando sea compartida o compleja.
2. Agrega la función MCP en el módulo correspondiente de `mcp_tools/`.
3. Escribe un docstring orientado al cliente MCP: cuándo usarla, cuándo no usarla, parámetros clave y respuesta.
4. Regenera `docs/reference/tools.md`.
5. Agrega o actualiza una guía de usuario si la tool habilita un flujo nuevo.
