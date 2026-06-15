import garua.settings as settings
from garua.utils.html_utils import html_table_to_csv
from garua.utils.ui_console import ui
from garua.models.station import Station
from garua.models.scraping import ScrapingQueryBaseParams
from garua.utils.helpers import build_station_folder_name, check_dir_output_path


class CSVManager:
    """
    Maneja la creación y escritura de archivos CSV
    """

    def __init__(self, station: Station, output_dir: str | None = None):
        self.station = station
        self.station_name = station.name.strip().title().replace(" ", "")
        self.station_folder_name = build_station_folder_name(station)
        self.filename = None
        self.output_dir = check_dir_output_path(output_dir) / self.station_folder_name
        self.csv_data_buffer = []
        self.saved_files: list[str] = []
        self.headers = []
        self.start_line = 1  # Línea inicial para procesar (después de encabezados)

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
                ui.success(
                    f"Datos añadidos al buffer para periodo {option_value}: {len(processed_lines)} filas"
                )
        except Exception as e:
            ui.error(f"Error procesando tabla para {option_value}: {e}")

    def _process_csv_lines(self, csv_content: str) -> list[str]:
        """
        Procesa las líneas CSV añadiendo el periodo
        """
        lines = csv_content.split("\n")
        processed_lines = []

        for line in lines:
            if line.strip():
                processed_lines.append(line)

        return processed_lines

    def _generate_option_value(
        self,
        params: ScrapingQueryBaseParams,
    ) -> str:
        """
        Genera un valor de opción para nombrar archivos basado en el modo y periodo
        """
        if params.mode == "month" and params.year and params.month:
            return f"{params.year:04d}{params.month:02d}"
        elif params.mode == "year" and params.year:
            return f"{params.year:04d}"
        elif params.mode == "period" and params.start_year and params.end_year:
            return f"{params.start_year:04d}-{params.end_year:04d}"
        else:
            return "unknown_period"

    def _generate_filename(self, option_value: str) -> str:
        """
        Genera un nombre de archivo basado en la estación y el periodo
        """
        return f"{self.station_name}-{option_value}.csv"

    def save_individual_file(self, table_html: str, option_value: str) -> str:
        """
        Guarda una tabla individual en un archivo CSV
        """
        filename = self._generate_filename(option_value)
        filepath = self.output_dir / filename

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            csv_content = html_table_to_csv(
                table_html, separator=settings.CSV_SEPARATOR, start_line=self.start_line
            )
            if csv_content:
                content = settings.CSV_SEPARATOR.join(self.headers) + "\n" + csv_content

                filepath.write_text(content, encoding=settings.CSV_ENCODING)

                self.saved_files.append(str(filepath.resolve()))
                ui.success(f"Archivo individual guardado: {filename}")
                return str(filepath)
        except Exception as e:
            ui.error(f"Error guardando archivo {filename}: {e}")

        return ""

    def save_consolidated_file(self, params: ScrapingQueryBaseParams) -> str:
        """
        Guarda todos los datos del buffer en un archivo consolidado
        """
        if not self.csv_data_buffer:
            ui.error("No hay datos en el buffer para guardar")
            return ""

        option_value = self._generate_option_value(params)
        filename = self._generate_filename(option_value)

        filepath = self.output_dir / filename

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)

            filepath.write_text(
                "\n".join(self.csv_data_buffer), encoding=settings.CSV_ENCODING
            )  # Crear archivo vacío

            self.saved_files.append(str(filepath.resolve()))
            ui.success(f"Archivo consolidado guardado: {filename}")
            ui.info(f"Contiene {len(self.csv_data_buffer)} líneas")
            return str(filepath)

        except Exception as e:
            ui.error(f"Error guardando archivo consolidado: {e}")
            return ""

    def clear_buffer(self):
        """
        Limpia el buffer de datos
        """
        self.csv_data_buffer.clear()
