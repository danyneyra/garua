# Arquitectura

Garua esta organizado como paquete Python con CLI, servicios de dominio y servidor MCP.

## Capas principales

- `src/garua/main.py`: entrada CLI.
- `src/garua/mcp_server.py`: servidor MCP y registro de tools.
- `src/garua/mcp_tools/`: adaptadores MCP por grupo funcional.
- `src/garua/services/`: lógica de estaciones, resúmenes, comparaciones, validación y archivos.
- `src/garua/schemas/`: modelos y serializadores de respuestas.
- `src/garua/scraping/`: descarga de datos desde SENAMHI.

## Regla de diseño

Las tools MCP deben delegar cálculos y reglas a servicios. El docstring de cada tool explica intención, uso correcto y restricciones para clientes MCP.

## Documentacion

Las guías de usuario viven en `docs/guides/`. La referencia de tools se genera desde `src/garua/mcp_tools/*.py` con `scripts/generate_tools_reference.py`.
