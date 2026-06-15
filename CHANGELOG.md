# Changelog - Garúa

Todos los cambios relevantes del proyecto se documentan en este archivo.

## [Unreleased]

### Documentación

- Se agrega una sección para actualizar Garúa con `pip` y `pipx`.
- Se agrega una página de changelog dentro de la documentación pública.

## [0.30.0] - 2026-06-11

### Primera versión pública como Garúa

- Renombramiento del proyecto de `senamhi-scraper` a `garua`.
- Nueva identidad conectada con [garua.app](https://garua.app).
- Paquete preparado para publicación como CLI y servidor MCP.
- Versión alineada entre `pyproject.toml` y `src/garua/settings.py`.

### CLI

- Se documenta Garúa como app interactiva de terminal: ejecutar `garua` abre el menú guiado.
- Se mantiene el uso por parámetros para flujos automatizados:
  - `garua --search Cabana`
  - `garua --station 108047 --mode month --year 2025 --month 7`
- Se agrega captura de la interfaz CLI en `docs/images/garua-cli-ui.jpg`.
- Se agregan comandos de diagnóstico con `garua --doctor` y `garua --health`.

### Servidor MCP

- Servidor MCP ejecutable con `garua-mcp`.
- Referencia actualizada de tools MCP generada desde docstrings del código.
- Configuración documentada por cliente:
  - VS Code con GitHub Copilot.
  - Claude Desktop.
  - Codex con `config.toml`.
  - Otros clientes compatibles con MCP.

### Documentación

- README reducido a portada de proyecto para GitHub/PyPI.
- Nueva estructura de documentación en `docs/`:
  - `quickstart.md`
  - `installation.md`
  - `usage/cli.md`
  - `usage/mcp.md`
  - `usage/examples.md`
  - guías por tarea en `docs/guides/`
  - referencia técnica en `docs/reference/`
  - notas de desarrollo en `docs/development/`
- Se agregan guías para buscar estaciones, descargar datos, explorar CSV, resumir periodos, comparar periodos, validar calidad y recomendar estaciones.
- Se agregan referencias para variables de entorno, archivos de salida y calidad de datos.
- `INSTALL.md` queda como puente corto hacia `docs/installation.md`.
- `docs/COMPARISON_SYSTEM.md` y `docs/RECOMMENDATION_SYSTEM.md` quedan como documentos puente hacia las nuevas guías.
- Se agrega `CONTRIBUTING.md` para colaboración open source.

### Empaquetado

- `pyproject.toml` actualizado con metadata de publicación:
  - descripción orientada a CLI interactiva + MCP.
  - URLs del repositorio `danyneyra/garua`.
  - classifiers y keywords adicionales.
  - `license = "MIT"`.
- Se declaran dependencias directas usadas por el paquete:
  - `mcp`
  - `rich`
- El `sdist` queda liviano: incluye paquete fuente, README, changelog, contributing, licencia y metadata, sin empaquetar `docs/` ni assets pesados.

### Herramientas destacadas

- Búsqueda y filtrado de estaciones SENAMHI.
- Recomendación de estaciones por distancia, historial, estado operativo y altitud.
- Descarga histórica desde SENAMHI a CSV.
- Listado, preview y extracción de archivos CSV locales.
- Resumen de periodos individuales.
- Comparación de dos o más periodos.
- Detección de anomalías y problemas de calidad.
- Estadísticas por inventario, departamento y jerarquía administrativa.

## Historia del proyecto

Garúa nació como una herramienta CLI interactiva para descargar datos hidrometeorológicos del SENAMHI. Con el tiempo evolucionó hacia una librería modular y servidor MCP para que asistentes compatibles puedan buscar estaciones, descargar datos, resumir, comparar y validar información sin que el usuario tenga que escribir scripts.

### Evolución

- 2024: desarrollo inicial como `senamhi-scraper`.
- 2025: incorporación de automatización con Zendriver para trabajar con el sitio de SENAMHI.
- 2026: refactorización modular, servidor MCP y preparación para publicación open source como `garua`.

### Por qué 0.30.0

La versión `0.30.0` marca el inicio de una etapa pública del proyecto bajo el nombre Garúa.
