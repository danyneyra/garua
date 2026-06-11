import asyncio
import zendriver as zd
from zendriver import cdp
from bs4 import BeautifulSoup
import random

from garua.settings import (
    ERROR,
    TIMEOUT_SECONDS,
    DATA_ENDPOINT,
    MAX_RETRIES,
    RETRY_SLEEP,
    JITTER_MIN,
    JITTER_MAX,
    YEAR_BOUNDARY_SLEEP,
)
from garua.models.station import Station
from garua.models.scraping import ScrapingQueryParams
from garua.exceptions import TableNotFoundError, SelectNotFoundError
from garua.utils.ui_console import ui
from garua.services.station import (
    build_scraping_url_for_station,
    get_headers_for_station,
)
from garua.scraping.query_modes import QueryModeHandler
from garua.storage.csv_manager import CSVManager


async def capture_post_response(
    page, response_queue: asyncio.Queue, trigger_action
) -> str:
    """
    Ejecuta trigger_action (cambio de select) e intercepta directamente
    la respuesta HTML del endpoint de datos via CDP.
    Evita esperar la recarga del iframe en el DOM.
    """
    # Limpiar eventos residuales antes de la acción
    while not response_queue.empty():
        response_queue.get_nowait()

    await trigger_action()

    # Esperar el request_id del POST generado por el cambio de select
    request_id = await asyncio.wait_for(response_queue.get(), timeout=TIMEOUT_SECONDS)

    # get_response_body retorna una tupla (body: str, base64Encoded: bool)
    body, _ = await page.send(cdp.network.get_response_body(request_id))
    return body


async def setup_page(browser, url: str):
    """
    Carga la página, habilita monitoreo de red CDP y prepara la pestaña de tabla.
    Retorna (page, response_queue) donde response_queue recibe request_ids
    de cada POST al endpoint de datos.
    """
    page = await browser.get(url)

    # Habilitar monitoreo de red via CDP
    await page.send(cdp.network.enable())

    # ResponseReceived dispara cuando llegan los headers (body aún no está disponible).
    # LoadingFinished dispara cuando el body completo está en el buffer CDP.
    # Esperamos LoadingFinished antes de llamar get_response_body.
    response_queue: asyncio.Queue = asyncio.Queue()
    pending_request_ids: set = set()

    async def on_response_received(event: cdp.network.ResponseReceived):
        if DATA_ENDPOINT in str(event.response.url):
            pending_request_ids.add(event.request_id)

    async def on_loading_finished(event: cdp.network.LoadingFinished):
        if event.request_id in pending_request_ids:
            pending_request_ids.discard(event.request_id)
            await response_queue.put(event.request_id)

    page.add_handler(cdp.network.ResponseReceived, on_response_received)
    page.add_handler(cdp.network.LoadingFinished, on_loading_finished)

    # Hacer clic en la pestaña de tabla
    tab_elem = await page.wait_for(selector="a#tabla-tab")
    await tab_elem.click()

    # Confirmar que el select está presente (la página cargó correctamente)
    select_found = await page.wait_for(selector="select#CBOFiltro")
    if not select_found:
        raise SelectNotFoundError(f"{ERROR} Select CBOFiltro no encontrado")

    # Descartar el request_id del POST inicial (carga de la página)
    try:
        await asyncio.wait_for(response_queue.get(), timeout=15)
        ui.success("Página configurada. Carga inicial capturada y descartada.")
    except asyncio.TimeoutError:
        ui.success("Página configurada (sin POST inicial detectado).")

    return page, response_queue


async def get_select_options(page) -> str:
    """Obtiene el HTML del select CBOFiltro para parsear sus opciones."""
    select_found = await page.wait_for(selector="select#CBOFiltro")
    if not select_found:
        raise SelectNotFoundError(f"{ERROR} Select CBOFiltro no encontrado")
    return await select_found.get_html()


async def process_option(
    page, response_queue: asyncio.Queue, option, csv_manager, save_individual=True
) -> bool:
    """
    Procesa una opción del select usando intercepción directa de red.
    Reintenta hasta MAX_RETRIES veces ante fallos transitorios.
    """
    ui.processing(f"Procesando opción: {option['text']} ({option['value']})")

    async def select_action():
        option_elem = await page.query_selector(f"option[value='{option['value']}']")
        if not option_elem:
            raise SelectNotFoundError(
                f"Opción no encontrada en el select: {option['value']}"
            )
        await option_elem.select_option()
        ui.success(f"Opción seleccionada: {option['value']}")

    for attempt in range(1, MAX_RETRIES + 2):  # intentos: 1..MAX_RETRIES+1
        try:
            full_html = await capture_post_response(page, response_queue, select_action)

            soup = BeautifulSoup(full_html, "html.parser")
            data_table = soup.find("table", id="dataTable")
            if not data_table:
                raise TableNotFoundError(
                    "No se encontró table#dataTable en la respuesta del endpoint"
                )

            table_html = str(data_table)
            ui.print_data_captured(option["value"], len(full_html))

            if save_individual:
                csv_manager.save_individual_file(table_html, option["value"])
            else:
                csv_manager.add_table_data(table_html, option["value"])

            return True

        except Exception as e:
            if attempt <= MAX_RETRIES:
                ui.print_retry_attempt(attempt, option["value"], str(e))
                await asyncio.sleep(RETRY_SLEEP)
            else:
                ui.error(
                    f"Error procesando opción {option['value']} tras {attempt} intentos: {e}"
                )
                import traceback

                traceback.print_exc()

    return False


async def scraping_main(query_station: Station, query_params: ScrapingQueryParams):
    try:
        # Obtener headers para el csv de acuerdo al tipo y categoría de estación
        headers = get_headers_for_station(query_station)

        # Construir URL de la estación y preparar navegador + página
        url_station = build_scraping_url_for_station(query_station)
        browser = await zd.start()
        page, response_queue = await setup_page(browser, url_station)

        # Seleccionar el periodo a consultar y obtener el HTML del select para parsear opciones
        select_html = await get_select_options(page)
        query_handler = QueryModeHandler()
        query_handler.load_options(select_html)

        # Preparar CSVManager con directorio de salida (si se proporciona) y configuración de encabezados
        csv_output_dir = query_params.output_dir if query_params.output_dir else None
        csv_manager = CSVManager(query_station, csv_output_dir)
        csv_manager.headers = headers
        csv_manager.start_line = 1 if query_station.status == "AUTOMATICA" else 2

        available_years = query_handler.get_available_years()
        ui.print_available_years(available_years)

        # Filtrar opciones del select según el modo de consulta (mes, año, periodo) y parámetros proporcionados
        if query_params.mode == "month":
            if not query_params.year or not query_params.month:
                raise ValueError(
                    f"Año {query_params.year} o mes {query_params.month} no disponible para esta estación"
                )
            filtered_options = query_handler.filter_by_month(
                query_params.year, query_params.month
            )
            save_individual = True
        elif query_params.mode == "year":
            if not query_params.year:
                raise ValueError(
                    f"Año {query_params.year} no disponible para esta estación"
                )
            filtered_options = query_handler.filter_by_year(query_params.year)
            save_individual = query_params.individual
        elif query_params.mode == "period":
            if not query_params.start_year or not query_params.end_year:
                raise ValueError(
                    f"Años de inicio {query_params.start_year} o fin {query_params.end_year} no disponibles para esta estación"
                )
            filtered_options = query_handler.filter_by_period(
                query_params.start_year, query_params.end_year
            )
            save_individual = query_params.individual

        # ── Filtro MCP: Periodos específicos ──────────────────────────────────
        # Si la llamada viene del MCP con periodos específicos, filtrar solo esos
        if query_params.mcp_filter_periods:
            target_values = {
                f"{p.year:04d}{p.month:02d}" for p in query_params.mcp_filter_periods
            }
            filtered_options = [
                opt for opt in filtered_options if opt["value"] in target_values
            ]
            save_individual = True  # Siempre individual para periodos MCP
            ui.info(
                f"🔍 Filtro MCP: {len(filtered_options)} periodo(s) específico(s) seleccionado(s)"
            )

        if not filtered_options:
            ui.error("No se encontraron opciones para los criterios especificados")
            return {
                "success": False,
                "error": "No se encontraron opciones para los criterios especificados.",
                "saved_files": [],
            }

        ui.print_options_count(len(filtered_options))

        successful_count = 0
        prev_year = None
        for i, option in enumerate(filtered_options, 1):
            ui.print_processing_option(i, len(filtered_options), option["text"])

            current_year = option["value"][:4]
            if prev_year is not None and current_year != prev_year:
                ui.info(f"Nuevo año ({current_year}) — pausa de {YEAR_BOUNDARY_SLEEP}s")
                await asyncio.sleep(YEAR_BOUNDARY_SLEEP)
            prev_year = current_year

            success = await process_option(
                page,
                response_queue,
                option,
                csv_manager,
                save_individual=save_individual,
            )
            if success:
                successful_count += 1

            if i < len(filtered_options):
                jitter = random.uniform(JITTER_MIN, JITTER_MAX)
                await asyncio.sleep(jitter)

        if not save_individual:
            csv_manager.save_consolidated_file(query_params)

        ui.print_completion_summary(
            successful_count, len(filtered_options), csv_manager.saved_files
        )
        return {
            "success": successful_count > 0,
            "station_name": query_station.name,
            "mode": query_params.mode,
            "saved_files": csv_manager.saved_files,
            "successful_count": successful_count,
            "total_options": len(filtered_options),
        }
    except Exception as e:
        ui.error(f"Error durante el proceso: {e}")
        import traceback

        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "saved_files": [],
        }
    finally:
        await asyncio.sleep(1)
        await browser.stop()
