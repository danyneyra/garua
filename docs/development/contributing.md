---
icon: lucide/hand-metal
---

# Contribuir

Garúa está abierto a mejoras en la CLI, el servidor MCP, el scraper, las guías
de uso y la referencia técnica. Antes de cambiar código, identifica si tu cambio
toca una interfaz de usuario, una tool MCP o un servicio compartido.

## Preparar el entorno

```bash
git clone https://github.com/danyneyra/garua.git
cd garua
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,docs]"
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

Verifica que el paquete cargue correctamente:

```bash
python -m garua --help
python -m garua_mcp
```

## Tipos de cambio

| Si cambias... | Revisa también |
| --- | --- |
| Una tool MCP | Docstring, `scripts/generate_tools_reference.py`, `docs/reference/tools.md`. |
| Una regla de análisis | Servicios, modelos, guías relacionadas y ejemplos de uso. |
| Descargas o scraping | Variables de entorno, timeouts, mensajes de error y notas de navegador. |
| CLI | `docs/usage/cli.md`, `docs/reference/cli.md` y ejemplos. |
| Documentación | Enlaces internos, build estricto y capturas o GIF si aplica. |

## Estilo de código

El proyecto usa herramientas declaradas en `pyproject.toml`:

```bash
black src scripts
isort src scripts
mypy src
```

Si agregas pruebas, ejecútalas con:

```bash
pytest
```

!!! note "Pruebas"
    Si una prueba depende del portal de SENAMHI o de navegador, intenta aislarla
    de la red cuando sea posible. Las reglas de parsing, métricas y servicios
    internos son mejores candidatas para pruebas unitarias.

## Actualizar documentación

La referencia de tools MCP se genera desde `src/garua/mcp_tools/*.py`:

```bash
python scripts/generate_tools_reference.py
```

Para revisar el sitio localmente:

```bash
zensical serve
```

Antes de enviar cambios, valida el sitio:

```bash
zensical build --clean --strict
```

## Criterios de documentación

- Escribe guías orientadas a tareas reales, no a funciones internas.
- Usa tildes y nombres consistentes: Garúa, SENAMHI, estación, periodo.
- Prefiere ejemplos con estaciones y fechas concretas.
- Evita duplicar la referencia técnica dentro de las guías.
- Mantén `docs/reference/tools.md` generado, no editado manualmente.
- No incluyas `site/` ni otros artefactos generados en el repositorio.

## Checklist antes de enviar

- El cambio mantiene la lógica compartida en `services/` cuando corresponde.
- Las tools MCP tienen docstrings claros y parámetros con `Field(description=...)`.
- La documentación afectada fue actualizada.
- `python scripts/generate_tools_reference.py` se ejecutó si cambió una tool MCP.
- `zensical build --clean --strict` pasa sin advertencias.
- Los cambios generados o temporales no están incluidos por accidente.

## Lecturas relacionadas

- [Arquitectura](architecture.md){data-preview}
- [Servidor MCP](mcp-server.md){data-preview}
- [Referencia de tools MCP](../reference/tools.md){data-preview}
