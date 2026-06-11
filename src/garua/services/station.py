import json
from datetime import date
from typing import List, Optional
from urllib.parse import urlencode

import requests

import garua.settings as settings
from garua.models.station import (
    Station,
    StationDataAvailability,
    StationDataAvailabilityResponse,
)
from garua.schemas.station import station_response_serializer
from garua.utils.html_utils import extract_station_info


def load_stations(path: str) -> list[Station]:
    with open(path, "r", encoding=settings.CSV_ENCODING) as file:
        data_json = json.load(file)
    return [Station(**item) for item in data_json]


stations = load_stations(settings.STATIONS_FILE_PATH)


def calculate_years_available(data_available_since: str | None) -> int | None:
    """Calcula años completos de datos disponibles desde una fecha YYYY-MM o YYYY."""
    if not data_available_since:
        return None

    try:
        parts = data_available_since.split("-")
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1

        current = date.today()
        years = current.year - year
        if current.month < month:
            years -= 1

        return max(0, years)
    except (ValueError, IndexError):
        return None


def data_available_year(data_available_since: str | None) -> int | None:
    """Extrae el año inicial de disponibilidad de datos."""
    if not data_available_since:
        return None

    try:
        return int(data_available_since.split("-")[0])
    except (ValueError, IndexError):
        return None


def station_data_availability(station: Station) -> StationDataAvailability:
    """Construye la respuesta de disponibilidad para una estación puntual."""
    return StationDataAvailability(
        name=station.name,
        code=station.code,
        data_available_since=station.data_available_since,
        years_available=calculate_years_available(station.data_available_since),
    )


def station_matches_availability_filters(
    station: Station,
    before_year: int | None = None,
    after_year: int | None = None,
) -> bool:
    """Indica si una estación cumple filtros de disponibilidad histórica."""
    year = data_available_year(station.data_available_since)
    if year is None:
        return False

    if before_year is not None and year >= before_year:
        return False
    if after_year is not None and year <= after_year:
        return False

    return True


def station_availability_summary(station: Station) -> dict:
    """Serializa una estación con sus años de disponibilidad calculados."""
    return {
        **station_response_serializer(station),
        "years_available": calculate_years_available(station.data_available_since),
    }


def filter_stations_by_data_availability(
    before_year: int | None = None,
    after_year: int | None = None,
    station_list: list[Station] | None = None,
) -> list[StationDataAvailability]:
    """Filtra estaciones por año inicial de disponibilidad de datos."""
    source = station_list if station_list is not None else stations
    results = [
        StationDataAvailability(**station_availability_summary(station))
        for station in source
        if station_matches_availability_filters(station, before_year, after_year)
    ]
    results.sort(key=lambda item: item.data_available_since or "9999")
    return results


def check_data_availability(
    station_code: str | None = None,
    before_year: int | None = None,
    after_year: int | None = None,
) -> StationDataAvailabilityResponse | None:
    """Consulta disponibilidad de datos para una estación o un conjunto filtrado."""
    if station_code:
        station = find_station_by_code(station_code)
        if not station:
            return None
        return StationDataAvailabilityResponse(
            station=station_data_availability(station)
        )

    return StationDataAvailabilityResponse(
        stations=filter_stations_by_data_availability(
            before_year=before_year,
            after_year=after_year,
        )
    )


def build_scraping_url_for_station(station: Station) -> str:
    """Construye la URL para acceder a los datos de una estación específica"""
    url_base = settings.BASE_URL
    params = {
        "cod": station.code,
        "estado": station.status,
        "tipo_esta": station.station_type,
        "cate": station.category,
        "cod_old": station.legacy_code,
    }
    return f"{url_base}?{urlencode(params)}"


def scraping_station_by_code(code: str) -> Optional[Station]:
    """Realiza scraping para obtener los datos de una estación por su código interno (campo 'cod') desde SENAMHI
    NOTA: Por el momento solo se usa para testing
    """
    code = code.strip().upper()
    station = None
    for est in stations:
        if (
            est.code == code
            or est.legacy_code == code
            or (est.frontend_code and est.frontend_code.upper() == code)
        ):
            station = est
            break

    if station is None:
        return None

    url_scraping = build_scraping_url_for_station(station)

    # Realizar fetch GET a url_scraping y parsear la respuesta para obtener los datos actualizados de la estación
    # Si la respuesta es exitosa y se pueden extraer los datos, actualizar el objeto, se espera HTML con la tabla de datos, parsear y llenar los campos de la estación (data_available_since, etc.)
    # Si ocurre un error (timeout, datos no encontrados, etc.), retornar None o manejar según corresponda

    response = requests.get(url_scraping, timeout=settings.TIMEOUT_SECONDS)
    if response.status_code == 200:
        station_info = extract_station_info(response.text)
        if station_info:
            for key, value in station_info.items():
                setattr(station, key, value)
            return station
        else:
            return None
    else:
        return None


def find_station_by_code(code: str) -> Optional[Station]:
    """Busca una estación por su código interno (campo 'cod') desde la lista precargada de estaciones"""
    code = code.strip().upper()
    for station in stations:
        if (
            station.code == code
            or station.legacy_code == code
            or (station.frontend_code and station.frontend_code.upper() == code)
        ):
            return station
    return None


def search_stations_by_name(query: str) -> List[Station]:
    """
    Busca estaciones por nombre (coincidencia parcial, insensible a mayúsculas/tildes).
    Retorna la lista ordenada: primero las que empiezan con el query, luego las que lo contienen.
    """
    query_upper = query.strip().upper()
    if not query_upper:
        return []
    starts_with = [s for s in stations if s.name.upper().startswith(query_upper)]
    contains = [
        s for s in stations if query_upper in s.name.upper() and s not in starts_with
    ]
    return starts_with + contains


def search_and_print_stations(query: str) -> None:
    """
    Busca estaciones por código exacto o nombre parcial e imprime los resultados
    en formato tabular. Pensado para el comando --search del CLI.
    """
    from garua.utils.ui_console import ui

    # Intento 1: código exacto
    exact = find_station_by_code(query)
    if exact:
        matches = [exact]
    else:
        matches = search_stations_by_name(query)

    ui.print_search_results(matches, query)


def get_headers_for_station(station: Station) -> List[str]:
    """Obtiene los headers CSV apropiados para una estación"""
    return station.get_csv_headers()
