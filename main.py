import asyncio
import random
import argparse
import sys
import zendriver as zd
from zendriver import cdp
from bs4 import BeautifulSoup
from settings import (
    SUCCESS,
    ERROR,
    PROCESSING,
    WARNING,
    TIMEOUT_SECONDS,
    DATA_ENDPOINT,
    JITTER_MIN,
    JITTER_MAX,
    YEAR_BOUNDARY_SLEEP,
    MAX_RETRIES,
    RETRY_SLEEP,
)
from src.query_handler import (
    QueryModeHandler,
    CSVManager,
    get_user_query_mode,
    get_station_code,
)
from src.exceptions import TableNotFoundError, SelectNotFoundError
from src.station_service import (
    create_station_url,
    get_headers_for_station,
    find_station_by_code,
    search_and_print_stations,
)


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
        print(f"{SUCCESS} Página configurada. Carga inicial capturada y descartada.")
    except asyncio.TimeoutError:
        print(f"{SUCCESS} Página configurada (sin POST inicial detectado).")

    return page, response_queue


async def get_select_options(page) -> str:
    """Obtiene el HTML del select CBOFiltro para parsear sus opciones."""
    select_found = await page.wait_for(selector="select#CBOFiltro")
    if not select_found:
        raise SelectNotFoundError(f"{ERROR} Select CBOFiltro no encontrado")
    return await select_found.get_html()


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


async def process_option(
    page, response_queue: asyncio.Queue, option, csv_manager, save_individual=True
) -> bool:
    """
    Procesa una opción del select usando intercepción directa de red.
    Reintenta hasta MAX_RETRIES veces ante fallos transitorios.
    """
    print(f"\n{PROCESSING} Procesando opción: {option['text']} ({option['value']})")

    async def select_action():
        option_elem = await page.query_selector(f"option[value='{option['value']}']")
        if not option_elem:
            raise SelectNotFoundError(
                f"Opción no encontrada en el select: {option['value']}"
            )
        await option_elem.select_option()
        print(f"{SUCCESS} Opción seleccionada: {option['value']}")

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
            print(
                f"{SUCCESS} Datos capturados para {option['value']} ({len(full_html):,} bytes)"
            )

            if save_individual:
                csv_manager.save_individual_file(table_html, option["value"])
            else:
                csv_manager.add_table_data(table_html, option["value"])

            return True

        except Exception as e:
            if attempt <= MAX_RETRIES:
                print(
                    f"{WARNING} Intento {attempt} fallido para {option['value']}: {e}"
                )
                print(f"{PROCESSING} Reintentando en {RETRY_SLEEP}s...")
                await asyncio.sleep(RETRY_SLEEP)
            else:
                print(
                    f"{ERROR} Error procesando opción {option['value']} tras {attempt} intentos: {e}"
                )
                import traceback

                traceback.print_exc()

    return False


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="SENAMHI Scraper — Descarga datos de estaciones meteorológicas.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python main.py --search SIHUAS\n"
            "  python main.py --search 108047\n"
            "  python main.py -s 108047 -m month -y 2024 --month 9\n"
            "  python main.py -s 108047 -m year  -y 2024\n"
            "  python main.py -s 108047 -m year  -y 2024 --individual\n"
            "  python main.py -s 108047 -m period --start 2020 --end 2025\n"
        ),
    )

    # Búsqueda standalone
    parser.add_argument(
        "-S",
        "--search",
        metavar="QUERY",
        help="Busca estaciones por código exacto o nombre parcial y las lista. No inicia el scraping.",
    )

    # Estación
    parser.add_argument(
        "-s",
        "--station",
        metavar="CÓDIGO",
        help="Código interno de la estación (ej: 108047).",
    )

    # Modo
    parser.add_argument(
        "-m",
        "--mode",
        choices=["month", "year", "period"],
        metavar="MODO",
        help="Modo de consulta: month | year | period.",
    )

    # Parámetros de tiempo
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        metavar="AÑO",
        help="Año (requerido para month y year).",
    )
    parser.add_argument(
        "--month", type=int, metavar="MES", help="Mes 1-12 (solo para --mode month)."
    )
    parser.add_argument(
        "--start",
        type=int,
        metavar="AÑO",
        help="Año inicial (solo para --mode period).",
    )
    parser.add_argument(
        "--end", type=int, metavar="AÑO", help="Año final   (solo para --mode period)."
    )

    # Formato de salida
    parser.add_argument(
        "-i",
        "--individual",
        action="store_true",
        default=False,
        help="Genera un archivo CSV por cada mes en lugar de uno consolidado (por defecto: consolidado).",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        help="Directorio de salida para los CSV (por defecto: el definido en settings.py).",
    )

    return parser


def validate_cli_args(args: argparse.Namespace) -> None:
    """
    Valida combinaciones de argumentos CLI y lanza SystemExit con mensaje claro
    si hay errores de uso antes de arrancar el navegador.
    """
    if args.search:
        return  # --search es standalone, no necesita nada más

    mode = args.mode
    if mode == "month":
        if args.year is not None and not (2000 <= args.year <= 2050):
            sys.exit(
                f"{ERROR} --year inválido: {args.year}. Debe estar entre 2000 y 2050."
            )
        if args.month is not None and not (1 <= args.month <= 12):
            sys.exit(
                f"{ERROR} --month inválido: {args.month}. Debe estar entre 1 y 12."
            )
        if args.start or args.end:
            sys.exit(f"{ERROR} --start / --end son exclusivos de --mode period.")

    elif mode == "year":
        if args.year is not None and not (2000 <= args.year <= 2050):
            sys.exit(
                f"{ERROR} --year inválido: {args.year}. Debe estar entre 2000 y 2050."
            )
        if args.month or args.start or args.end:
            sys.exit(f"{ERROR} --month / --start / --end no aplican para --mode year.")

    elif mode == "period":
        if args.year:
            sys.exit(
                f"{ERROR} --year no aplica para --mode period. Use --start y --end."
            )
        if args.month:
            sys.exit(f"{ERROR} --month no aplica para --mode period.")
        if args.start is not None and not (2000 <= args.start <= 2050):
            sys.exit(
                f"{ERROR} --start inválido: {args.start}. Debe estar entre 2000 y 2050."
            )
        if args.end is not None and not (2000 <= args.end <= 2050):
            sys.exit(
                f"{ERROR} --end inválido: {args.end}. Debe estar entre 2000 y 2050."
            )
        if args.start is not None and args.end is not None and args.start > args.end:
            sys.exit(
                f"{ERROR} --start ({args.start}) no puede ser mayor que --end ({args.end})."
            )


async def main(args: argparse.Namespace | None = None):
    print(f"{SUCCESS} Bienvenido al sistema de scraping del SENAMHI")

    # --- Resolución de estación ---
    if args and args.station:
        query_station = find_station_by_code(args.station)
        if not query_station:
            sys.exit(
                f"{ERROR} No se encontró ninguna estación con el código '{args.station}'.\n"
                f"       Use --search para buscar por nombre."
            )
    else:
        query_station = get_station_code()
        if not query_station:
            print(f"{ERROR} Código de estación inválido o no encontrado")
            return

    print(f"{SUCCESS} Estación encontrada: {query_station.name} ({query_station.code})")

    headers = get_headers_for_station(query_station)
    station_name = query_station.name.replace(" ", "")

    # Construir dict de args CLI para que get_user_query_mode solo pregunte lo que falta
    cli_dict = {}
    if args:
        if args.mode:
            cli_dict["mode"] = args.mode
        if args.year:
            cli_dict["year"] = args.year
        if args.month:
            cli_dict["month"] = args.month
        if args.start:
            cli_dict["start"] = args.start
        if args.end:
            cli_dict["end"] = args.end
        cli_dict["individual"] = args.individual  # siempre presente (default False)

    query_params = get_user_query_mode(station_name, cli_dict)

    print(
        f"\n🚀 Iniciando scraping — Estación: {query_station.name} | Modo: {query_params['mode'].upper()}"
    )

    browser = await zd.start()

    try:
        url_station = create_station_url(query_station)
        page, response_queue = await setup_page(browser, url_station)

        select_html = await get_select_options(page)

        query_handler = QueryModeHandler()
        query_handler.load_options(select_html)

        csv_output_dir = args.output if (args and args.output) else None
        csv_manager = CSVManager(
            station_name,
            **({} if not csv_output_dir else {"output_dir": csv_output_dir}),
        )
        csv_manager.headers = headers
        csv_manager.start_line = 1 if query_station.status == "AUTOMATICA" else 2

        available_years = query_handler.get_available_years()
        print(f"📅 Años disponibles: {available_years}")

        if query_params["mode"] == "month":
            filtered_options = query_handler.filter_by_month(
                query_params["year"], query_params["month"]
            )
            save_individual = True
        elif query_params["mode"] == "year":
            filtered_options = query_handler.filter_by_year(query_params["year"])
            save_individual = not query_params["consolidated"]
        elif query_params["mode"] == "period":
            filtered_options = query_handler.filter_by_period(
                query_params["start_year"], query_params["end_year"]
            )
            save_individual = not query_params["consolidated"]

        if not filtered_options:
            print(
                f"{ERROR} No se encontraron opciones para los criterios especificados"
            )
            return

        print(f"\n📊 Se procesarán {len(filtered_options)} opciones")

        successful_count = 0
        prev_year = None
        for i, option in enumerate(filtered_options, 1):
            print(f"\n--- Procesando {i}/{len(filtered_options)} ---")

            current_year = option["value"][:4]
            if prev_year is not None and current_year != prev_year:
                print(
                    f"📅 Nuevo año ({current_year}) — pausa de {YEAR_BOUNDARY_SLEEP}s"
                )
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

        if not save_individual and query_params.get("filename"):
            csv_manager.save_consolidated_file(query_params["filename"])

        print(
            f"\n🎉 Proceso completado: {successful_count}/{len(filtered_options)} opciones procesadas exitosamente"
        )

    except Exception as e:
        print(f"{ERROR} Error durante el proceso: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("🔍 Cerrando navegador...")
        await asyncio.sleep(1)
        await browser.stop()


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()

    # --search es standalone: lista resultados y sale
    if args.search:
        search_and_print_stations(args.search)
        sys.exit(0)

    validate_cli_args(args)
    asyncio.run(main(args))
