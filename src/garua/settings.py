# Garua - Configuración Simple
import os
from importlib.resources import files
from pathlib import Path
from datetime import datetime

# Configuración básica del proyecto
PROJECT_NAME = "Garua"
VERSION = "0.30.0"

# URLs
BASE_URL = os.getenv(
    "GARUA_BASE_URL",
    "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php",
)
DATA_ENDPOINT = os.getenv("GARUA_DATA_ENDPOINT", "__dt_est_tp_0s3n")

# Timeouts (en segundos)
PAGE_TIMEOUT = 30
ELEMENT_TIMEOUT = 10
TIMEOUT_SECONDS = 30
POLL_INTERVAL = 0.5

# Configuración Csv
CSV_SEPARATOR = ";"
CSV_ENCODING = "utf-8"

# Datos internos del paquete
STATIONS_FILE = files("garua").joinpath("data", "estaciones.json")
STATIONS_FILE_PATH = str(STATIONS_FILE)

# Directorios de salida configurable
DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "Garua"

OUTPUT_DIR = Path(os.getenv("GARUA_OUTPUT_DIR", DEFAULT_OUTPUT_DIR))
CSV_DIR = OUTPUT_DIR / "csv"
LOGS_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Años permitidos para scraping (configurables vía variables de entorno)
YEAR_MIN = int(os.getenv("GARUA_YEAR_MIN", 2000))
YEAR_MAX = int(
    os.getenv("GARUA_YEAR_MAX", datetime.now().year)
)  # Permitir hasta el año actual para evitar errores de scraping en años futuros

# Mensajes de estado
SUCCESS = "✅"
ERROR = "❌"
PROCESSING = "🔄"
INFO = "ℹ️"
WARNING = "⚠️"

# Rate limiting — controla la velocidad de las peticiones para evitar detección
# Pausa aleatoria entre cada mes (simula comportamiento humano)
JITTER_MIN = 0.3  # segundos mínimos de espera entre meses (0.4 original)
JITTER_MAX = 0.9  # segundos máximos de espera entre meses (1.2 original)
# Pausa extra al cambiar de año (reduce el riesgo de ráfagas detectables)
YEAR_BOUNDARY_SLEEP = 1.5  # segundos (aumentado de 2.0 a 3.0 para mayor seguridad)

# Reintentos — ante fallos transitorios (Turnstile, timeout de red, etc.)
MAX_RETRIES = 2  # número de reintentos antes de marcar la opción como fallida
RETRY_SLEEP = 5.0  # segundos de espera entre reintentos


def ensure_output_dirs() -> None:
    for directory in (OUTPUT_DIR, CSV_DIR, LOGS_DIR, REPORTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
