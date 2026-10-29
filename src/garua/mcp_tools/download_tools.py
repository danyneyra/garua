"""Tools para descarga de datos desde SENAMHI."""

from fastmcp.tools import ToolResult
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

from typing import Annotated

from pydantic import Field

from garua.models.scraping import ScrapingPeriod, ScrapingServiceErrorResponse
from garua.schemas.scraping import (
    build_scraping_error_response,
    build_scraping_success_response,
)
from garua.services.scraping import scrape_station_data_service


def register_download_tools(mcp):
    """Registra las tools de descarga en el servidor MCP."""

    @mcp.tool()
    async def scrape_station_data(
        station_code: Annotated[
            str,
            Field(
                description=(
                    "Código interno de la estación (ej: '100090'). "
                    "Usa search_stations primero si no tienes el código."
                )
            ),
        ],
        mode: Annotated[
            str | None,
            Field(
                description=(
                    "Para varios meses específicos usa periods en una sola llamada. "
                    "En otros casos: "
                    "'month' = un mes específico (requiere year + month), "
                    "'year' = un año completo (requiere year), "
                    "'period' = rango de años (requiere start_year + end_year). "
                    "Opcional si se usa el parámetro 'periods'."
                )
            ),
        ] = None,
        year: Annotated[
            int | None,
            Field(
                description="Año (ej: 2025) para mode='month' o 'year'. Para varios meses específicos usa periods."
            ),
        ] = None,
        month: Annotated[
            int | None,
            Field(
                description="Un único mes (1-12) para mode='month'. Para varios meses usa periods en una sola llamada."
            ),
        ] = None,
        start_year: Annotated[
            int | None,
            Field(description="Año de inicio del rango. Requerido para mode='period'."),
        ] = None,
        end_year: Annotated[
            int | None,
            Field(description="Año de fin del rango. Requerido para mode='period'."),
        ] = None,
        individual: Annotated[
            bool,
            Field(
                description="Para mode='year' o 'period': True genera un CSV por mes; False consolida. Con periods o mode='month' siempre se genera un CSV por mes."
            ),
        ] = False,
        periods: Annotated[
            list[ScrapingPeriod] | None,
            Field(
                description=(
                    "Opción preferida para varios meses de la misma estación, consecutivos "
                    "o separados, incluso entre años. Una llamada y como máximo una sesión "
                    "de navegador; genera un CSV por mes. De 1 a 12 periodos con year y month. "
                    "Ejemplo enero-marzo: [{'year': 2025, 'month': 1}, "
                    "{'year': 2025, 'month': 2}, {'year': 2025, 'month': 3}]. "
                    "Omite mode/year/month/start_year/end_year cuando uses periods."
                )
            ),
        ] = None,
        force_download: Annotated[
            bool,
            Field(
                description=(
                    "Si True, fuerza la descarga incluso si ya existe un archivo para ese periodo. "
                    "Útil para obtener datos actualizados o corregidos. Por defecto: False."
                )
            ),
        ] = False,
        ctx: Context = CurrentContext(),
    ) -> ToolResult:
        """
        Descarga datos históricos del SENAMHI para una estación y los guarda como CSV.

        Para descargar varios meses específicos de una misma estación, usa UNA
        llamada con periods (máximo 12), no una llamada mode="month" por mes.
        Aplica a meses consecutivos, separados y de distintos años. Para más de
        12 meses específicos divide en lotes de hasta 12.

        Ejemplo enero a marzo de 2025:
        {"station_code": "106145", "periods": [
            {"year": 2025, "month": 1},
            {"year": 2025, "month": 2},
            {"year": 2025, "month": 3}
        ]}

        Selección de argumentos:
        - Varios meses específicos: periods; omite mode y los argumentos de fecha
          independientes. Se usa como máximo una sesión de navegador por llamada
          y se genera un CSV por mes.
        - Un solo mes: mode="month", year y month.
        - Un año completo: mode="year" y year.
        - Años completos: mode="period", start_year y end_year.
        - individual solo controla la consolidación en mode="year" o "period".

        Úsala cuando el usuario pida descargar, traer o actualizar datos. Puede
        abrir un navegador y tardar varios minutos. Si falta el código, resuélvelo
        con search_stations. Para meses mediante periods o mode="month", intenta
        extraer datos de consolidados locales antes de descargar. Si pide actualizar
        o descargar de nuevo, usa force_download=True para omitir esa extracción.

        El resultado incluye success, message, station_name, station_code, mode,
        period, files (metadatos, rutas, URI local y resource_uri MCP cuando está
        disponible), stats (successful, failed, total)
        y extracted_from; en errores incluye error_code y details. Conserva los
        fallos parciales. Las rutas y enlaces ya vienen en el resultado: no llames
        list_downloaded_files inmediatamente para volver a obtenerlos. Su apertura
        depende del cliente. Para leer un archivo sin acceso al disco, usa su
        resource_uri mediante resources/read. Los CSV pequeños también pueden
        venir como recursos embebidos; eso no garantiza un adjunto descargable.

        Entrega al usuario: si el cliente dispone de herramientas Filesystem con
        acceso a files[].path, puede leer un CSV con read_text_file o varios con
        read_multiple_files. Usa las herramientas realmente disponibles y sus
        directorios autorizados. Si dispone además de un entorno para guardar
        archivos y un mecanismo de adjuntos (por ejemplo present_files), puede
        guardar allí el contenido completo y presentarlo, conservando el original.
        Leer mediante Filesystem no copia automáticamente al entorno del cliente.
        Si estas capacidades no existen, devuelve las rutas y URI disponibles;
        para obtener el contenido también puede usar resource_uri o los recursos
        embebidos. No afirmes que se adjuntó o copió un archivo sin haberlo hecho.

        Para resumir, comparar o detectar anomalías usa las tools específicas;
        esta tool descarga o extrae archivos. Si faltan varios meses antes de un
        análisis, descárgalos juntos con periods y luego ejecuta el análisis.
        """

        # Count real status events, without implying a duration percentage.
        event_count = 0

        async def report(message: str) -> None:
            nonlocal event_count
            event_count += 1
            await ctx.report_progress(progress=event_count, message=message)

        result = await scrape_station_data_service(
            station_code=station_code,
            mode=mode,
            year=year,
            month=month,
            start_year=start_year,
            end_year=end_year,
            individual=individual,
            periods=periods,
            force_download=force_download,
            on_progress=report,
        )

        if isinstance(result, ScrapingServiceErrorResponse):
            await report(f"Proceso fallido: {result.message}")
        else:
            await report(
                f"Proceso terminado para {result.station_name}: "
                f"{result.stats.successful} correctos y {result.stats.failed} fallidos "
                f"de {result.stats.total} periodos."
            )

        if not result.success or isinstance(result, ScrapingServiceErrorResponse):
            if isinstance(result, ScrapingServiceErrorResponse):
                error_code = result.error_code
                error_details = result.details
            else:
                error_code = "UNKNOWN_ERROR"
                error_details = None

            return build_scraping_error_response(
                message=result.message,
                error_code=error_code,
                station_code=result.station_code,
                station_name=result.station_name,
                details=error_details,
            )

        return build_scraping_success_response(
            message=result.message,
            station_name=result.station_name,
            station_code=result.station_code,
            mode=result.mode,
            period=result.period,
            stats=result.stats.model_dump(),
            files=result.files,
            extracted_from=result.extracted_from,
        )
