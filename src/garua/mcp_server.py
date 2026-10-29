"""
Garúa MCP Server — Servidor MCP local (stdio) para consultar estaciones
meteorológicas e hidrológicas del SENAMHI y descargar datos históricos.

Garúa: llovizna fina característica del clima peruano 🇵🇪

Configuración en VS Code (.vscode/mcp.json):
    {
      "servers": {
        "garua": {
          "type": "stdio",
          "command": "<ruta-absoluta>/.venv/Scripts/python.exe",
          "args": ["-m", "garua_mcp"]
        }
      }
    }

Organización modular:
    src/mcp_tools/
    ├── anomaly_tools.py        — Detección de anomalías climáticas
    ├── station_tools.py        — Búsqueda y filtrado de estaciones
    ├── stats_tools.py          — Estadísticas y resúmenes
    ├── file_tools.py           — Gestión de archivos CSV
    ├── download_tools.py       — Descarga desde SENAMHI
    ├── comparison_tools.py     — Comparación de periodos
    ├── recommendation_tools.py — Recomendaciones basadas en datos
    └── summary_tools.py        — Resumen de datos históricos
"""

import sys
from pathlib import Path

from .mcp_compat import ensure_mcp_compatibility

ensure_mcp_compatibility()

from fastmcp import FastMCP
from . import settings
from mcp.types import Icon
from .mcp_tools.anomaly_tools import register_anomaly_tools
from .mcp_tools.comparison_tools import register_comparison_tools
from .mcp_tools.download_tools import register_download_tools
from .mcp_tools.file_tools import register_file_tools
from .mcp_tools.recommendation_tools import register_recommendation_tools
from .mcp_tools.station_tools import register_station_tools
from .mcp_tools.stats_tools import register_stats_tools
from .mcp_tools.summary_tools import register_summary_tools
from .mcp_prompts import register_prompts
from .mcp_resources import register_resources
from .services.station import stations

# En Windows el codec por defecto (charmap/cp1252) no soporta emojis.
# Reconfiguramos stdout y stderr a UTF-8 antes de cualquier print.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore

PACKAGE_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PACKAGE_ROOT))


# ── Servidor ───────────────────────────────────────────────────────────────────
svg_icon = Icon(
    src="data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgdmlld0JveD0iMCAwIDk2IDk2IiB3aWR0aD0iOTYiIGhlaWdodD0iOTYiPgoJPHN0eWxlPgoJCS5zMCB7IGZpbGw6ICM2NDY5ZTMgfSAKCQkuczEgeyBmaWxsOiAjZmZmZmZmIH0gCgk8L3N0eWxlPgoJPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGFzcz0iczAiIGQ9Im03My42OCA1NS4xN2MtMi4yMSAyMi4wMS0xMi4yMyAzOC43OC0zNi4xIDI3LjQ5LTIzLjA2LTQuNTQtMTcuNTktMjguMTktMTAuMTQtNDEuNDYgOC42Mi0xNC43OSAyNS42My0yNS4xNiAzNS42NC0zMC41MiAxLjE3LTAuNTggMS45OC0xLjA0IDIuOC0xLjUxcTEuMDUtMC40NyAxLjM5IDAuMzVjMC40NyAwLjkzIDAuODIgMS44NiAxLjE3IDIuOTEgNC4zMSAxMiA2LjY0IDI4LjQyIDUuMjQgNDIuNzR6Ii8+Cgk8cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsYXNzPSJzMSIgZD0ibTUwLjI3IDc4LjM1Yy01LjE1IDAtOS4zMi0yLjIxLTkuMzItNC45NSAwLTIuNzQgNC4xNy00Ljk1IDkuMzItNC45NSA1LjE1IDAgOS4zMiAyLjIxIDkuMzIgNC45NSAwIDIuNzQtNC4xNyA0Ljk1LTkuMzIgNC45NXoiLz4KPC9zdmc+",
    mime_type="image/svg+xml",
)

mcp = FastMCP(
    name=settings.PROJECT_NAME,
    instructions=(
        "Eres Garua, un asistente especializado en estaciones meteorológicas e "
        "hidrológicas del SENAMHI (Perú). "
        "Regla principal: para responder usa las capacidades MCP de este servidor. "
        "Consulta Resources para catálogo, esquemas y contexto estable; usa las "
        "tools para búsquedas dinámicas, descargas, transformaciones y análisis. "
        "Si el cliente ofrece Prompts, úsalos para seguir los flujos de análisis "
        "predefinidos. "
        "No escribas código Python, scripts, cálculos manuales ni implementaciones "
        "propias para buscar estaciones, filtrar resultados, recomendar estaciones, "
        "consultar disponibilidad, listar archivos, leer CSV, descargar datos, "
        "resumir periodos, comparar periodos o detectar anomalías. "
        "No inventes datos ni supongas resultados: si falta información, obténla con "
        "las tools adecuadas y, solo si es necesario, pide al usuario el dato mínimo "
        "faltante. "
        "Al seleccionar una estación o antes de una descarga consulta su ficha y revisa "
        "catalog_status, availability_status, catalog_checked_at, availability_checked_at y note. "
        "catalog_status=absent significa que no figura en el listado consultado en esa fecha, "
        "no que haya una baja oficial; puede conservar datos históricos. "
        "periods_announced indica meses anunciados, no observaciones confirmadas ni continuidad "
        "hasta hoy. no_periods_announced no demuestra ausencia total de datos. "
        "periods_unknown significa que no se conoce el listado de meses anunciados en la ficha. "
        "Nunca lo presentes como datos sin verificar, poco confiables o sin datos: este campo "
        "no evalúa la autenticidad, exactitud ni calidad del contenido descargado de SENAMHI. "
        "Explica estas limitaciones cuando afecten la consulta; no ocultes estaciones ni "
        "bloquees una solicitud explícita por estos estados. "
        "Selecciona siempre el Resource, Prompt o tool más específico para la intención del usuario. "
        "Guía operativa: usa search_stations si el usuario menciona una estación por "
        "nombre o código; usa filter_stations_* o find_stations_near para explorar o "
        "filtrar estaciones; usa get_station_info para ver el detalle completo de una "
        "estación o garua://catalog/stations/{station_code} para consultar su ficha; "
        "usa check_data_availability para validar cobertura histórica; usa "
        "recommend_station_for_point_tool para recomendar estaciones; usa "
        "list_downloaded_files, read_csv_preview y extract_month_from_csv para "
        "trabajar con archivos locales; usa scrape_station_data solo cuando el usuario "
        "pida descargar, actualizar o traer datos; usa summarize_station_data_tool "
        "para resumir un único periodo; usa compare_periods_tool solo para comparar "
        "dos o más periodos; usa detect_anomalies_tool para calidad y anomalías. "
        "Si una tool ya devuelve la respuesta, no la rehagas por tu cuenta."
    ),
    icons=[svg_icon],
    version=settings.VERSION,
    website_url="https://www.garua.app/",
)


# ── Registrar Tools Modulares ──────────────────────────────────────────────────

# Registrar todas las tools
register_station_tools(mcp)
register_stats_tools(mcp)
register_file_tools(mcp)
register_download_tools(mcp)
register_recommendation_tools(mcp, stations)
register_comparison_tools(mcp)
register_anomaly_tools(mcp)
register_summary_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


# ── Entry point ────────────────────────────────────────────────────────────────


def main():
    settings.ensure_output_dirs()
    mcp.run()


if __name__ == "__main__":
    main()
