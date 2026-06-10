"""Tools para descarga de datos desde SENAMHI."""

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
                    "Modo de descarga: "
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
                description="Año (ej: 2025). Requerido para mode='month' o mode='year'."
            ),
        ] = None,
        month: Annotated[
            int | None,
            Field(description="Mes como número (1-12). Requerido para mode='month'."),
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
                description="True = genera un CSV por mes. False (por defecto) = CSV consolidado."
            ),
        ] = False,
        periods: Annotated[
            list[ScrapingPeriod] | None,
            Field(
                description=(
                    "Lista de periodos específicos a descargar en una sola sesión de navegador "
                    "(MÁS EFICIENTE para múltiples meses). Cada periodo debe tener 'year' y 'month'. "
                    "Máximo 12 periodos. "
                    "Ejemplo: [{'year': 2025, 'month': 3}, {'year': 2026, 'month': 3}]. "
                    "Si se provee, ignora mode/year/month/start_year/end_year. "
                    "BENEFICIO: Abre el navegador UNA SOLA VEZ en lugar de N veces."
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
    ) -> dict:
        """
        Descarga datos históricos del SENAMHI para una estación y los guarda como CSV.

        Usa esta tool solo cuando el usuario pida explícitamente descargar, obtener,
        bajar, traer o actualizar datos SENAMHI. Esta tool no resume, compara ni valida
        los datos; solo gestiona la descarga o extracción de archivos CSV.

        NOTA: Si se descargan archivos siempre intenta incluir enlaces directos a los archivos usando file:// o resource_link para que el usuario pueda hacer clic y abrir el archivo directamente desde la respuesta del MCP.

        IMPORTANTE PARA MCP CLIENTS:
        Si esta tool retorna success=true, NO llames list_downloaded_files inmediatamente.
        Esta respuesta ya incluye las rutas generadas en `files` y en `message`.
        Usa list_downloaded_files solo cuando el usuario pregunte explícitamente qué archivos existen localmente.

        COMPORTAMIENTO INTELIGENTE (mode='month', force_download=False):
        1. Primero busca archivos consolidados existentes, por ejemplo Estacion-2017-2020.csv
        2. Si encuentra el mes solicitado, lo extrae y retorna rapidamente
        3. Si no encuentra el mes localmente, descarga desde SENAMHI

        FORZAR DESCARGA (force_download=True):
        - Ignora archivos locales y consolidados existentes
        - Vuelve a consultar SENAMHI aunque el periodo ya exista localmente
        - Usalo cuando el usuario pida actualizar, refrescar, descargar de nuevo o volver a bajar datos
        - Recomendado para el mes actual, porque una descarga hecha a mitad de mes puede estar incompleta
        - Util para regenerar archivos creados con versiones antiguas de Garua

        MODO EFICIENTE (parametro periods):
        - Descarga multiples meses en una sola sesion de navegador
        - Ideal antes de comparar periodos con compare_periods_tool
        - Maximo 12 periodos por llamada
        - Ejemplo: periods=[{"year": 2025, "month": 3}, {"year": 2026, "month": 3}]

        Encadenamiento recomendado:
        - Si el usuario pide "compara marzo 2025 vs marzo 2026" y los datos no existen,
        primero usa esta tool con periods y luego compare_periods_tool.
        - Si el usuario pide "actualiza mayo 2026 y resumelo", usa esta tool con
        force_download=True y luego summarize_station_data_tool.

        Modos soportados:
        - mode="month": descarga o extrae un mes especifico
        - mode="year": descarga un ano completo
        - mode="period": descarga un rango de anos
        - periods=[...]: descarga multiples meses especificos eficientemente

        Advertencia:
        - Puede lanzar un navegador.
        - Puede tardar varios minutos si necesita descargar desde SENAMHI.
        - No la uses automaticamente si el usuario solo pide analizar datos ya disponibles.
        - Para resumen usa summarize_station_data_tool.
        - Para comparacion usa compare_periods_tool.
        - Para calidad/anomalias usa detect_anomalies_tool.

        Retorna JSON con:
        - success: bool
        - message: mensaje con rutas de archivos generados
        - station: nombre de la estacion
        - mode: modo usado
        - period: periodo descargado
        - files: lista de rutas de CSV generados
        - stats: {successful, total, partial}
        - extracted_from: archivo consolidado origen, si extrajo localmente
        - force_download: bool indicando si se ignoro cache local
        - error: detalle del error, solo si success=false
        """

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
