import settings
from src.models import Station
import json
from urllib.parse import urlencode
from typing import List, Optional


def load_stations(path: str) -> list[Station]:
    with open(path, "r", encoding=settings.CSV_ENCODING) as file:
        data_json = json.load(file)
    return [Station(**item) for item in data_json]


stations = load_stations(settings.STATIONS_FILE)


def find_station_by_code(code: str) -> Optional[Station]:
    """Busca una estación por su código interno (campo 'cod')"""
    code = code.strip().upper()
    for est in stations:
        if est.code == code:
            return est
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
    station_type_map = {"M": "METEOROLOGICA", "H": "HIDROLOGICA"}

    # Intento 1: código exacto
    exact = find_station_by_code(query)
    if exact:
        matches = [exact]
    else:
        matches = search_stations_by_name(query)

    if not matches:
        import settings

        print(f"{settings.ERROR} No se encontró ninguna estación con '{query}'.")
        return

    print(
        f"\n{'#':<4} {'NOMBRE':<30} {'TIPO':<14} {'CAT':<6} {'ESTADO':<10} {'CÓDIGO'}"
    )
    print("-" * 75)
    for i, s in enumerate(matches, 1):
        tipo = station_type_map.get(s.station_type, "DESCONOCIDO")
        print(f"{i:<4} {s.name:<30} {tipo:<14} {s.category:<6} {s.status:<10} {s.code}")
    print(f"\nTotal: {len(matches)} estación(es) encontrada(s).")


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
