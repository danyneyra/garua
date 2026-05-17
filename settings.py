# SENAMHI Scraper - Configuración Simple

# Configuración básica del proyecto
PROJECT_NAME = "SENAMHI Scraper"
VERSION = "1.0.0"

# URLs
BASE_URL = "https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php"
DATA_ENDPOINT = "__dt_est_tp_0s3n"

# Timeouts (en segundos)
PAGE_TIMEOUT = 30
ELEMENT_TIMEOUT = 10
TIMEOUT_SECONDS = 30
POLL_INTERVAL = 0.5

# Configuración de archivos
CSV_SEPARATOR = ";"
CSV_ENCODING = "utf-8"
OUTPUT_DIR = "output"
CSV_DIR = "output/csv"
LOGS_DIR = "output/logs"
REPORTS_DIR = "output/reports"

# Datos
STATIONS_FILE = "data/estaciones.json"

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
