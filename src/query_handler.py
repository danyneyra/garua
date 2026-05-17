import settings
from typing import List, Dict
import re
import os
from src.html_utils import extract_select_options, html_table_to_csv
from src.models.station import Station
from src.station_service import find_station_by_code, search_stations_by_name


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
        print(f"{settings.SUCCESS} {len(self.available_options)} opciones cargadas")

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

        print(f"📅 Filtro por mes {year}/{month}: {len(filtered)} opciones encontradas")
        return filtered

    def filter_by_year(self, year: int) -> List[Dict[str, str]]:
        """
        Filtra opciones por año completo
        """
        year_str = str(year)
        valid_options = self.get_valid_options()

        filtered = [opt for opt in valid_options if opt["value"].startswith(year_str)]

        print(f"📅 Filtro por año {year}: {len(filtered)} opciones encontradas")
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

        print(
            f"📅 Filtro por periodo {start_year}-{end_year}: {len(filtered)} opciones encontradas"
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


class CSVManager:
    """
    Maneja la creación y escritura de archivos CSV
    """

    def __init__(self, filename: str, output_dir: str = settings.CSV_DIR):
        self.filename = filename
        self.output_dir = os.path.join(output_dir, filename)
        self.csv_data_buffer = []
        self.headers = []
        self.start_line = 1  # Línea inicial para procesar (después de encabezados)

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def add_table_data(self, table_html: str, option_value: str) -> None:
        """
        Añade datos de una tabla al buffer
        """
        try:
            csv_content = html_table_to_csv(
                table_html, separator=settings.CSV_SEPARATOR, start_line=self.start_line
            )
            if csv_content:
                processed_lines = self._process_csv_lines(csv_content)
                # Comprobar si el buffer ya tiene encabezados
                if not self.csv_data_buffer and self.headers:
                    self.csv_data_buffer.append(
                        settings.CSV_SEPARATOR.join(self.headers)
                    )  # Añadir encabezados al inicio
                self.csv_data_buffer.extend(processed_lines)
                print(
                    f"{settings.SUCCESS} Datos añadidos al buffer para periodo {option_value}: {len(processed_lines)} filas"
                )
        except Exception as e:
            print(f"{settings.ERROR} Error procesando tabla para {option_value}: {e}")

    def _process_csv_lines(self, csv_content: str) -> List[str]:
        """
        Procesa las líneas CSV añadiendo el periodo
        """
        lines = csv_content.split("\n")
        processed_lines = []

        for line in lines:
            if line.strip():
                processed_lines.append(line)

        return processed_lines

    def save_individual_file(self, table_html: str, option_value: str) -> str:
        """
        Guarda una tabla individual en un archivo CSV
        """
        filename = f"{self.filename}-{option_value}.csv"
        filepath = os.path.join(self.output_dir, filename)

        try:
            csv_content = html_table_to_csv(
                table_html, separator=settings.CSV_SEPARATOR, start_line=self.start_line
            )
            if csv_content:
                with open(filepath, "w", encoding=settings.CSV_ENCODING) as f:
                    f.write(
                        settings.CSV_SEPARATOR.join(self.headers) + "\n" + csv_content
                    )
                print(f"{settings.SUCCESS} Archivo individual guardado: {filename}")
                return filepath
        except Exception as e:
            print(f"{settings.ERROR} Error guardando archivo {filename}: {e}")

        return ""

    def save_consolidated_file(self, filename: str) -> str:
        """
        Guarda todos los datos del buffer en un archivo consolidado
        """
        if not self.csv_data_buffer:
            print(f"{settings.ERROR} No hay datos en el buffer para guardar")
            return ""

        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, "w", encoding=settings.CSV_ENCODING) as f:
                f.write("\n".join(self.csv_data_buffer))

            print(f"{settings.SUCCESS} Archivo consolidado guardado: {filename}")
            print(f"📊 Contiene {len(self.csv_data_buffer)} líneas")
            return filepath

        except Exception as e:
            print(f"{settings.ERROR} Error guardando archivo consolidado: {e}")
            return ""

    def clear_buffer(self):
        """
        Limpia el buffer de datos
        """
        self.csv_data_buffer.clear()


def get_station_code() -> Station | None:
    """
    Solicita al usuario el código o nombre de la estación meteorológica.
    Primero intenta coincidencia exacta por código; si no encuentra, ofrece
    búsqueda interactiva por nombre con una lista numerada de resultados.
    """
    while True:
        print("\n" + "=" * 50)
        print("🔍 INGRESE EL CÓDIGO O NOMBRE DE LA ESTACIÓN")
        entry = input("Código o nombre (ej: 472D30C8 o SIHUAS): ").strip()

        if not entry:
            continue

        # 1. Búsqueda exacta por código
        station = find_station_by_code(entry)
        if station:
            return station

        # 2. Búsqueda por nombre
        matches = search_stations_by_name(entry)

        if not matches:
            print(
                f"{settings.ERROR} No se encontró ninguna estación con el código o nombre '{entry}'."
            )
            retry = input("¿Desea buscar de nuevo? (s/n): ").strip().lower()
            if retry not in ("s", "si", "y", "yes", "1"):
                return None
            continue

        MAX_DISPLAY = 20
        shown = matches[:MAX_DISPLAY]
        print(f"\n🔍 {len(matches)} estación(es) encontrada(s):")
        station_type_map = {"M": "METEREOLOGICA", "H": "HIDROLOGICA"}
        for i, s in enumerate(shown, 1):
            print(
                f"  {i:2}. {s.name:<30} {station_type_map.get(s.station_type, 'DESCONOCIDO'):<15} {s.category:<6} {s.status:<10} [cod: {s.code}]"
            )
        if len(matches) > MAX_DISPLAY:
            print(
                f"  ... y {len(matches) - MAX_DISPLAY} más. Refine su búsqueda para ver menos resultados."
            )

        while True:
            pick = input(
                f"\nSeleccione número (1-{len(shown)}) o Enter para nueva búsqueda: "
            ).strip()
            if pick == "":
                break
            try:
                idx = int(pick) - 1
                if 0 <= idx < len(shown):
                    return shown[idx]
                print(
                    f"{settings.ERROR} Número fuera de rango. Elija entre 1 y {len(shown)}."
                )
            except ValueError:
                print(f"{settings.ERROR} Por favor ingresa un número válido.")


def get_user_query_mode(filename: str, cli_args: dict | None = None) -> dict:
    """
    Solicita al usuario el modo de consulta.
    Si cli_args contiene datos suficientes, los usa directamente sin preguntar.
    """
    cli_args = cli_args or {}
    mode = cli_args.get("mode")

    if not mode:
        print("\n" + "=" * 50)
        print("🔍 SELECCIONA EL MODO DE CONSULTA")
        print("=" * 50)
        print("1. Month  - Descargar un mes específico (YYYY-MM)")
        print("2. Year   - Descargar todo un año")
        print("3. Period - Descargar un periodo de años (YYYY-YYYY)")
        print("=" * 50)

        while True:
            mode_input = input("Ingresa el número del modo (1-3): ").strip()
            if mode_input == "1":
                mode = "month"
                break
            elif mode_input == "2":
                mode = "year"
                break
            elif mode_input == "3":
                mode = "period"
                break
            else:
                print(f"{settings.ERROR} Opción inválida. Por favor ingresa 1, 2 o 3.")

    if mode == "month":
        return get_month_params(filename, cli_args)
    elif mode == "year":
        return get_year_params(filename, cli_args)
    elif mode == "period":
        return get_period_params(filename, cli_args)
    else:
        print(f"{settings.ERROR} Modo inválido: '{mode}'. Use: month, year o period.")
        raise SystemExit(1)


def get_month_params(filename: str, cli_args: dict | None = None) -> dict:
    """
    Obtiene parámetros para consulta mensual.
    Usa cli_args si están disponibles; pregunta solo lo que falte.
    """
    cli_args = cli_args or {}
    print("\n📅 Modo MONTH seleccionado")

    # --- año ---
    year = cli_args.get("year")
    if year is None:
        while True:
            try:
                year = int(input("Ingresa el año (ej: 2024): ").strip())
                if 2000 <= year <= 2050:
                    break
                print(f"{settings.ERROR} Año inválido. Debe estar entre 2000 y 2050.")
            except ValueError:
                print(f"{settings.ERROR} Por favor ingresa un número válido.")
    elif not (2000 <= year <= 2050):
        print(f"{settings.ERROR} Año inválido: {year}. Debe estar entre 2000 y 2050.")
        raise SystemExit(1)

    # --- mes ---
    month = cli_args.get("month")
    if month is None:
        while True:
            try:
                month = int(input("Ingresa el mes (1-12): ").strip())
                if 1 <= month <= 12:
                    break
                print(f"{settings.ERROR} Mes inválido. Debe estar entre 1 y 12.")
            except ValueError:
                print(f"{settings.ERROR} Por favor ingresa un número válido.")
    elif not (1 <= month <= 12):
        print(f"{settings.ERROR} Mes inválido: {month}. Debe estar entre 1 y 12.")
        raise SystemExit(1)

    return {
        "mode": "month",
        "year": year,
        "month": month,
        # month siempre genera archivo individual (un solo mes)
        "consolidated": False,
        "filename": f"{filename}-{year:04d}{month:02d}.csv",
    }


def get_year_params(filename: str, cli_args: dict | None = None) -> dict:
    """
    Obtiene parámetros para consulta anual.
    Usa cli_args si están disponibles; pregunta solo lo que falte.
    Consolidado es el modo por defecto.
    """
    cli_args = cli_args or {}
    print("\n📅 Modo YEAR seleccionado")

    # --- año ---
    year = cli_args.get("year")
    if year is None:
        while True:
            try:
                year = int(input("Ingresa el año (ej: 2024): ").strip())
                if 2000 <= year <= 2050:
                    break
                print(f"{settings.ERROR} Año inválido. Debe estar entre 2000 y 2050.")
            except ValueError:
                print(f"{settings.ERROR} Por favor ingresa un número válido.")
    elif not (2000 <= year <= 2050):
        print(f"{settings.ERROR} Año inválido: {year}. Debe estar entre 2000 y 2050.")
        raise SystemExit(1)

    # --- consolidado (default: True) ---
    # cli_args puede traer individual=True (flag --individual)
    consolidated = not cli_args.get("individual", False)
    if "individual" not in cli_args and "consolidated" not in cli_args:
        # modo interactivo: preguntar solo si no vino de CLI
        if "year" not in cli_args:  # si el año también fue interactivo, preguntar
            save_mode = (
                input("¿Guardar como archivo consolidado? [S/n]: ").strip().lower()
            )
            consolidated = save_mode not in ("n", "no")

    return {
        "mode": "year",
        "year": year,
        "consolidated": consolidated,
        "filename": f"{filename}-{year}.csv" if consolidated else None,
    }


def get_period_params(filename: str, cli_args: dict | None = None) -> dict:
    """
    Obtiene parámetros para consulta de periodo.
    Usa cli_args si están disponibles; pregunta solo lo que falte.
    Consolidado es el modo por defecto.
    """
    cli_args = cli_args or {}
    print("\n📅 Modo PERIOD seleccionado")

    # --- año inicial ---
    start_year = cli_args.get("start")
    if start_year is None:
        while True:
            try:
                start_year = int(input("Ingresa el año inicial (ej: 2020): ").strip())
                if 2000 <= start_year <= 2050:
                    break
                print(f"{settings.ERROR} Año inválido. Debe estar entre 2000 y 2050.")
            except ValueError:
                print(f"{settings.ERROR} Por favor ingresa un número válido.")
    elif not (2000 <= start_year <= 2050):
        print(
            f"{settings.ERROR} Año inicial inválido: {start_year}. Debe estar entre 2000 y 2050."
        )
        raise SystemExit(1)

    # --- año final ---
    end_year = cli_args.get("end")
    if end_year is None:
        while True:
            try:
                end_year = int(input("Ingresa el año final (ej: 2025): ").strip())
                if end_year < start_year:
                    print(
                        f"{settings.ERROR} El año final no puede ser menor que el inicial ({start_year})."
                    )
                    continue
                if 2000 <= end_year <= 2050:
                    break
                print(f"{settings.ERROR} Año inválido. Debe estar entre 2000 y 2050.")
            except ValueError:
                print(f"{settings.ERROR} Por favor ingresa un número válido.")
    else:
        if end_year < start_year:
            print(
                f"{settings.ERROR} El año final ({end_year}) no puede ser menor que el inicial ({start_year})."
            )
            raise SystemExit(1)
        if not (2000 <= end_year <= 2050):
            print(
                f"{settings.ERROR} Año final inválido: {end_year}. Debe estar entre 2000 y 2050."
            )
            raise SystemExit(1)

    # --- consolidado (default: True) ---
    consolidated = not cli_args.get("individual", False)
    if "individual" not in cli_args and "start" not in cli_args:
        save_mode = input("¿Guardar como archivo consolidado? [S/n]: ").strip().lower()
        consolidated = save_mode not in ("n", "no")

    return {
        "mode": "period",
        "start_year": start_year,
        "end_year": end_year,
        "consolidated": consolidated,
        "filename": f"{filename}-{start_year}-{end_year}.csv" if consolidated else None,
    }
