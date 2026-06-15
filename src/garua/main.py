import asyncio
import argparse
import sys
from garua.exceptions import (
    BrowserNotFoundError,
    SelectNotFoundError,
    TableNotFoundError,
)
from garua.settings import (
    ERROR,
    PROJECT_NAME,
    VERSION,
    YEAR_MAX,
    YEAR_MIN,
    ensure_output_dirs,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="garua",
        description="Garua — Descarga datos de estaciones meteorológicas.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  garua --search SIHUAS\n"
            "  garua --search 108047\n"
            "  garua -s 108047 -m month -y 2024 --month 9\n"
            "  garua -s 108047 -m year  -y 2024\n"
            "  garua -s 108047 -m year  -y 2024 --individual\n"
            "  garua -s 108047 -m period --start 2020 --end 2025\n"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{PROJECT_NAME} {VERSION}",
        help="Muestra la versión instalada y sale.",
    )
    parser.add_argument(
        "--doctor",
        "--health",
        action="store_true",
        help="Revisa requisitos básicos: Python, sistema, carpetas y navegador.",
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
    if args.search or args.doctor:
        return  # --search y --doctor son standalone, no necesitan nada más

    mode = args.mode

    if mode == "month":
        if args.year is not None and not (YEAR_MIN <= args.year <= YEAR_MAX):
            sys.exit(
                f"{ERROR} --year inválido: {args.year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}."
            )
        if args.month is not None and not (1 <= args.month <= 12):
            sys.exit(
                f"{ERROR} --month inválido: {args.month}. Debe estar entre 1 y 12."
            )
        if args.start or args.end:
            sys.exit(f"{ERROR} --start / --end son exclusivos de --mode period.")

    elif mode == "year":
        if args.year is not None and not (YEAR_MIN <= args.year <= YEAR_MAX):
            sys.exit(
                f"{ERROR} --year inválido: {args.year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}."
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
        if args.start is not None and not (YEAR_MIN <= args.start <= YEAR_MAX):
            sys.exit(
                f"{ERROR} --start inválido: {args.start}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}."
            )
        if args.end is not None and not (YEAR_MIN <= args.end <= YEAR_MAX):
            sys.exit(
                f"{ERROR} --end inválido: {args.end}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}."
            )
        if args.start is not None and args.end is not None and args.start > args.end:
            sys.exit(
                f"{ERROR} --start ({args.start}) no puede ser mayor que --end ({args.end})."
            )


def run_doctor() -> int:
    from rich.console import Console
    from rich import box
    from rich.panel import Panel
    from rich.table import Table

    from garua.scraping.browser import ENV_BROWSER_PATH, get_runtime_summary
    from garua.settings import CSV_DIR, EXPORTS_DIR, LOGS_DIR, OUTPUT_DIR

    console = Console()
    console.print(
        Panel(
            f"{PROJECT_NAME} v{VERSION}\nDiagnóstico de requisitos básicos",
            title="Garua Doctor",
            title_align="left",
        )
    )
    summary = get_runtime_summary()

    dirs_ok = True
    dirs_message = "Directorios listos"
    try:
        ensure_output_dirs()
    except Exception as exc:
        dirs_ok = False
        dirs_message = str(exc)

    table = Table(
        title="Diagnóstico Garua",
        show_header=True,
        header_style="bold",
        box=box.ROUNDED,
        expand=True,
    )
    table.add_column("Check", no_wrap=True)
    table.add_column("Estado", no_wrap=True)
    table.add_column("Detalle")

    table.add_row("Python", "OK", str(summary["python"]))
    table.add_row("Sistema", "OK", str(summary["platform"]))
    table.add_row(
        "Carpetas",
        "OK" if dirs_ok else "ERROR",
        (
            f"{dirs_message}\n"
            f"OUTPUT_DIR={OUTPUT_DIR}\n"
            f"CSV_DIR={CSV_DIR}\n"
            f"LOGS_DIR={LOGS_DIR}\n"
            f"EXPORTS_DIR={EXPORTS_DIR}"
        ),
    )
    table.add_row(
        "Navegador",
        "OK" if summary["browser_ok"] else "ERROR",
        (
            f"{summary['browser_message']}\n"
            f"Origen: {summary['browser_source'] or 'N/A'}\n"
            f"Ruta: {summary['browser_path'] or 'N/A'}"
        ),
    )

    console.print(table)

    if not summary["browser_ok"]:
        console.print(
            f"Configura {ENV_BROWSER_PATH} o instala Google Chrome, Brave o Microsoft Edge."
        )

    return 0 if dirs_ok and summary["browser_ok"] else 1


async def main(args: argparse.Namespace | None = None):
    from garua.models.scraping import ScrapingQueryParams
    from garua.scraping.query_modes import get_station_code, get_user_query_mode
    from garua.scraping.scraper import scraping_main
    from garua.services.station import find_station_by_code
    from garua.utils.ui_console import ui

    # Validar carpetas
    ensure_output_dirs()

    # Imprimir bienvenida
    ui.print_welcome()

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
            ui.error("Código de estación inválido o no encontrado")
            return {
                "success": False,
                "error": "Código de estación inválido o no encontrado.",
                "saved_files": [],
            }

    ui.print_station_found(query_station)

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
            cli_dict["start_year"] = args.start
        if args.end:
            cli_dict["end_year"] = args.end
        cli_dict["individual"] = (
            args.individual if args.individual is not None else False
        )  # siempre presente (default False)

    cli_dict = get_user_query_mode(cli_dict)

    ui.print_scraping_start(query_station.name, cli_dict["mode"])

    try:
        query_params = ScrapingQueryParams(
            mode=cli_dict.get("mode"),
            year=cli_dict.get("year"),
            month=cli_dict.get("month"),
            start_year=cli_dict.get("start_year"),
            end_year=cli_dict.get("end_year"),
            individual=cli_dict.get("individual", False),
        )
        query_params.validate()

        result = await scraping_main(query_station, query_params)
        return result

    except ValueError as ve:
        ui.error(f"Error de validación: {ve}")
        return {
            "success": False,
            "error": f"Error de validación: {ve}",
            "saved_files": [],
        }
    except (BrowserNotFoundError, SelectNotFoundError, TableNotFoundError) as e:
        ui.error(str(e))
        return {
            "success": False,
            "error": str(e),
            "saved_files": [],
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
        ui.print_browser_status("Cerrando navegador")
        await asyncio.sleep(1)


def cli() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    # --search es standalone: lista resultados y sale
    if args.doctor:
        return run_doctor()

    if args.search:
        from garua.services.station import search_and_print_stations
        from garua.utils.ui_console import ui

        # Imprimir bienvenida
        ui.print_welcome()
        # Ejecutar búsqueda e imprimir resultados
        search_and_print_stations(args.search)
        return 0

    try:
        validate_cli_args(args)
        asyncio.run(main(args))
        return 0
    except (KeyboardInterrupt, EOFError):
        from garua.utils.ui_console import ui

        ui.print_goodbye()
        return 0


if __name__ == "__main__":
    sys.exit(cli())
