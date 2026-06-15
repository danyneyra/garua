"""Tools MCP para detección de anomalías de calidad de datos."""

from typing import Annotated, Literal

from pydantic import Field

from garua.services.anomaly import detect_anomalies
from garua.schemas.anomaly import (
    build_anomaly_sucess_response,
    build_anomaly_error_response,
)


def register_anomaly_tools(mcp):
    """Registra las tools de anomalías en el servidor MCP."""

    @mcp.tool()
    def detect_anomalies_tool(
        station_code: Annotated[
            str,
            Field(
                description=(
                    "Código interno de la estación SENAMHI (ej: '107008', '100090')."
                )
            ),
        ],
        year: Annotated[
            int | None,
            Field(description="Año específico a analizar (ej: 2025)."),
        ] = None,
        month: Annotated[
            int | None,
            Field(description="Mes específico (1-12). Requiere year."),
        ] = None,
        start_year: Annotated[
            int | None,
            Field(description="Año inicial del periodo a analizar."),
        ] = None,
        end_year: Annotated[
            int | None,
            Field(description="Año final del periodo a analizar."),
        ] = None,
        checks: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Lista opcional de checks a ejecutar. Si es None, usa checks por "
                    "defecto según el esquema detectado."
                )
            ),
        ] = None,
        severity: Annotated[
            Literal["all", "info", "warning", "critical"],
            Field(
                description=(
                    "Filtro de severidad: all, info, warning o critical. "
                    "Por defecto all."
                )
            ),
        ] = "all",
        auto_download: Annotated[
            bool,
            Field(
                description=(
                    "Si True, intenta resolver faltantes automáticamente. "
                    "Actualmente no implementado."
                )
            ),
        ] = False,
        trace_policy: Annotated[
            Literal["as_0_05", "as_0", "as_null"],
            Field(
                description=(
                    "Política para T en precipitación: as_0_05, as_0 o as_null. "
                    "Por defecto as_0_05."
                )
            ),
        ] = "as_0_05",
    ) -> dict:
        """
        Detecta anomalías y problemas de calidad en datos SENAMHI descargados para una
        estación y periodo.

        Usa esta tool cuando el usuario quiera validar datos, revisar confiabilidad,
        encontrar duplicados, fechas/horas faltantes, valores S/D, trazas T, valores
        no numéricos o valores fuera de rango.

        No uses esta tool para resumir el comportamiento climático/hidrológico de un
        periodo; para eso usa summarize_station_data_tool. No la uses para comparar
        dos o más periodos; para eso usa compare_periods_tool.

        Soporta estos esquemas:
        - meteorological_conventional
        - meteorological_automatic
        - hydrological_conventional
        - hydrological_automatic

        Incluye validaciones de:
        - duplicados
        - fechas/horas faltantes
        - valores faltantes (S/D = Sin Datos)
        - trazas (T = precipitación menor a 0.1 mm/día)
        - valores no numéricos
        - rangos inválidos
        - precipitaciones negativas
        - consistencia temp. máxima vs mínima en estaciones meteorológicas convencionales

        Nota: S/D se trata como dato faltante, no como 0.0. T se trata como traza de
        precipitación según la política trace_policy.
        """
        try:
            result = detect_anomalies(
                station_code=station_code,
                year=year,
                month=month,
                start_year=start_year,
                end_year=end_year,
                checks=checks,
                severity=severity,
                auto_download=auto_download,
                trace_policy=trace_policy,
            )
            message = f"La operación de detección de anomalías para la estación {result.station.name} ({result.station.code}) se completó. Se encontraron {result.summary.issues_found} issues en {result.summary.rows_analyzed} filas analizadas."
            return build_anomaly_sucess_response(message, result)
        except Exception as e:
            return build_anomaly_error_response(str(e))
