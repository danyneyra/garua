"""Generate docs/reference/tools.md from MCP tool docstrings.

This script parses source files without importing Garua, so it is safe to run
even when browser or MCP dependencies are not installed.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "src" / "garua" / "mcp_tools"
OUTPUT_FILE = ROOT / "docs" / "reference" / "tools.md"


@dataclass
class ToolDoc:
    name: str
    module: str
    description: str
    parameters: list[str]
    prompt: str
    flow_note: str


PROMPTS = {
    "search_stations": "Busca estaciones llamadas Cabana",
    "get_station_info": "Dame la ficha de la estacion 108047",
    "get_all_stations": "Lista las primeras estaciones disponibles",
    "export_all_stations_csv": "Exporta el catalogo completo de estaciones a CSV",
    "check_data_availability": "Desde cuando hay datos para la estacion 108047?",
    "filter_stations_by_location": "Busca estaciones en Arequipa, provincia Caylloma",
    "filter_stations_by_altitude": "Busca estaciones sobre 3000 msnm",
    "filter_stations_advanced": (
        "Busca estaciones meteorologicas activas en Puno sobre 3500 msnm"
    ),
    "find_stations_near": "Busca estaciones cerca de lat -7.61, lon -77.82",
    "recommend_station_for_point_tool": (
        "Recomienda una estacion para lat -7.61, lon -77.82 con altitud 3000 msnm"
    ),
    "stations_count": "Cuantas estaciones tienes disponibles?",
    "stations_summary": "Resume el inventario de estaciones por tipo y estado",
    "get_departments_summary": "Que departamentos tienen mas estaciones?",
    "get_location_hierarchy": "Muestra la jerarquia de ubicaciones con estaciones",
    "list_downloaded_files": (
        "Lista archivos descargados para la estacion 108047 en 2025"
    ),
    "read_csv_preview": (
        "Muestra una vista previa del CSV de julio 2025 para la estacion 108047"
    ),
    "extract_month_from_csv": (
        "Extrae julio 2025 desde el CSV consolidado de la estacion 108047"
    ),
    "scrape_station_data": "Descarga julio 2025 de la estacion 108047",
    "summarize_station_data_tool": "Resume julio 2025 para la estacion 108047",
    "compare_periods_tool": "Compara marzo 2025 vs marzo 2026 para la estacion 108047",
    "detect_anomalies_tool": (
        "Valida la calidad de datos de julio 2025 para la estacion 108047"
    ),
}


FLOW_NOTES = {
    "search_stations": (
        "Usala antes de descargar o analizar cuando el codigo de estacion no este "
        "confirmado."
    ),
    "get_station_info": (
        "Usala despues de buscar cuando necesites confirmar metadatos de una estacion."
    ),
    "check_data_availability": "Usala antes de descargar o comparar periodos historicos.",
    "scrape_station_data": (
        "Descarga datos; no resume ni valida. Luego usa preview, resumen, "
        "comparacion o validacion."
    ),
    "list_downloaded_files": (
        "Usala para confirmar si ya existen CSV locales antes de analizar."
    ),
    "read_csv_preview": (
        "Usala para inspeccionar columnas y una muestra de filas antes de calcular "
        "metricas."
    ),
    "extract_month_from_csv": "Usala cuando un mes esta dentro de un CSV anual o multianual.",
    "summarize_station_data_tool": (
        "Usala para un solo periodo. Para dos o mas periodos usa comparacion."
    ),
    "compare_periods_tool": "Usala solo para dos o mas periodos de una misma estacion.",
    "detect_anomalies_tool": "Usala para auditoria de calidad; no reemplaza resumen ni comparacion.",
    "recommend_station_for_point_tool": (
        "Usala cuando la seleccion de estacion debe justificarse por criterios multiples."
    ),
}


ToolFunction = ast.FunctionDef | ast.AsyncFunctionDef


def _public_tool_functions(tree: ast.Module) -> list[ToolFunction]:
    tools: list[ToolFunction] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("register_") or node.name.startswith("_"):
            continue
        if ast.get_docstring(node):
            tools.append(node)
    return tools


def _param_names(fn: ToolFunction) -> list[str]:
    names = [arg.arg for arg in fn.args.args]
    names.extend(arg.arg for arg in fn.args.kwonlyargs)
    return [name for name in names if name not in {"self", "mcp"}]


def _first_paragraph(docstring: str) -> str:
    paragraphs = [part.strip().replace("\n", " ") for part in docstring.split("\n\n")]
    return paragraphs[0] if paragraphs else ""


def collect_tools() -> list[ToolDoc]:
    docs: list[ToolDoc] = []
    for path in sorted(TOOLS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in _public_tool_functions(tree):
            docstring = ast.get_docstring(fn) or ""
            docs.append(
                ToolDoc(
                    name=fn.name,
                    module=path.stem,
                    description=_first_paragraph(docstring),
                    parameters=_param_names(fn),
                    prompt=PROMPTS.get(fn.name, f"Usa {fn.name} para mi caso"),
                    flow_note=FLOW_NOTES.get(
                        fn.name,
                        "Revisa la guia de usuario relacionada antes de usarla en "
                        "flujos largos.",
                    ),
                )
            )
    return sorted(docs, key=lambda item: (item.module, item.name))


def render(tools: list[ToolDoc]) -> str:
    lines = [
        "# Referencia de tools MCP",
        "",
        "Este archivo se genera desde los docstrings en `src/garua/mcp_tools/*.py`.",
        "",
        "Para actualizarlo:",
        "",
        "```bash",
        "python scripts/generate_tools_reference.py",
        "```",
        "",
        "La referencia es tecnica. Para aprender por flujo de trabajo, usa las "
        "guias en `docs/guides/`.",
        "",
        f"## Tools disponibles ({len(tools)})",
        "",
    ]

    current_module = ""
    for tool in tools:
        if tool.module != current_module:
            current_module = tool.module
            lines.extend([f"### {current_module}", ""])
        lines.extend(
            [
                f"#### `{tool.name}`",
                "",
                tool.description,
                "",
                "- **Parametros:** "
                f"{', '.join(f'`{p}`' for p in tool.parameters) or 'sin parametros'}",
                f"- **Ejemplo de prompt:** `{tool.prompt}`",
                f"- **Nota de flujo:** {tool.flow_note}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(render(collect_tools()), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
