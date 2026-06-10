# 📋 Changelog - Garúa

## [0.30.0] - 2026-05-30

### 🎉 Primera Versión Pública

**Renombramiento del Proyecto:**
- Cambio de nombre de `senamhi-scraper` a `garua`
- Nueva identidad de marca conectada con [garua.app](https://garua.app)
- Garúa: llovizna fina característica del clima peruano 🌧️🇵🇪

**Características Principales:**

### 🤖 Servidor MCP
- 16 herramientas organizadas en 4 categorías
- Compatible con VS Code, Claude Desktop, Cursor
- Protocolo stdio para comunicación eficiente

### 🔍 Búsqueda y Filtrado (7 tools)
- `search_stations` - Búsqueda por nombre
- `get_station_info` - Información detallada
- `find_stations_near` - Búsqueda geográfica
- `filter_stations_by_location` - Filtro por ubicación
- `filter_stations_by_altitude` - Filtro por altitud
- `check_data_availability` - Disponibilidad de datos
- `filter_stations_advanced` - Filtro multi-criterio

### 📊 Estadísticas (5 tools)
- `stations_count` - Conteo total
- `stations_summary` - Resumen por tipo
- `get_all_stations` - Lista completa
- `get_departments_summary` - Estadísticas departamentales
- `get_location_hierarchy` - Jerarquía geográfica

### 📁 Gestión de Archivos (3 tools)
- `list_downloaded_files` - Listado con filtros opcionales
- `read_csv_preview` - Vista previa de datos con filtrado
- `extract_month_from_csv` - Extracción de periodos específicos

### ⬇️ Descarga (1 tool)
- `scrape_station_data` - Descarga desde SENAMHI con bypass Cloudflare Turnstile

**Tecnologías:**
- Python 3.11+
- FastMCP 3.3.1 (protocolo MCP)
- Zendriver 0.7.2 (bypass Cloudflare Turnstile automático)
- BeautifulSoup4 4.12.3 (parsing HTML)
- Pydantic 2.10.6 (validación de datos)

**Instalación:**
```bash
pip install garua
```

**Uso:**

*CLI (Línea de comandos):*
```bash
garua --help
```

*MCP con VS Code + Copilot:*
```
@garua busca estaciones en Lima
@garua descarga datos de febrero 2025
```

*MCP con Claude Desktop:*
```
¿Qué estaciones hay disponibles en Cajamarca?
Descarga datos de enero 2025 de la estación Cabana
```

**Documentación:**
- [INSTALL.md](INSTALL.md) - Guía de instalación por cliente MCP
- [MCP_EXPLAINED.md](MCP_EXPLAINED.md) - Protocolo MCP explicado
- [DISTRIBUTION.md](DISTRIBUTION.md) - Guía de distribución
- [PUBLISHING.md](PUBLISHING.md) - Publicación en PyPI

**Enlaces:**
- 🌐 Website: https://garua.app
- 📦 PyPI: https://pypi.org/project/garua/
- 🔗 GitHub: https://github.com/danyneyra/senamhi-scraper
- 🐛 Issues: https://github.com/danyneyra/senamhi-scraper/issues

---

## Historia del Proyecto

Este proyecto anteriormente se llamaba `senamhi-scraper`. La transición a `garua` marca el inicio de la distribución pública y la reconexión con la plataforma web [garua.app](https://garua.app).

**Evolución:**
- **2024**: Desarrollo inicial como `senamhi-scraper`
- **2025**: Implementación de bypass Cloudflare Turnstile con Zendriver
- **2026**: Refactorización modular y lanzamiento como servidor MCP
- **2026-05-24**: Renombramiento a `garua` v0.30.0 y primera versión pública

**¿Por qué 0.30.0?**
- Versión de la suerte elegida por el autor 🍀
- Marca el comienzo de una nueva etapa del proyecto
