from typing import List, Dict
import re

from garua.settings import YEAR_MAX, YEAR_MIN
from garua.utils.html_utils import extract_select_options
from garua.models.station import Station
from garua.services.station import find_station_by_code, search_stations_by_name
from garua.utils.ui_console import ui
from pathlib import Path
from typing import Union

PathInput = Union[str, Path]


class QueryModeHandler:
    """
    Maneja los diferentes modos de consulta: Month, Year, Period
    """

    def __init__(self):
        self.available_options: List[Dict[str, str]] = []

    def load_options(self, select_html: str) -> None:
        """
        Carga las opciones disponibles del select
        """
        self.available_options = extract_select_options(select_html)
        ui.success(f"{len(self.available_options)} opciones cargadas")

    def get_valid_options(self) -> List[Dict[str, str]]:
        """
        Filtra opciones válidas (que tienen valor y formato correcto YYYYMM)
        """
        valid_options = []
        for option in self.available_options:
            value = option["value"].strip()
            if value and re.match(r"^\d{6}$", value):  # Formato YYYYMM
                valid_options.append(option)
        return valid_options

    def filter_by_month(self, year: int, month: int) -> List[Dict[str, str]]:
        """
        Filtra opciones por año y mes específico
        """
        target_value = f"{year:04d}{month:02d}"
        valid_options = self.get_valid_options()

        filtered = [opt for opt in valid_options if opt["value"] == target_value]

        ui.info(f"Filtro por mes {year}/{month}: {len(filtered)} opciones encontradas")
        return filtered

    def filter_by_year(self, year: int) -> List[Dict[str, str]]:
        """
        Filtra opciones por año completo
        """
        year_str = str(year)
        valid_options = self.get_valid_options()

        filtered = [opt for opt in valid_options if opt["value"].startswith(year_str)]

        ui.info(f"Filtro por año {year}: {len(filtered)} opciones encontradas")
        return filtered

    def filter_by_period(self, start_year: int, end_year: int) -> List[Dict[str, str]]:
        """
        Filtra opciones por periodo de años
        """
        valid_options = self.get_valid_options()
        filtered = []

        for option in valid_options:
            year = int(option["value"][:4])
            if start_year <= year <= end_year:
                filtered.append(option)

        ui.info(
            f"Filtro por periodo {start_year}-{end_year}: {len(filtered)} opciones encontradas"
        )
        return filtered

    def get_available_years(self) -> List[int]:
        """
        Obtiene lista de años disponibles
        """
        valid_options = self.get_valid_options()
        years = set()

        for option in valid_options:
            year = int(option["value"][:4])
            years.add(year)

        return sorted(years)


def get_station_code() -> Station | None:
    """
    Solicita al usuario el código o nombre de la estación meteorológica.
    Primero intenta coincidencia exacta por código; si no encuentra, ofrece
    búsqueda interactiva por nombre con una lista numerada de resultados.
    """
    try:
        while True:
            ui.print_section_header("BÚSQUEDA DE ESTACIÓN")
            from rich.prompt import Prompt

            try:
                entry = Prompt.ask(
                    f"{ui.prompt('Código o nombre')} (ej: 472D30C8 o SIHUAS)"
                ).strip()
            except (KeyboardInterrupt, EOFError):
                return None

            if not entry:
                continue

            # 1. Búsqueda exacta por código
            station = find_station_by_code(entry)
            if station:
                return station

            # 2. Búsqueda por nombre
            matches = search_stations_by_name(entry)

            if not matches:
                ui.error(
                    f"No se encontró ninguna estación con el código o nombre '{entry}'."
                )
                from rich.prompt import Confirm

                try:
                    retry_confirm = Confirm.ask(
                        ui.prompt("¿Desea buscar de nuevo?", icon=""), default=True
                    )
                    retry = "s" if retry_confirm else "n"
                except (KeyboardInterrupt, EOFError):
                    return None
                if retry not in ("s", "si", "y", "yes", "1"):
                    return None
                continue

            try:
                selected = ui.select_station_result(matches, entry, max_display=20)
            except (KeyboardInterrupt, EOFError):
                return None
            if selected:
                return selected
    except (KeyboardInterrupt, EOFError):
        return None


def get_user_query_mode(cli_args: dict | None = None) -> dict:
    """
    Solicita al usuario el modo de consulta.
    Si cli_args contiene datos suficientes, los usa directamente sin preguntar.
    """
    cli_args = cli_args or {}
    mode = cli_args.get("mode")

    if not mode:
        ui.print_section_header("MODO DE CONSULTA")
        ui.console.print(
            f"{ui.prompt('1.', icon='')} Month  - Descargar un mes específico (YYYY-MM)"
        )
        ui.console.print(f"{ui.prompt('2.', icon='')} Year   - Descargar todo un año")
        ui.console.print(
            f"{ui.prompt('3.', icon='')} Period - Descargar un periodo de años (YYYY-YYYY)"
        )
        ui.console.print()

        while True:
            from rich.prompt import Prompt

            try:
                mode_input = Prompt.ask(
                    ui.prompt("Ingresa el número del modo"),
                    choices=["1", "2", "3"],
                ).strip()
            except (KeyboardInterrupt, EOFError):
                raise SystemExit(0)
            if mode_input == "1":
                mode = "month"
                break
            elif mode_input == "2":
                mode = "year"
                break
            elif mode_input == "3":
                mode = "period"
                break

    if mode == "month":
        return get_month_params(cli_args)
    elif mode == "year":
        return get_year_params(cli_args)
    elif mode == "period":
        return get_period_params(cli_args)
    else:
        ui.error(f"Modo inválido: '{mode}'. Use: month, year o period.")
        raise SystemExit(1)


def get_month_params(cli_args: dict | None = None) -> dict:
    """
    Obtiene parámetros para consulta mensual.
    Usa cli_args si están disponibles; pregunta solo lo que falte.
    """
    cli_args = cli_args or {}
    ui.info("📅 Modo MONTH seleccionado")

    # --- año ---
    year = cli_args.get("year")
    if year is None:
        while True:
            try:
                from rich.prompt import IntPrompt

                year = IntPrompt.ask(f"{ui.prompt('Ingresa el año')} (ej: 2024)")
                if YEAR_MIN <= year <= YEAR_MAX:
                    break
                ui.error(f"Año inválido. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.")
            except (KeyboardInterrupt, EOFError):
                raise SystemExit(0)
            except ValueError:
                ui.error("Por favor ingresa un número válido.")
    elif not (YEAR_MIN <= year <= YEAR_MAX):
        ui.error(f"Año inválido: {year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.")
        raise SystemExit(1)

    # --- mes ---
    month = cli_args.get("month")
    if month is None:
        while True:
            try:
                from rich.prompt import IntPrompt

                month = IntPrompt.ask(f"{ui.prompt('Ingresa el mes')} (1-12)")
                if 1 <= month <= 12:
                    break
                ui.error("Mes inválido. Debe estar entre 1 y 12.")
            except (KeyboardInterrupt, EOFError):
                raise SystemExit(0)
            except ValueError:
                ui.error("Por favor ingresa un número válido.")
    elif not (1 <= month <= 12):
        ui.error(f"Mes inválido: {month}. Debe estar entre 1 y 12.")
        raise SystemExit(1)

    return {
        "mode": "month",
        "year": year,
        "month": month,
        # month siempre genera archivo individual (un solo mes)
        "individual": True,
    }


def get_year_params(cli_args: dict | None = None) -> dict:
    """
    Obtiene parámetros para consulta anual.
    Usa cli_args si están disponibles; pregunta solo lo que falte.
    Consolidado es el modo por defecto.
    """
    cli_args = cli_args or {}
    ui.info("📅 Modo YEAR seleccionado")

    # --- año ---
    year = cli_args.get("year")
    if year is None:
        while True:
            try:
                from rich.prompt import IntPrompt

                year = IntPrompt.ask(f"{ui.prompt('Ingresa el año')} (ej: 2024)")
                if YEAR_MIN <= year <= YEAR_MAX:
                    break
                ui.error(f"Año inválido. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.")
            except (KeyboardInterrupt, EOFError):
                raise SystemExit(0)
            except ValueError:
                ui.error("Por favor ingresa un número válido.")
    elif not (YEAR_MIN <= year <= YEAR_MAX):
        ui.error(f"Año inválido: {year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.")
        raise SystemExit(1)

    # --- consolidado (default: True) ---
    # cli_args puede traer individual=True (flag --individual)
    consolidated = not cli_args.get("individual", False)
    if "individual" not in cli_args and "year" not in cli_args:
        # modo interactivo: preguntar solo si no vino de CLI
        from rich.prompt import Confirm

        try:
            consolidated = Confirm.ask(
                ui.prompt("¿Guardar como archivo consolidado?", icon=""),
                default=True,
            )
        except (KeyboardInterrupt, EOFError):
            raise SystemExit(0)

    return {"mode": "year", "year": year, "individual": not consolidated}


def get_period_params(cli_args: dict | None = None) -> dict:
    """
    Obtiene parámetros para consulta de periodo.
    Usa cli_args si están disponibles; pregunta solo lo que falte.
    Consolidado es el modo por defecto.
    """
    cli_args = cli_args or {}
    ui.info("📅 Modo PERIOD seleccionado")

    # --- año inicial ---
    start_year = cli_args.get("start_year")
    if start_year is None:
        while True:
            try:
                from rich.prompt import IntPrompt

                start_year = IntPrompt.ask(
                    f"{ui.prompt('Ingresa el año inicial')} (ej: 2020)"
                )
                if YEAR_MIN <= start_year <= YEAR_MAX:
                    break
                ui.error(f"Año inválido. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.")
            except (KeyboardInterrupt, EOFError):
                raise SystemExit(0)
            except ValueError:
                ui.error("Por favor ingresa un número válido.")
    elif not (YEAR_MIN <= start_year <= YEAR_MAX):
        ui.error(
            f"Año inicial inválido: {start_year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}."
        )
        raise SystemExit(1)

    # --- año final ---
    end_year = cli_args.get("end_year")
    if end_year is None:
        while True:
            try:
                from rich.prompt import IntPrompt

                end_year = IntPrompt.ask(
                    f"{ui.prompt('Ingresa el año final')} (ej: 2025)"
                )
                if end_year < start_year:
                    ui.error(
                        f"El año final no puede ser menor que el inicial ({start_year})."
                    )
                    continue
                if YEAR_MIN <= end_year <= YEAR_MAX:
                    break
                ui.error(f"Año inválido. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.")
            except (KeyboardInterrupt, EOFError):
                raise SystemExit(0)
            except ValueError:
                ui.error("Por favor ingresa un número válido.")
    else:
        if end_year < start_year:
            ui.error(
                f"El año final ({end_year}) no puede ser menor que el inicial ({start_year})."
            )
            raise SystemExit(1)
        if not (YEAR_MIN <= end_year <= YEAR_MAX):
            ui.error(
                f"Año final inválido: {end_year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}."
            )
            raise SystemExit(1)

    # --- consolidado (default: True) ---
    consolidated = not cli_args.get("individual", False)
    if "individual" not in cli_args and "start_year" not in cli_args:
        from rich.prompt import Confirm

        try:
            consolidated = Confirm.ask(
                ui.prompt("¿Guardar como archivo consolidado?", icon=""), default=True
            )
        except (KeyboardInterrupt, EOFError):
            raise SystemExit(0)

    return {
        "mode": "period",
        "start_year": start_year,
        "end_year": end_year,
        "individual": not consolidated,
    }
