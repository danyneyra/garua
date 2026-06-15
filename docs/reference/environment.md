---
icon: lucide/container
tags:
  - Variables de entorno
  - ENV
---

# Variables de entorno

Garúa puede configurarse con variables de entorno. La mayoría de usuarios solo necesita ajustar la carpeta de salida o la ruta del navegador; las demás opciones son útiles para diagnóstico, scraping avanzado o cambios del portal de SENAMHI.

## Uso común

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `GARUA_OUTPUT_DIR` | `~/Documents/Garua` | Directorio base donde Garúa crea las carpetas `csv`, `logs` y `exports`. Acepta rutas absolutas o rutas con `~`. |
| `GARUA_BROWSER_PATH` | Vacío | Ruta completa a un navegador compatible con Chromium. Si no se define, Garua intenta detectar Chrome, Brave o Microsoft Edge automáticamente. |

Ejemplo en PowerShell:

```powershell
$env:GARUA_OUTPUT_DIR = "D:\datos\garua"
$env:GARUA_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

Ejemplo en Linux o macOS:

```bash
export GARUA_OUTPUT_DIR="$HOME/garua"
export GARUA_BROWSER_PATH="/usr/bin/google-chrome"
```

## Portal SENAMHI

Estas variables cambian la URL y el endpoint que Garúa consulta en el portal de SENAMHI. Úsalas solo si el portal cambia o si necesitas probar un endpoint alternativo.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `GARUA_BASE_URL` | `https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/map_red_graf.php` | URL base del mapa de estaciones de SENAMHI. |
| `GARUA_DATA_ENDPOINT` | `__dt_est_tp_0s3n` | Endpoint usado para consultar datos desde el portal. |

## Años disponibles

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `GARUA_YEAR_MIN` | `2000` | Año mínimo permitido en consultas y descargas. |
| `GARUA_YEAR_MAX` | Año actual | Año máximo permitido. Si no se define, Garua usa el año actual del sistema. |

## Tiempos de espera

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `GARUA_PAGE_TIMEOUT` | `30` | Tiempo máximo, en segundos, para operaciones de página durante scraping. |
| `GARUA_ELEMENT_TIMEOUT` | `10` | Tiempo máximo, en segundos, para esperar elementos del sitio. |
| `GARUA_TIMEOUT_SECONDS` | `30` | Tiempo general de espera usado por flujos internos. |
| `GARUA_POLL_INTERVAL` | `0.5` | Intervalo, en segundos, entre verificaciones repetidas. |

## Ritmo y reintentos de scraping

!!! warning "`GARUA_JITTER_MIN` y `GARUA_JITTER_MAX`"

    Definen una espera aleatoria entre acciones de descarga para reducir el riesgo de bloqueos por solicitudes consecutivas al portal de SENAMHI.

    Usa valores prudentes: tiempos demasiado bajos pueden aumentar la probabilidad de bloqueo, mientras que tiempos muy altos harán que las descargas tarden más.

| Variable | Valor por defecto | Descripción |
| --- | --- | --- |
| `GARUA_JITTER_MIN` | `0.3` | Espera aleatoria mínima, en segundos, entre acciones de scraping. |
| `GARUA_JITTER_MAX` | `0.9` | Espera aleatoria máxima, en segundos, entre acciones de scraping. |
| `GARUA_YEAR_BOUNDARY_SLEEP` | `1.5` | Pausa, en segundos, al cambiar de año durante descargas de periodos largos. |
| `GARUA_MAX_RETRIES` | `2` | Número máximo de reintentos para operaciones recuperables. |
| `GARUA_RETRY_SLEEP` | `5.0` | Pausa, en segundos, antes de reintentar una operación. |


## Notas

- Las variables numéricas usan el valor por defecto si están vacías o tienen un formato inválido.
- `GARUA_OUTPUT_DIR` define el directorio base; Garúa crea dentro las carpetas `csv`, `logs` y `exports`.
- Para cambios permanentes, configura las variables en tu sistema, perfil de terminal o archivo de entorno del cliente MCP que uses.
