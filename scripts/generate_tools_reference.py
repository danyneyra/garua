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
class ParameterDoc:
    name: str
    type_hint: str
    required: bool
    default: str
    description: str


@dataclass
class ToolDoc:
    name: str
    module: str
    description: str
    parameters: list[ParameterDoc]
    prompt: str
    flow_note: str


PROMPTS = {
    "search_stations": "Busca estaciones llamadas Cabana",
    "get_station_info": "Dame la ficha de la estación 108047",
    "get_all_stations": "Lista las primeras estaciones disponibles",
    "export_all_stations_csv": "Exporta el catálogo completo de estaciones a CSV",
    "check_data_availability": "¿Desde cuándo hay datos para la estación 108047?",
    "filter_stations_by_location": "Busca estaciones en Arequipa, provincia Caylloma",
    "filter_stations_by_altitude": "Busca estaciones sobre 3000 msnm",
    "filter_stations_advanced": (
        "Busca estaciones meteorológicas activas en Puno sobre 3500 msnm"
    ),
    "find_stations_near": "Busca estaciones cerca de lat -7.61, lon -77.82",
    "recommend_station_for_point_tool": (
        "Recomienda una estación para lat -7.61, lon -77.82 con altitud 3000 msnm"
    ),
    "stations_count": "¿Cuántas estaciones tienes disponibles?",
    "stations_summary": "Resume el inventario de estaciones por tipo y estado",
    "get_departments_summary": "¿Qué departamentos tienen más estaciones?",
    "get_location_hierarchy": "Muestra la jerarquía de ubicaciones con estaciones",
    "list_downloaded_files": (
        "Lista archivos descargados para la estación 108047 en 2025"
    ),
    "read_csv_preview": (
        "Muestra una vista previa del CSV de julio 2025 para la estación 108047"
    ),
    "extract_month_from_csv": (
        "Extrae julio 2025 desde el CSV consolidado de la estación 108047"
    ),
    "scrape_station_data": "Descarga julio 2025 de la estación 108047",
    "summarize_station_data_tool": "Resume julio 2025 para la estación 108047",
    "compare_periods_tool": "Compara marzo 2025 vs marzo 2026 para la estación 108047",
    "detect_anomalies_tool": (
        "Valida la calidad de datos de julio 2025 para la estación 108047"
    ),
}


FLOW_NOTES = {
    "search_stations": (
        "Úsala antes de descargar o analizar cuando el código de estación no esté "
        "confirmado."
    ),
    "get_station_info": (
        "Úsala después de buscar cuando necesites confirmar metadatos de una estación."
    ),
    "check_data_availability": "Úsala antes de descargar o comparar periodos históricos.",
    "scrape_station_data": (
        "Descarga datos; no resume ni valida. Luego usa preview, resumen, "
        "comparación o validación."
    ),
    "list_downloaded_files": (
        "Úsala para confirmar si ya existen CSV locales antes de analizar."
    ),
    "read_csv_preview": (
        "Úsala para inspeccionar columnas y una muestra de filas antes de calcular "
        "métricas."
    ),
    "extract_month_from_csv": "Úsala cuando un mes está dentro de un CSV anual o multianual.",
    "summarize_station_data_tool": (
        "Úsala para un solo periodo. Para dos o más periodos usa comparación."
    ),
    "compare_periods_tool": "Úsala solo para dos o más periodos de una misma estación.",
    "detect_anomalies_tool": "Úsala para auditoría de calidad; no reemplaza resumen ni comparación.",
    "recommend_station_for_point_tool": (
        "Úsala cuando la selección de estación debe justificarse por criterios múltiples."
    ),
}

MODULE_LABELS = {
    "anomaly_tools": "Calidad de datos",
    "comparison_tools": "Comparación",
    "download_tools": "Descarga",
    "file_tools": "Archivos CSV",
    "recommendation_tools": "Recomendación",
    "station_tools": "Estaciones",
    "stats_tools": "Inventario",
    "summary_tools": "Resumen",
}

WORKFLOW_ROWS = [
    ("Buscar estaciones", "`search_stations`, `filter_stations_*`, `find_stations_near`"),
    ("Confirmar metadatos", "`get_station_info`, `check_data_availability`"),
    ("Descargar datos", "`scrape_station_data`"),
    ("Revisar archivos locales", "`list_downloaded_files`, `read_csv_preview`, `extract_month_from_csv`"),
    ("Analizar datos", "`summarize_station_data_tool`, `compare_periods_tool`, `detect_anomalies_tool`"),
    ("Explorar inventario", "`stations_count`, `stations_summary`, `get_departments_summary`, `get_location_hierarchy`"),
]


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


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _literal_string(node.left)
        right = _literal_string(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _field_description(annotation: ast.AST | None) -> str:
    if annotation is None:
        return ""
    for node in ast.walk(annotation):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "Field":
            continue
        for keyword in node.keywords:
            if keyword.arg == "description":
                return " ".join((_literal_string(keyword.value) or "").split())
    return ""


def _type_hint(annotation: ast.AST | None) -> str:
    if annotation is None:
        return ""
    try:
        text = ast.unparse(annotation)
    except Exception:  # pragma: no cover - defensive for old AST shapes
        return ""
    if text.startswith("Annotated[") and text.endswith("]"):
        inner = text[len("Annotated[") : -1]
        depth = 0
        for index, char in enumerate(inner):
            if char in "[(":
                depth += 1
            elif char in "])":
                depth -= 1
            elif char == "," and depth == 0:
                return inner[:index].strip()
    return text


def _default_value(node: ast.AST | None) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "None"
        return repr(node.value)
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensive for old AST shapes
        return "..."


def _parameters(fn: ToolFunction) -> list[ParameterDoc]:
    positional = list(fn.args.args)
    positional_defaults = [None] * (len(positional) - len(fn.args.defaults))
    positional_defaults.extend(fn.args.defaults)

    params: list[ParameterDoc] = []
    for arg, default in [*zip(positional, positional_defaults), *zip(fn.args.kwonlyargs, fn.args.kw_defaults)]:
        if arg.arg in {"self", "mcp"}:
            continue
        params.append(
            ParameterDoc(
                name=arg.arg,
                type_hint=_type_hint(arg.annotation),
                required=default is None,
                default=_default_value(default) or "—",
                description=_field_description(arg.annotation),
            )
        )
    return params


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
                    parameters=_parameters(fn),
                    prompt=PROMPTS.get(fn.name, f"Usa {fn.name} para mi caso"),
                    flow_note=FLOW_NOTES.get(
                        fn.name,
                        "Revisa la guía de usuario relacionada antes de usarla en "
                        "flujos largos.",
                    ),
                )
            )
    return sorted(docs, key=lambda item: (item.module, item.name))


def _md_escape(text: str) -> str:
    return (
        text.replace("|", "\\|")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
        .replace("\n", "<br>")
    )


def _html_code(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("[", "&#91;")
        .replace("]", "&#93;")
        .replace("|", "&#124;")
    )


def _param_list(parameters: list[ParameterDoc]) -> str:
    return ", ".join(f"`{param.name}`" for param in parameters) or "sin parámetros"


def _params_table(parameters: list[ParameterDoc]) -> list[str]:
    if not parameters:
        return ["Sin parámetros."]

    lines = [
        "| Parámetro | Tipo | Requerido | Default | Descripción |",
        "| --- | --- | --- | --- | --- |",
    ]
    for param in parameters:
        required = "Sí" if param.required else "No"
        description = param.description or "—"
        lines.append(
            "| "
            f"`{param.name}` | "
            f"<code>{_html_code(param.type_hint)}</code> | "
            f"{required} | "
            f"<code>{_html_code(param.default)}</code> | "
            f"{_md_escape(description)} |"
        )
    return lines


def render(tools: list[ToolDoc]) -> str:
    lines = [
        "---",
        "icon: lucide/hammer",
        "tags:",
        "  - Tools MCP",
        "  - Referencia",
        "---",
        "",
        "# Referencia de tools MCP",
        "",
        "Esta referencia se genera desde los docstrings y las firmas de "
        "`src/garua/mcp_tools/*.py`.",
        "",
        "Para actualizarla:",
        "",
        "```bash",
        "python scripts/generate_tools_reference.py",
        "```",
        "",
        "Si buscas una guía por tarea, empieza por las páginas de `docs/guides/`. "
        "Esta página sirve como inventario técnico de las tools disponibles para MCP.",
        "",
        f"## Vista general ({len(tools)} tools)",
        "",
        "| Flujo | Tools relacionadas |",
        "| --- | --- |",
    ]

    for label, related_tools in WORKFLOW_ROWS:
        lines.append(f"| {label} | {related_tools} |")

    lines.extend(
        [
            "",
            "## Índice de tools",
            "",
            "| Grupo | Tool | Parámetros |",
            "| --- | --- | --- |",
        ]
    )

    for tool in tools:
        label = MODULE_LABELS.get(tool.module, tool.module)
        lines.append(
            f"| {label} | [`{tool.name}`](#{tool.name}) | {_param_list(tool.parameters)} |"
        )

    lines.extend(
        [
            "",
            "## Detalle por grupo",
            "",
        ]
    )

    current_module = ""
    for tool in tools:
        if tool.module != current_module:
            current_module = tool.module
            label = MODULE_LABELS.get(current_module, current_module)
            lines.extend([f"### {label}", ""])

        lines.extend(
            [
                f'??? abstract "`{tool.name}`"',
                "",
                f"    <a id=\"{tool.name}\"></a>",
                "",
                f"    {tool.description}",
                "",
                "    **Prompt de ejemplo**",
                "",
                "    ```text",
                f"    {tool.prompt}",
                "    ```",
                "",
                f"    **Cuándo usarla.** {tool.flow_note}",
                "",
                "    **Parámetros**",
                "",
            ]
        )

        for param_line in _params_table(tool.parameters):
            lines.append(f"    {param_line}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(render(collect_tools()), encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
