import garua.settings as settings
from garua.models import Station
import json
from urllib.parse import urlencode
from typing import List, Optional
import requests
from garua.utils.html_utils import extract_station_info


def load_stations(path: str) -> list[Station]:
    with open(path, "r", encoding=settings.CSV_ENCODING) as file:
        data_json = json.load(file)
    return [Station(**item) for item in data_json]


stations = load_stations(settings.STATIONS_FILE_PATH)


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
    """Realiza scraping para obtener los datos de una estación por su código interno (campo 'cod') desde SENAMHI"""
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
        print(station_info)
        if station_info:
            for key, value in station_info.items():
                setattr(station, key, value)
            return station
        else:
            print(
                f"{settings.ERROR} No se pudieron extraer los datos para estación {code} desde {url_scraping}"
            )
            return None
    else:
        print(
            f"{settings.ERROR} Error al obtener datos para estación {code} desde {url_scraping}: HTTP {response.status_code}"
        )
        return None


def fetch_station_by_code(code: str) -> Optional[Station]:
    """Busca una estación por su código interno (campo 'cod') desde API Garua"""
    code = code.strip().upper()
    for station in stations:
        if (
            station.code == code
            or station.legacy_code == code
            or (station.frontend_code and station.frontend_code.upper() == code)
        ):
            return station
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


def create_station_url(station: Station) -> str:
    """Crea la URL para acceder a los datos de una estación"""
    url_base = settings.BASE_URL
    params = {
        "cod": station.code,
        "estado": station.status,
        "tipo_esta": station.station_type,
        "cate": station.category,
        "cod_old": station.legacy_code,
    }
    return f"{url_base}?{urlencode(params)}"
