"""Tools MCP para resumen de datos de estaciones SENAMHI."""

from typing import Annotated, Literal

from pydantic import Field

from garua.schemas.summary import (
    build_summary_error_response,
    build_summary_success_response,
)
from garua.services.summary import summarize_station_data


def register_summary_tools(mcp):
    """Registra las tools de resumen en el servidor MCP."""

    @mcp.tool()
    def summarize_station_data_tool(
        station_code: Annotated[
            str,
            Field(
                description=(
                    "Código interno de la estación SENAMHI (ej: '107008', '100090'). "
                    "Obténlo primero con search_stations o get_station_info."
                )
            ),
        ],
        year: Annotated[
            int | None,
            Field(description="Año específico a resumir (ej: 2025)."),
        ] = None,
        month: Annotated[
            int | None,
            Field(description="Mes específico (1-12). Requiere year."),
        ] = None,
        start_year: Annotated[
            int | None,
            Field(description="Año inicial si se resume un rango de años."),
        ] = None,
        end_year: Annotated[
            int | None,
            Field(description="Año final si se resume un rango de años."),
        ] = None,
        metrics: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Métricas específicas a calcular. Si es None, usa las del esquema detectado.\n"
                    "Meteorológica convencional: temp_max_avg, temp_min_avg, humidity_avg, "
                    "precip_total, rainy_days, dry_days, missing_days, trace_days, max_daily_precip\n"
                    "Meteorológica automática: temp_avg, precip_total, rainy_hours, rainy_days, "
                    "dry_hours, wind_speed_avg, wind_speed_max\n"
                    "Hidrológica: river_level_avg/max/min, precip_total, rainy_hours"
                )
            ),
        ] = None,
        include_quality: Annotated[
            bool,
            Field(
                description=(
                    "Si True, incluye diagnóstico resumido de calidad reutilizando "
                    "validate_dataset (duplicados, S/D, T, fechas faltantes)."
                )
            ),
        ] = True,
        auto_download: Annotated[
            bool,
            Field(
                description=(
                    "Si True, intenta descargar datos faltantes. "
                    "Actualmente no implementado — los datos deben existir localmente."
                )
            ),
        ] = False,
        trace_policy: Annotated[
            Literal["as_0_05", "as_0", "as_null"],
            Field(
                description=(
                    "Política para trazas T en precipitación: as_0_05 (default), as_0 o as_null."
                )
            ),
        ] = "as_0_05",
    ) -> dict:
        """
        Resume datos SENAMHI de una estación para un mes, año o periodo individual.

        Usa esta tool cuando el usuario quiera saber cómo fue un periodo específico:
        precipitación acumulada, días con lluvia, temperaturas, humedad, viento, nivel
        del río u otras métricas compatibles con el tipo de estación.

        No uses esta tool para comparar dos o más periodos; para eso usa
        compare_periods_tool. No la uses como diagnóstico principal de calidad; para eso
        usa detect_anomalies_tool. Esta tool puede incluir una vista general de calidad
        si include_quality=True.

        Esta tool responde preguntas como:
        - ¿Cómo fue diciembre 2025 en esta estación?
        - ¿Cuánta precipitación acumuló en un año?
        - ¿Cuál fue la temperatura promedio del mes?
        - ¿Cuál fue el nivel máximo del río en el periodo?
        - Dame un resumen con métricas y calidad general.

        Características:
        - Detección automática de esquema: meteorológica/hidrológica, convencional/automática
        - Métricas técnicas según el tipo de estación
        - Manejo de S/D como dato faltante, no como 0.0
        - Manejo de T como traza de precipitación según trace_policy
        - Resumen narrativo breve en español
        - Diagnóstico general de calidad opcional
        - Warnings para S/D, T, duplicados, métricas inválidas o fechas/horas faltantes

        Ejemplos:
        {
        "station_code": "107008",
        "year": 2025,
        "month": 12
        }

        {
        "station_code": "107008",
        "year": 2025
        }

        {
        "station_code": "107008",
        "start_year": 2022,
        "end_year": 2025
        }

        Respuesta incluye:
        - station: información de la estación
        - schema: esquema detectado y frecuencia
        - period: periodo resumido con etiqueta legible
        - rows: cantidad de registros usados
        - metrics: valores calculados
        - quality: resumen general de calidad, si include_quality=True
        - warnings: advertencias detectadas
        - summary: resumen interpretativo en español

        USA ESTA TOOL cuando el usuario:
        - Pida un resumen de una estación en un periodo individual
        - Quiera saber cómo fue un mes, año o rango específico
        - Necesite precipitación acumulada, días con lluvia, temperaturas, humedad, viento o nivel de río
        - Quiera métricas del periodo con una vista general de calidad

        NUNCA calcules métricas manualmente: esta tool ya implementa los cálculos.
        NUNCA uses esta tool para comparar periodos: usa compare_periods_tool.
        NUNCA uses esta tool para auditoría detallada de calidad: usa detect_anomalies_tool.
        """
        try:
            result = summarize_station_data(
                station_code=station_code,
                year=year,
                month=month,
                start_year=start_year,
                end_year=end_year,
                metrics=metrics,
                include_quality=include_quality,
                auto_download=auto_download,
                trace_policy=trace_policy,
            )
            message = f"Se resumió la estación {result.station.name} ({result.station.code}) para el periodo solicitado. {len(result.warnings)} warning(s) detectado(s). {'Incluye diagnóstico de calidad.' if include_quality else 'No se incluyó diagnóstico de calidad.'} {result.summary if result.summary else ''}"
            return build_summary_success_response(message, result)
        except Exception as e:
            return build_summary_error_response(str(e))
