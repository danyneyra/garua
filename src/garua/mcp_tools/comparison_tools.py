"""Tools MCP para comparación de periodos."""

from typing import Annotated

from pydantic import Field

from garua.services.comparison import compare_periods
from garua.schemas.comparison import (
    build_comparison_error_response,
    build_comparison_success_response,
)


def register_comparison_tools(mcp):
    """Registra las tools de comparación en el servidor MCP."""

    @mcp.tool()
    def compare_periods_tool(
        station_code: Annotated[
            str,
            Field(
                description=(
                    "Código interno de la estación SENAMHI (ej: '107008', '100090'). "
                    "Obténlo primero con search_stations."
                )
            ),
        ],
        periods: Annotated[
            list[dict],
            Field(
                description=(
                    "Lista de periodos a comparar. Cada periodo debe tener:\n"
                    "- label: Etiqueta descriptiva (ej: 'Diciembre 2024')\n"
                    "- year: Año (ej: 2024)\n"
                    "- month: Mes opcional (1-12)\n"
                    "Ejemplo: [{'label': 'Dic 2024', 'year': 2024, 'month': 12}, "
                    "{'label': 'Dic 2025', 'year': 2025, 'month': 12}]"
                )
            ),
        ],
        metrics: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Métricas específicas a calcular. Si es None, usa todas las disponibles.\n"
                    "Métricas meteorológicas convencionales: temp_max_avg, temp_min_avg, "
                    "humidity_avg, precip_total, rainy_days, max_daily_precip\n"
                    "Métricas meteorológicas automáticas: temp_avg, temp_max, temp_min, "
                    "humidity_avg, precip_total, rainy_hours, rainy_days, wind_speed_avg, "
                    "wind_speed_max, wind_direction_avg\n"
                    "Métricas hidrológicas: river_level_avg, river_level_max, river_level_min, "
                    "precip_total, rainy_hours, rainy_days"
                )
            ),
        ] = None,
        aggregation: Annotated[
            str,
            Field(
                description="Tipo de agregación. Usar 'auto' (por ahora único valor soportado)."
            ),
        ] = "auto",
        deduplicate: Annotated[
            bool,
            Field(
                description=(
                    "Si True, elimina registros duplicados basándose en fecha/hora antes de calcular. "
                    "Recomendado: True."
                )
            ),
        ] = True,
        auto_download: Annotated[
            bool,
            Field(
                description=(
                    "Si True, intenta descargar datos faltantes automáticamente. "
                    "Actualmente no implementado - los datos deben existir localmente."
                )
            ),
        ] = False,
    ) -> dict:
        """
        Compara dos o más periodos de datos de una estación SENAMHI con esquema
        autodetectado.

        Usa esta tool cuando el usuario quiera comparar meses, años o rangos; calcular
        diferencias entre periodos; o saber qué periodo tuvo mayor precipitación,
        temperatura, humedad, viento o nivel de río.

        No uses esta tool para resumir un único periodo; para eso usa
        summarize_station_data_tool. No la uses como diagnóstico principal de calidad;
        para eso usa detect_anomalies_tool. Esta tool puede devolver warnings de calidad,
        pero su objetivo principal es comparar periodos.

        Esta tool es consciente del tipo de estación y detecta automáticamente si es:
        - Meteorológica convencional (datos diarios)
        - Meteorológica automática (datos horarios)
        - Hidrológica convencional (observaciones diarias)
        - Hidrológica automática (datos horarios)

        Calcula métricas apropiadas según el esquema:
        - Meteorológicas: temperatura, humedad, precipitación y viento cuando aplique
        - Hidrológicas: nivel del río y precipitación cuando aplique

        Características:
        - Detección automática de esquema por headers del CSV
        - Deduplicación de registros duplicados
        - Manejo de S/D como dato faltante, no como 0.0
        - Manejo de T como traza de precipitación según trace_policy
        - Cálculo de diferencias entre periodos
        - Cálculo de cambios porcentuales cuando aplica
        - Warnings para duplicados, métricas inválidas o datos faltantes
        - Resumen interpretativo en español

        Flujo de uso típico:
        1. Descargar datos con scrape_station_data si aún no existen localmente
        2. Llamar a compare_periods_tool con los periodos a comparar
        3. Revisar metrics, differences, warnings y summary

        Casos de uso:
        - Comparar meses del mismo año o de años diferentes
        - Comparar años completos
        - Analizar variabilidad entre periodos
        - Identificar qué periodo fue más lluvioso, seco, cálido o húmedo
        - Comparar niveles de río entre periodos
        - Apoyar análisis técnico con métricas estructuradas

        Ejemplo básico:
        {
        "station_code": "107008",
        "periods": [
            {"label": "Diciembre 2024", "year": 2024, "month": 12},
            {"label": "Diciembre 2025", "year": 2025, "month": 12}
        ]
        }

        Ejemplo con métricas específicas:
        {
        "station_code": "107008",
        "periods": [
            {"label": "2024", "year": 2024},
            {"label": "2025", "year": 2025}
        ],
        "metrics": ["temp_max_avg", "precip_total", "rainy_days"]
        }

        Respuesta incluye:
        - station: información de la estación
        - schema: esquema detectado y métricas disponibles
        - periods: métricas calculadas por periodo
        - differences: diferencias y cambios porcentuales entre periodos
        - warnings: advertencias detectadas durante el cálculo
        - summary: resumen interpretativo en español

        USA ESTA TOOL cuando el usuario:
        - Pida comparar periodos, meses o años
        - Pregunte por diferencias o cambios entre periodos
        - Quiera saber qué periodo fue más lluvioso, seco, cálido o húmedo
        - Necesite comparar métricas históricas de una misma estación

        NUNCA calcules métricas manualmente: esta tool ya implementa los cálculos.
        NUNCA asumas el tipo de estación: la tool lo detecta automáticamente.
        """

        try:
            result = compare_periods(
                station_code=station_code,
                periods=periods,
                metrics=metrics,
                aggregation=aggregation,
                deduplicate=deduplicate,
                auto_download=auto_download,
            )
            message = f"Comparación de {len(periods)} periodos para estación {result.station.name} ({result.station.code}) completada. {len(result.warnings)} warnings detectados. Revisa 'warnings' para detalles. Resumen: {result.summary if result.summary else 'No disponible'}"
            return build_comparison_success_response(
                message=message, structured_data=result
            )
        except Exception as e:
            return build_comparison_error_response(str(e))
