"""Resources MCP de contexto estable para Garúa.

Los resources exponen información de referencia que el cliente puede leer sin
tener que ejecutar una tool. Las operaciones sobre datos dinámicos (descarga,
resumen y comparación) siguen siendo responsabilidad de las tools.
"""

import json
from datetime import date
from pathlib import Path

from garua import settings
from garua.services.file_delivery import read_file_resource
from garua.models.data_schema import (
    get_expected_columns_count,
    get_headers_for_station_type,
)
from garua.models.station import StationStatus, StationType
from garua.schemas.station import station_response_serializer
from garua.services.downloaded_files import (
    list_downloaded_csv_files,
    serialize_downloaded_files,
)
from garua.services.station import (
    calculate_years_available,
    find_station_by_code,
    station_data_availability,
    stations,
)


def _json_resource(payload: dict) -> str:
    """Serializa un resource de forma estable y legible para clientes MCP."""
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def register_resources(mcp) -> None:
    """Registra los resources de catálogo y esquema de datos."""

    @mcp.resource(
        "garua://files/{file_id}",
        name="generated_csv_file",
        title="Contenido de un CSV de Garúa",
        description="Lee la resource_uri devuelta por una tool o el índice de archivos. Incluye CSV descargados y exportados.",
        mime_type="text/csv",
    )
    def generated_csv_file(file_id: str) -> str:
        return read_file_resource(file_id)

    @mcp.resource(
        "garua://about",
        name="server_about",
        title="Información del servidor Garúa",
        description=(
            "Metadatos de versión, fuente, configuración y capacidades del servidor "
            "MCP de Garúa."
        ),
        mime_type="application/json",
        tags={"about", "metadata", "senamhi"},
    )
    def server_about() -> str:
        """Devuelve información de ejecución y capacidades del servidor."""
        return _json_resource(
            {
                "resource": "garua://about",
                "name": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "source": "SENAMHI",
                "catalog": {
                    "stations": len(stations),
                    "path": settings.STATIONS_FILE_PATH,
                },
                "configuration": {
                    "output_dir": str(settings.OUTPUT_DIR),
                    "csv_dir": str(settings.CSV_DIR),
                    "year_min": settings.YEAR_MIN,
                    "year_max": settings.YEAR_MAX,
                    "csv_separator": settings.CSV_SEPARATOR,
                    "csv_encoding": settings.CSV_ENCODING,
                },
                "capabilities": {
                    "resources": [
                        "garua://about",
                        "garua://catalog/stations",
                        "garua://catalog/stations/{station_code}",
                        "garua://schema/{station_type}/{status}",
                        "garua://data/downloads",
                        "garua://data/files/{station_code}/{filename}",
                        "garua://files/{file_id}",
                    ],
                    "prompts": [
                        "analizar_periodo_estacion",
                        "comparar_periodos_estacion",
                        "auditar_calidad_datos",
                        "seleccionar_estacion",
                    ],
                },
                "generated_at": date.today().isoformat(),
            }
        )

    @mcp.resource(
        "garua://catalog/stations",
        name="stations_catalog",
        title="Catálogo de estaciones SENAMHI",
        description=(
            "Catálogo local de estaciones meteorológicas e hidrológicas del SENAMHI "
            "con ubicación, tipo, estado y disponibilidad histórica."
        ),
        mime_type="application/json",
        tags={"catalog", "stations", "senamhi"},
    )
    def stations_catalog() -> str:
        """Devuelve el catálogo serializado de estaciones."""
        station_items = []
        for station in stations:
            item = station_response_serializer(station)
            item["years_available"] = calculate_years_available(
                station.data_available_since
            )
            station_items.append(item)

        return _json_resource(
            {
                "resource": "garua://catalog/stations",
                "source": "SENAMHI",
                "catalog_version": settings.VERSION,
                "generated_at": date.today().isoformat(),
                "total_stations": len(station_items),
                "stations": station_items,
            }
        )

    @mcp.resource(
        "garua://catalog/stations/{station_code}",
        name="station_catalog_entry",
        title="Ficha de estación SENAMHI",
        description=(
            "Ficha completa de una estación SENAMHI, incluyendo ubicación, "
            "disponibilidad, columnas CSV y URL de consulta."
        ),
        mime_type="application/json",
        tags={"catalog", "stations", "senamhi"},
    )
    def station_catalog_entry(station_code: str) -> str:
        """Devuelve la ficha de una estación identificada por código."""
        station = find_station_by_code(station_code)
        if station is None:
            raise ValueError(f"No se encontró una estación con código: {station_code}")

        item = station_response_serializer(station)
        item["years_available"] = calculate_years_available(
            station.data_available_since
        )
        item["availability"] = station_data_availability(station).model_dump()
        item["csv_schema"] = {
            "headers": station.get_csv_headers(),
            "expected_columns": len(station.get_csv_headers()),
            "separator": settings.CSV_SEPARATOR,
        }

        return _json_resource(
            {
                "resource": f"garua://catalog/stations/{station.code}",
                "source": "SENAMHI",
                "catalog_version": settings.VERSION,
                "station": item,
            }
        )

    @mcp.resource(
        "garua://data/downloads",
        name="downloaded_files_index",
        title="Índice de archivos descargados",
        description=(
            "Metadatos de los CSV descargados localmente por Garúa. No incluye "
            "el contenido de los archivos."
        ),
        mime_type="application/json",
        tags={"data", "files", "csv"},
    )
    def downloaded_files_index() -> str:
        """Devuelve un índice actualizado de los CSV locales."""
        files = serialize_downloaded_files(list_downloaded_csv_files())
        return _json_resource(
            {
                "resource": "garua://data/downloads",
                "directory": str(settings.CSV_DIR),
                "total_files": len(files),
                "files": files,
            }
        )

    @mcp.resource(
        "garua://data/files/{station_code}/{filename}",
        name="downloaded_csv_file",
        title="CSV descargado de una estación",
        description=(
            "Contenido de un CSV descargado por Garúa. Requiere el código de la "
            "estación y el nombre exacto devuelto por garua://data/downloads."
        ),
        mime_type="text/csv",
        tags={"data", "files", "csv"},
    )
    def downloaded_csv_file(station_code: str, filename: str) -> str:
        """Lee un CSV existente, validando que pertenezca a la carpeta configurada."""
        normalized_code = station_code.strip().upper()
        normalized_filename = Path(filename).name

        if normalized_filename != filename or Path(filename).suffix.lower() != ".csv":
            raise ValueError("filename debe ser el nombre simple de un archivo CSV.")

        matches = list_downloaded_csv_files(station_code=normalized_code)
        match = next(
            (item for item in matches if item.filename == normalized_filename), None
        )
        if match is None:
            raise FileNotFoundError(
                f"No se encontró {normalized_filename} para la estación {normalized_code}."
            )

        base_dir = settings.CSV_DIR.resolve()
        file_path = Path(match.path).resolve()
        try:
            file_path.relative_to(base_dir)
        except ValueError as exc:
            raise ValueError(
                "El archivo está fuera de la carpeta CSV configurada."
            ) from exc

        return file_path.read_text(encoding=settings.CSV_ENCODING)

    @mcp.resource(
        "garua://schema/{station_type}/{status}",
        name="station_data_schema",
        title="Diccionario de datos de estación",
        description=(
            "Columnas, unidades y convenciones del CSV según el tipo y estado "
            "de una estación. station_type acepta M o H; status acepta REAL, "
            "DIFERIDO o AUTOMATICA."
        ),
        mime_type="application/json",
        tags={"schema", "csv", "senamhi"},
    )
    def station_data_schema(station_type: str, status: str) -> str:
        """Devuelve el esquema CSV para una combinación válida de estación."""
        normalized_type = station_type.strip().upper()
        normalized_status = status.strip().upper()

        try:
            parsed_type = StationType(normalized_type)
            parsed_status = StationStatus(normalized_status)
        except ValueError as exc:
            raise ValueError(
                "Combinación inválida. station_type debe ser M o H y status debe "
                "ser REAL, DIFERIDO o AUTOMATICA."
            ) from exc

        headers = get_headers_for_station_type(parsed_type, parsed_status)
        columns = [
            {
                "position": index,
                "name": header,
                "description": _column_description(header),
            }
            for index, header in enumerate(headers, start=1)
        ]

        return _json_resource(
            {
                "resource": f"garua://schema/{normalized_type}/{normalized_status}",
                "station_type": normalized_type,
                "station_status": normalized_status,
                "expected_columns": get_expected_columns_count(
                    parsed_type, parsed_status
                ),
                "csv_separator": settings.CSV_SEPARATOR,
                "encoding": settings.CSV_ENCODING,
                "special_values": {
                    "S/D": "Dato sin disponibilidad; no debe interpretarse como cero.",
                    "T": "Traza de precipitación; su valor depende de trace_policy.",
                },
                "columns": columns,
            }
        )


def _column_description(header: str) -> str:
    """Añade una explicación corta a las columnas conocidas del CSV."""
    descriptions = {
        "Año": "Año calendario de la observación.",
        "Mes": "Mes calendario, de 1 a 12.",
        "Día": "Día del mes.",
        "Hora": "Hora de la observación.",
        "Temp. Máx (°C)": "Temperatura máxima diaria en grados Celsius.",
        "Temp. Mín (°C)": "Temperatura mínima diaria en grados Celsius.",
        "Temperatura (°C)": "Temperatura observada en grados Celsius.",
        "Humedad (%)": "Humedad relativa porcentual.",
        "Precipitación (mm)": "Precipitación acumulada en milímetros.",
        "Precipitación (mm/hora)": "Precipitación observada por hora en milímetros.",
        "Dir. Viento (°)": "Dirección del viento en grados.",
        "Vel. Viento (m/s)": "Velocidad del viento en metros por segundo.",
        "Nivel del río (m) 06": "Nivel del río en metros, observado a las 06:00.",
        "Nivel del río (m) 10": "Nivel del río en metros, observado a las 10:00.",
        "Nivel del río (m) 14": "Nivel del río en metros, observado a las 14:00.",
        "Nivel del río (m) 18": "Nivel del río en metros, observado a las 18:00.",
        "Nivel del río (m)": "Nivel del río en metros.",
    }
    return descriptions.get(header, "Columna de datos del SENAMHI.")
