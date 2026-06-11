"""Configuración central de Garúa."""

import os
from datetime import datetime
from importlib.resources import files
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    """Lee una variable de entorno entera con fallback seguro."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    """Lee una variable de entorno decimal con fallback seguro."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return float(raw_value)
    except ValueError:
        return default


def _env_path(name: str, default: Path) -> Path:
    """Lee una ruta desde variable de entorno con fallback."""
    raw_value = os.getenv(name)
    if not raw_value:
        return default
    return Path(raw_value).expanduser()


# Metadata del proyecto
PROJECT_NAME = "Garua"
VERSION = "0.30.0"


# Recursos internos del paquete
STATIONS_FILE = files("garua").joinpath("data", "estaciones.json")
STATIONS_FILE_PATH = str(STATIONS_FILE)


# Endpoints SENAMHI
BASE_URL = os.getenv(
    "GARUA_BASE_URL",
    "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php",
)
DATA_ENDPOINT = os.getenv("GARUA_DATA_ENDPOINT", "__dt_est_tp_0s3n")


# Directorios de salida configurable
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "Garua"

OUTPUT_DIR = _env_path("GARUA_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)
CSV_DIR = OUTPUT_DIR / "csv"
LOGS_DIR = OUTPUT_DIR / "logs"
EXPORTS_DIR = OUTPUT_DIR / "exports"

# Configuración CSV
CSV_SEPARATOR = ";"
CSV_ENCODING = "utf-8"


# Límites y tiempos de scraping
YEAR_MIN = _env_int("GARUA_YEAR_MIN", 2000)
YEAR_MAX = _env_int("GARUA_YEAR_MAX", datetime.now().year)

PAGE_TIMEOUT = _env_int("GARUA_PAGE_TIMEOUT", 30)
ELEMENT_TIMEOUT = _env_int("GARUA_ELEMENT_TIMEOUT", 10)
TIMEOUT_SECONDS = _env_int("GARUA_TIMEOUT_SECONDS", 30)
POLL_INTERVAL = _env_float("GARUA_POLL_INTERVAL", 0.5)


# Ritmo de scraping y reintentos
JITTER_MIN = _env_float("GARUA_JITTER_MIN", 0.3)
JITTER_MAX = _env_float("GARUA_JITTER_MAX", 0.9)
YEAR_BOUNDARY_SLEEP = _env_float("GARUA_YEAR_BOUNDARY_SLEEP", 1.5)

MAX_RETRIES = _env_int("GARUA_MAX_RETRIES", 2)
RETRY_SLEEP = _env_float("GARUA_RETRY_SLEEP", 5.0)


# Símbolos de consola
SUCCESS = "✅"
ERROR = "❌"
PROCESSING = "🔄"
INFO = "ℹ️"
WARNING = "⚠️"


def ensure_output_dirs() -> None:
    """Crea los directorios de salida configurados si no existen."""
    for directory in (OUTPUT_DIR, CSV_DIR, LOGS_DIR, EXPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
