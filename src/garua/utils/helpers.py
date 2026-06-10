from pathlib import Path
import re
import unicodedata

from garua.models.station import Station


def fmt(value: float | int | None, decimals: int = 1) -> str:
    """Formatea un valor numérico a una cadena con un número específico de decimales."""
    if value is None:
        return ""
    if isinstance(value, int):
        return str(value)
    return f"{value:.{decimals}f}".rstrip("0").rstrip(".")


def plural(value: float | int, singular: str, plural: str) -> str:
    """Devuelve el singular o el plural de una palabra basado en el valor."""
    return singular if float(value) == 1.0 else plural


def normalize_station_slug(name: str) -> str:
    """Normaliza un nombre de estación para usarlo como slug:
    - Elimina acentos y caracteres diacríticos
    - Convierte a mayúsculas y minúsculas de manera consistente
    - Reemplaza espacios y caracteres especiales por guiones"""
    text = unicodedata.normalize("NFKD", name.strip())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^A-Za-z0-9]+", "", text)
    return text.title()


def parse_station_folder(folder_name: str) -> dict | None:
    """
    Formato oficial:
    {station_slug}_{station_code}_{station_type}_{station_category}

    Ejemplo:
    Huanca_123456_M_CO
    Cajabamba_107008_M_CO
    """
    parts = folder_name.rsplit("_", 3)
    if len(parts) != 4:
        return None

    station_slug, station_code, station_type, station_category = parts

    return {
        "station": station_slug,
        "station_slug": station_slug,
        "station_code": station_code.upper(),
        "station_type": station_type.upper(),
        "station_category": station_category.upper(),
    }


def parse_csv_period(stem: str) -> dict | None:
    """
    Parsea el nombre de un archivo CSV para extraer información sobre el período que cubre. El formato esperado es:
    {station_part}-{year}{month} para archivos mensuales
    Soporta:
    - Cajabamba-202505
    - Cajabamba_202505
    - Cajabamba-2025
    - Cajabamba_2025
    - Cajabamba-2022-2025
    - Cajabamba_2022_2025
    """
    monthly = re.match(r"^(.+)[-_](\d{4})(\d{2})$", stem)
    if monthly:
        return {
            "kind": "month",
            "station_part": monthly.group(1),
            "year": int(monthly.group(2)),
            "month": int(monthly.group(3)),
        }

    period = re.match(r"^(.+)[-_](\d{4})[-_](\d{4})$", stem)
    if period:
        return {
            "kind": "period",
            "station_part": period.group(1),
            "start_year": int(period.group(2)),
            "end_year": int(period.group(3)),
        }

    yearly = re.match(r"^(.+)[-_](\d{4})$", stem)
    if yearly:
        return {
            "kind": "year",
            "station_part": yearly.group(1),
            "year": int(yearly.group(2)),
        }

    return None


def period_covers_request(
    period: dict,
    year: int | None,
    month: int | None,
    include_covering_files: bool = True,
) -> dict:
    """Determina si un período cubre la solicitud y si cubre el mes pedido."""
    covers_period = ""
    covers_requested_period = False
    can_extract_requested_month = False

    if period["kind"] == "month":
        covers_period = f"{period['month']:02d}/{period['year']}"
        matches = True

        if year is not None:
            matches = period["year"] == year

        if month is not None:
            matches = matches and period.get("month") == month

        covers_requested_period = matches
        can_extract_requested_month = False

    elif period["kind"] == "year":
        covers_period = f"año {period['year']}"

        if year is None:
            matches = True
        else:
            matches = period["year"] == year

        if month is not None:
            matches = matches and include_covering_files
            can_extract_requested_month = matches

        covers_requested_period = matches

    elif period["kind"] == "period":
        covers_period = f"{period['start_year']}-{period['end_year']}"

        if year is None:
            matches = True
        else:
            matches = period["start_year"] <= year <= period["end_year"]

        if month is not None:
            matches = matches and include_covering_files
            can_extract_requested_month = matches

        covers_requested_period = matches

    else:
        matches = False

    return {
        "matches": matches,
        "covers_period": covers_period,
        "covers_requested_period": covers_requested_period,
        "can_extract_requested_month": can_extract_requested_month,
    }


def station_folder_matches(
    folder_name: str,
    station_name: str | None = None,
    station_code: str | None = None,
    station_type: str | None = None,
    station_category: str | None = None,
) -> dict | None:
    """Devuelve metadata si la carpeta coincide con los filtros; si no, None."""
    meta = parse_station_folder(folder_name)
    if meta is None:
        return None

    if station_name:
        expected_slug = normalize_station_slug(station_name)
        if meta["station_slug"] != expected_slug:
            return None

    if station_code and meta["station_code"] != station_code.strip().upper():
        return None

    if station_type and meta["station_type"] != station_type.strip().upper():
        return None

    if (
        station_category
        and meta["station_category"] != station_category.strip().upper()
    ):
        return None

    return meta


def build_station_folder_name(station: Station) -> str:
    """
    Construye el nombre de una carpeta de estación a partir de sus componentes.
    El formato oficial es:
    {station_slug}_{station_code}_{station_type}_{station_category}
    Ejemplo:
    Huanca_123456_M_CO
    """
    slug = normalize_station_slug(station.name)
    return f"{slug}_{station.code.strip().upper()}_{station.station_type.strip().upper()}_{station.category.strip().upper()}"


def check_dir_output_path(base_dir: str | None) -> Path:
    """Comprobar que el directorio de salida existe o crearlo si no existe, si el directorio es inválido usar el directorio por defecto. Devuelve la ruta como Path."""
    from garua.settings import CSV_DIR

    try:
        output_path = Path(base_dir) if base_dir else Path(CSV_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    except Exception as _e:
        output_path = Path(CSV_DIR)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia en km entre dos puntos geográficos (fórmula de Haversine)."""
    import math

    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))
