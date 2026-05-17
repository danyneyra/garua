# 🌦️ SENAMHI Data Scraper

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Zendriver](https://img.shields.io/badge/Zendriver-Latest-orange.svg)](https://zendriver.dev/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-green.svg)](https://pydantic.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Automatiza la descarga de datos meteorológicos históricos del SENAMHI con bypass automático de Cloudflare Turnstile**

Este proyecto permite **descargar datos hidrometeorológicos históricos** en archivos CSV organizados por **Mes, Año o Rangos de años** desde el sitio web oficial del **SENAMHI** (Servicio Nacional de Meteorología e Hidrología del Perú). Utiliza tecnología avanzada con `Zendriver` para superar automáticamente las protecciones de Cloudflare Turnstile.

## 📚 Tabla de Contenidos

- [✨ Características](#-características)
- [🎯 Modos de Consulta](#-modos-de-consulta)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🚀 Instalación](#-instalación)
- [⚡ Uso Rápido](#-uso-rápido)
- [🖥️ Interfaz de Línea de Comandos (CLI)](#️-interfaz-de-línea-de-comandos-cli)
- [💡 Ejemplos de Uso](#-ejemplos-de-uso)
- [🔄 Flujo de Ejecución](#-flujo-de-ejecución)
- [🛠️ Configuración Avanzada](#️-configuración-avanzada)
- [🔧 Troubleshooting](#-troubleshooting)
- [⚠️ Limitaciones](#️-limitaciones)
- [📄 Licencia](#-licencia)

## ✨ Características

### 🚀 Funcionalidades Principales
- 🛡️ **Bypass automático de Cloudflare Turnstile** - Acceso garantizado sin intervención manual
- ⚡ **Intercepción de red via CDP** - Captura directa de respuestas POST sin esperar recarga visual, lo que hace el scraping significativamente más rápido
- 🔄 **Tres modos de consulta flexibles** - Month, Year, Period con opciones avanzadas
- 🔍 **Búsqueda de estaciones inteligente** - Busca por código exacto o por nombre parcial desde el CLI o en la interfaz interactiva
- 📊 **Exportación inteligente** - CSV organizados con nombres descriptivos
- 🖥️ **CLI con argumentos** - Ejecuta consultas completas en una sola línea sin pasar por el flujo interactivo
- 🔁 **Reintentos automáticos** - Ante fallos transitorios (Turnstile, timeout de red) reintenta automáticamente
- 📋 **Modelos Pydantic tipados** - Validación automática de datos
- 🔧 **Configuración centralizada** - Personalización fácil en `settings.py`


## 🎯 Modos de Consulta

### 1. Modo Month (Mensual)
Descarga datos de un mes específico.
- **Entrada**: Año y mes
- **Salida**: Un archivo CSV individual
- **Ejemplo**: `TICAPAMPA-202409.csv`

### 2. Modo Year (Anual)
Descarga todos los meses de un año completo.
- **Entrada**: Año
- **Opciones**: Archivos individuales o consolidado
- **Salida**: 12 archivos separados o 1 archivo consolidado
- **Ejemplo**: `TICAPAMPA-2024.csv`

### 3. Modo Period (Periodo)
Descarga datos de múltiples años.
- **Entrada**: Año inicial y final
- **Opciones**: Archivos individuales o consolidado
- **Salida**: Múltiples archivos o 1 archivo consolidado
- **Ejemplo**: `TICAPAMPA-2020-2025.csv`

## 📁 Estructura del Proyecto

```
senamhi_scraper/
├── 📄 main.py                    # 🚀 Script principal ejecutable
├── 📄 run_scraper.py            # 🎮 Interfaz interactiva (recomendado)
├── ⚙️ settings.py               # ✨ Configuración centralizada
├── 📋 requirements.txt          # 📦 Dependencias del proyecto
├── 📖 README.md                # 📚 Documentación completa
│
├── 📁 src/                      # Código fuente modular
│   ├── 🚨 exceptions.py        # Excepciones personalizadas
│   ├── 🎯 query_handler.py     # Manejador principal de consultas
│   ├── 🌐 html_utils.py        # Utilidades para parsing HTML
│   ├── 🏭 station_service.py   # Servicio de gestión de estaciones
│   └── 📁 models/              # 🏛️ Modelos de datos con Pydantic
│       ├── 📄 __init__.py      
│       ├── 🏢 station.py       # Modelo Station + validaciones
│       ├── 🔍 query.py         # Modelos de consultas y respuestas
│       └── 📊 data_schema.py   # Esquemas CSV y validadores
│
├── 📁 data/                     # 💾 Datos del proyecto
│   └── 🗄️ estaciones.json      # Base de datos de estaciones
│
├── 📁 output/                   # 📈 Archivos generados
│   └── 📊 *.csv                # Datos meteorológicos descargados
│                               # Estructura: ESTACION-YYYYMM.csv
│
└── 📁 .venv/                    # 🐍 Entorno virtual (opcional)
    └── 📦 [dependencias aisladas]
```

## 🚀 Instalación

### Requisitos
- **Python 3.11+** (recomendado 3.13+)
- **zendriver** - Automatización web avanzada
- **beautifulsoup4** - Parsing HTML
- **pydantic** - Validación de datos y modelos tipados


### 1. Clonar repositorio
```bash
git clone https://github.com/danyneyra/senamhi-scraper.git
cd senamhi-scraper
```

### 2. Crea un entorno virtual
```bash
python -m venv .venv
```

### 3. Ingresar en el entorno virtual
```bash
.venv\Scripts\activate        # En Windows
source .venv/bin/activate     # En Linux/macOS
```

### 4. Instalar librerías desde requirements.txt (Recomendado)
```bash
pip install -r requirements.txt
```


## ⚡ Uso Rápido

### Método 1: CLI (Recomendado para consultas rápidas)
```bash
# Búsqueda de estación por nombre
python main.py --search SIHUAS

# Consulta completa de un mes
python main.py -s 108047 -m month -y 2024 --month 9

# Consulta de año completo (consolidado)
python main.py -s 108047 -m year -y 2024

# Consulta de periodo con archivos individuales
python main.py -s 108047 -m period --start 2020 --end 2025 --individual
```

### Método 2: Modo Interactivo
```bash
python main.py
# ó
python run_scraper.py
```

## 🖥️ Interfaz de Línea de Comandos (CLI)

El script `main.py` acepta argumentos para ejecutar consultas sin pasar por el flujo interactivo. Todos los parámetros son opcionales: los que no se provean se preguntarán de forma interactiva.

### Referencia de argumentos

| Argumento | Corto | Tipo | Descripción |
|---|---|---|---|
| `--search QUERY` | `-S` | `str` | Busca estaciones por código exacto o nombre parcial y las lista. **No inicia el scraping.** |
| `--station CÓDIGO` | `-s` | `str` | Código interno de la estación (ej: `108047`). |
| `--mode MODO` | `-m` | `str` | Modo de consulta: `month` \| `year` \| `period`. |
| `--year AÑO` | `-y` | `int` | Año (requerido para `month` y `year`). |
| `--month MES` | | `int` | Mes 1-12 (solo para `--mode month`). |
| `--start AÑO` | | `int` | Año inicial (solo para `--mode period`). |
| `--end AÑO` | | `int` | Año final (solo para `--mode period`). |
| `--individual` | `-i` | flag | Genera un CSV por cada mes en lugar de uno consolidado. |
| `--output DIR` | `-o` | `str` | Directorio de salida (por defecto: el definido en `settings.py`). |

### 🔍 Búsqueda de Estaciones

La búsqueda funciona tanto por **código exacto** como por **nombre parcial** (insensible a mayúsculas):

```bash
# Búsqueda por nombre parcial
python main.py --search SIHUAS
python main.py --search "san marcos"

# Búsqueda por código exacto
python main.py --search 108047

# Salida de ejemplo:
# #    NOMBRE                         TIPO           CAT    ESTADO     CÓDIGO
# ---------------------------------------------------------------------------
# 1    SIHUAS                         METEOROLOGICA  M      ACTIVA     108047
# Total: 1 estación(es) encontrada(s).
```

También puedes buscar estaciones en el modo interactivo: cuando el scraper pide el código de estación puedes ingresar el nombre y se mostrarán los resultados coincidentes.

## 💡 Ejemplos de Uso

### Via CLI

```bash
# Mes específico
python main.py -s 108047 -m month -y 2024 --month 9
# → output/csv/SIHUAS/SIHUAS-202409.csv

# Año completo consolidado
python main.py -s 108047 -m year -y 2024
# → output/csv/SIHUAS/SIHUAS-2024.csv

# Año completo con archivos por mes
python main.py -s 108047 -m year -y 2024 --individual
# → output/csv/SIHUAS/SIHUAS-202401.csv, SIHUAS-202402.csv, ...

# Periodo consolidado
python main.py -s 108047 -m period --start 2020 --end 2025
# → output/csv/SIHUAS/SIHUAS-2020-2025.csv
```

### Via Modo Interactivo

```
Modo: 1 (Month)  → Pregunta año y mes
Modo: 2 (Year)   → Pregunta año y si desea consolidado
Modo: 3 (Period) → Pregunta año inicial, año final y si desea consolidado
```

### 📊 Casos de Uso Comunes

#### 🌡️ Análisis de Tendencias Climáticas
```bash
# Descargar últimos 10 años para análisis de tendencias
python main.py -s 108047 -m period --start 2015 --end 2024
# Resultado: Archivo único con datos históricos completos
```

#### 📈 Estudios de Variabilidad Estacional
```bash
# Descargar año completo en archivos separados por mes
python main.py -s 108047 -m year -y 2024 --individual
# Resultado: 12 archivos CSV (uno por mes)
```

#### 🔍 Verificación de Datos Específicos
```bash
# Consultar un mes particular para validación
python main.py -s 108047 -m month -y 2024 --month 9
# Resultado: Datos específicos de septiembre 2024
```

## 📋 Formato de Salida

### 📄 Archivos Individuales
Cada archivo contiene los datos del mes correspondiente:
- **Formato**: CSV con separador `;`
- **Encoding**: UTF-8
- **Nomenclatura**: `NOMBRE_ESTACION-YYYYMM.csv`
- **Ejemplo**: `TICAPAMPA-202409.csv`

### 📦 Archivos Consolidados
Consolida toda la información en un solo archivo:
- **Formato**: CSV con separador `;`
- **Encoding**: UTF-8 
- **Nomenclatura**: `NOMBRE_ESTACION-YYYY.csv` o `CODIGO_ESTACION-YYYY-YYYY.csv`
- **Contenido**: Datos ordenados cronológicamente


## 🔄 Flujo de Ejecución

1. **Inicialización**: Configuración del navegador y parámetros
2. **Navegación**: Acceso a la página y resolución de Cloudflare
3. **Configuración CDP**: Habilitación del monitoreo de red para interceptar respuestas POST
4. **Preparación**: Clic en la pestaña de tabla y descarte del POST inicial de carga
5. **Extracción**: Obtención de opciones del select `CBOFiltro`
6. **Filtrado**: Aplicación de criterios según modo de consulta (month / year / period)
7. **Procesamiento**: Por cada opción (mes), se cambia el select y se captura directamente la respuesta del endpoint via CDP — sin esperar recarga visual del DOM
8. **Reintentos**: Si una opción falla, se reintenta hasta `MAX_RETRIES` veces con pausa de `RETRY_SLEEP` segundos
9. **Rate limiting**: Pausa aleatoria entre meses (`JITTER_MIN`–`JITTER_MAX` s) y pausa extra al cambiar de año (`YEAR_BOUNDARY_SLEEP` s)
10. **Exportación**: Generación de archivos CSV individuales o consolidados
11. **Finalización**: Limpieza y cierre del navegador

## 🔧 Troubleshooting

### Errores Comunes

#### 🚫 "Select CBOFiltro no encontrado"
```bash
# Soluciones:
- Verificar conexión a internet estable
- Confirmar que la estación tiene datos disponibles
- Verificar código de estación en data/estaciones.json (usa --search para buscarlo)
- Aumentar timeout en settings.py: PAGE_TIMEOUT = 45
- Verificar que Cloudflare se resolvió correctamente
```

#### 🚫 "No se encontró table#dataTable en la respuesta del endpoint"
```bash
# Soluciones:
- Verificar que el año/periodo existe en los datos de la estación
- Probar con un rango de fechas más amplio
- Revisar si SENAMHI cambió la estructura del sitio
```

#### 🚫 "No se encontró ninguna estación con el código '...'"
```bash
# Solución: busca el código correcto con --search
python main.py --search NOMBRE_ESTACION
```

#### 🚫 Timeout esperando respuesta CDP
```bash
# Soluciones:
- Aumentar TIMEOUT_SECONDS en settings.py (ej: 45)
- Verificar estabilidad de la conexión a internet
- El servidor de SENAMHI puede estar lento; aumentar RETRY_SLEEP = 10.0
```

#### 🚫 Errores de Validación Pydantic
```bash
# Solución: Verificar datos de entrada según los modelos definidos en src/models/
```

## ⚠️ Limitaciones

- **Dependencia externa**: Sujeto a cambios en el sitio web de SENAMHI
- **Conexión requerida**: Necesita internet estable durante la operación
- **Navegador activo**: El navegador debe permanecer abierto durante el scraping
- **Cloudflare**: Puede requerir verificación adicional ocasionalmente
- **Rate limiting**: Respetar los límites del servidor de SENAMHI

## 🛠️ Configuración Avanzada

Todos los parámetros de comportamiento se centralizan en `settings.py`:

```python
# ── Timeouts ──────────────────────────────────────────────────────────────────
PAGE_TIMEOUT = 30        # Segundos de espera máxima para la carga de página
ELEMENT_TIMEOUT = 10     # Segundos de espera para localizar elementos en el DOM
TIMEOUT_SECONDS = 30     # Timeout general para captura de respuestas POST via CDP

# ── Rate limiting (simula comportamiento humano, reduce riesgo de detección) ──
JITTER_MIN = 0.3         # Segundos mínimos de pausa entre cada mes consultado
JITTER_MAX = 0.9         # Segundos máximos de pausa entre cada mes consultado
YEAR_BOUNDARY_SLEEP = 1.5  # Pausa extra (segundos) al cambiar de año

# ── Reintentos ante fallos transitorios ───────────────────────────────────────
MAX_RETRIES = 2          # Número de reintentos antes de marcar una opción como fallida
RETRY_SLEEP = 5.0        # Segundos de espera entre reintentos

# ── Archivos de salida ────────────────────────────────────────────────────────
CSV_SEPARATOR = ";"      # Separador de columnas en los CSV generados
CSV_ENCODING = "utf-8"   # Encoding de los archivos CSV
CSV_DIR = "output/csv"   # Directorio raíz de salida
```

### Ajuste de velocidad vs. seguridad

| Configuración | Valores conservadores | Valores agresivos |
|---|---|---|
| `JITTER_MIN` / `JITTER_MAX` | `1.0` / `2.5` | `0.1` / `0.5` |
| `YEAR_BOUNDARY_SLEEP` | `3.0` | `0.5` |
| `MAX_RETRIES` | `3` | `1` |

## 📝 Notas adicionales

- **Git:** Para clonar el repositorio necesitas tener [Git](https://git-scm.com/) instalado en tu sistema. Puedes verificarlo ejecutando `git --version` en la terminal.

- **Activación del entorno virtual en Windows:**  
  Si al ejecutar `.venv\Scripts\activate` en PowerShell ves el error:

  ```
  Activate.ps1 no se puede cargar porque la ejecución de scripts está deshabilitada en este sistema.
  ```

  Debes permitir la ejecución de scripts. Abre PowerShell como administrador y ejecuta:

  ```powershell
  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

  Luego intenta activar el entorno virtual nuevamente.

- **Consideraciones adicionales:**
  - Asegúrate de tener conexión a internet para instalar dependencias y navegadores.
  - Si usas otro shell (como CMD), la activación se realiza con `.venv\Scripts\activate.bat`.
  - Si tienes problemas con permisos, ejecuta la terminal como administrador.
  - Revisa que tu versión de Python sea 3.11 o superior (`python --version`).


## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la **Licencia MIT**.

```
MIT License - Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

##

<div align="center">
Desarollado con 💜 para la comunidad meteorológica peruana. <br/>
Facilitando el acceso a datos hidrometeorológicos históricos del SENAMHI
</div>
