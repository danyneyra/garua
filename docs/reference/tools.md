---
icon: lucide/hammer
tags:
  - Tools MCP
  - Referencia
---

# Referencia de tools MCP

Esta referencia se genera desde los docstrings y las firmas de `src/garua/mcp_tools/*.py`.

Para actualizarla:

```bash
python scripts/generate_tools_reference.py
```

Si buscas una guía por tarea, empieza por las páginas de `docs/guides/`. Esta página sirve como inventario técnico de las tools disponibles para MCP.

## Vista general (21 tools)

| Flujo | Tools relacionadas |
| --- | --- |
| Buscar estaciones | `search_stations`, `filter_stations_*`, `find_stations_near` |
| Confirmar metadatos | `get_station_info`, `check_data_availability` |
| Descargar datos | `scrape_station_data` |
| Revisar archivos locales | `list_downloaded_files`, `read_csv_preview`, `extract_month_from_csv` |
| Analizar datos | `summarize_station_data_tool`, `compare_periods_tool`, `detect_anomalies_tool` |
| Explorar inventario | `stations_count`, `stations_summary`, `get_departments_summary`, `get_location_hierarchy` |

## Índice de tools

| Grupo | Tool | Parámetros |
| --- | --- | --- |
| Calidad de datos | [`detect_anomalies_tool`](#detect_anomalies_tool) | `station_code`, `year`, `month`, `start_year`, `end_year`, `checks`, `severity`, `auto_download`, `trace_policy` |
| Comparación | [`compare_periods_tool`](#compare_periods_tool) | `station_code`, `periods`, `metrics`, `aggregation`, `deduplicate`, `auto_download` |
| Descarga | [`scrape_station_data`](#scrape_station_data) | `station_code`, `mode`, `year`, `month`, `start_year`, `end_year`, `individual`, `periods`, `force_download` |
| Archivos CSV | [`extract_month_from_csv`](#extract_month_from_csv) | `year`, `month`, `station_name`, `station_code`, `station_type`, `station_category`, `source_file`, `overwrite` |
| Archivos CSV | [`list_downloaded_files`](#list_downloaded_files) | `station_name`, `station_code`, `station_type`, `station_category`, `year`, `month`, `csv_dir`, `include_covering_files`, `mcp_response` |
| Archivos CSV | [`read_csv_preview`](#read_csv_preview) | `file_path`, `relative_path`, `station_name`, `station_code`, `station_type`, `station_category`, `year`, `month`, `max_rows`, `max_columns` |
| Recomendación | [`recommend_station_for_point_tool`](#recommend_station_for_point_tool) | `lat`, `lon`, `radius_km`, `station_type`, `target_altitude`, `prefer_status`, `min_years_available`, `limit` |
| Estaciones | [`check_data_availability`](#check_data_availability) | `station_code`, `before_year`, `after_year` |
| Estaciones | [`export_all_stations_csv`](#export_all_stations_csv) | `overwrite` |
| Estaciones | [`filter_stations_advanced`](#filter_stations_advanced) | `department`, `province`, `station_type`, `status`, `min_altitude`, `max_altitude`, `data_before_year` |
| Estaciones | [`filter_stations_by_altitude`](#filter_stations_by_altitude) | `min_altitude`, `max_altitude` |
| Estaciones | [`filter_stations_by_location`](#filter_stations_by_location) | `department`, `province`, `district` |
| Estaciones | [`find_stations_near`](#find_stations_near) | `lat`, `lon`, `radius_km`, `station_type` |
| Estaciones | [`get_all_stations`](#get_all_stations) | `limit`, `offset` |
| Estaciones | [`get_station_info`](#get_station_info) | `code` |
| Estaciones | [`search_stations`](#search_stations) | `query` |
| Inventario | [`get_departments_summary`](#get_departments_summary) | sin parámetros |
| Inventario | [`get_location_hierarchy`](#get_location_hierarchy) | sin parámetros |
| Inventario | [`stations_count`](#stations_count) | sin parámetros |
| Inventario | [`stations_summary`](#stations_summary) | sin parámetros |
| Resumen | [`summarize_station_data_tool`](#summarize_station_data_tool) | `station_code`, `year`, `month`, `start_year`, `end_year`, `metrics`, `include_quality`, `auto_download`, `trace_policy` |

## Detalle por grupo

### Calidad de datos

??? abstract "`detect_anomalies_tool`"

    <a id="detect_anomalies_tool"></a>

    Detecta anomalías y problemas de calidad en datos SENAMHI descargados para una estación y periodo.

    **Prompt de ejemplo**

    ```text
    Valida la calidad de datos de julio 2025 para la estación 108047
    ```

    **Cuándo usarla.** Úsala para auditoría de calidad; no reemplaza resumen ni comparación.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `station_code` | <code>str</code> | Sí | <code>—</code> | Código interno de la estación SENAMHI (ej: '107008', '100090'). |
    | `year` | <code>int &#124; None</code> | No | <code>None</code> | Año específico a analizar (ej: 2025). |
    | `month` | <code>int &#124; None</code> | No | <code>None</code> | Mes específico (1-12). Requiere year. |
    | `start_year` | <code>int &#124; None</code> | No | <code>None</code> | Año inicial del periodo a analizar. |
    | `end_year` | <code>int &#124; None</code> | No | <code>None</code> | Año final del periodo a analizar. |
    | `checks` | <code>list&#91;str&#93; &#124; None</code> | No | <code>None</code> | Lista opcional de checks a ejecutar. Si es None, usa checks por defecto según el esquema detectado. |
    | `severity` | <code>Literal&#91;'all', 'info', 'warning', 'critical'&#93;</code> | No | <code>'all'</code> | Filtro de severidad: all, info, warning o critical. Por defecto all. |
    | `auto_download` | <code>bool</code> | No | <code>False</code> | Si True, intenta resolver faltantes automáticamente. Actualmente no implementado. |
    | `trace_policy` | <code>Literal&#91;'as_0_05', 'as_0', 'as_null'&#93;</code> | No | <code>'as_0_05'</code> | Política para T en precipitación: as_0_05, as_0 o as_null. Por defecto as_0_05. |

### Comparación

??? abstract "`compare_periods_tool`"

    <a id="compare_periods_tool"></a>

    Compara dos o más periodos de datos de una estación SENAMHI con esquema autodetectado.

    **Prompt de ejemplo**

    ```text
    Compara marzo 2025 vs marzo 2026 para la estación 108047
    ```

    **Cuándo usarla.** Úsala solo para dos o más periodos de una misma estación.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `station_code` | <code>str</code> | Sí | <code>—</code> | Código interno de la estación SENAMHI (ej: '107008', '100090'). Obténlo primero con search_stations. |
    | `periods` | <code>list&#91;dict&#93;</code> | Sí | <code>—</code> | Lista de periodos a comparar. Cada periodo debe tener: - label: Etiqueta descriptiva (ej: 'Diciembre 2024') - year: Año (ej: 2024) - month: Mes opcional (1-12) Ejemplo: ``` {'label': 'Dic 2024', 'year': 2024, 'month': 12}, {'label': 'Dic 2025', 'year': 2025, 'month': 12}``` |
    | `metrics` | <code>list&#91;str&#93; &#124; None</code> | No | <code>None</code> | Métricas específicas a calcular. Si es None, usa todas las disponibles. Métricas meteorológicas convencionales: temp_max_avg, temp_min_avg, humidity_avg, precip_total, rainy_days, max_daily_precip Métricas meteorológicas automáticas: temp_avg, temp_max, temp_min, humidity_avg, precip_total, rainy_hours, rainy_days, wind_speed_avg, wind_speed_max, wind_direction_avg Métricas hidrológicas: river_level_avg, river_level_max, river_level_min, precip_total, rainy_hours, rainy_days |
    | `aggregation` | <code>str</code> | No | <code>'auto'</code> | Tipo de agregación. Usar 'auto' (por ahora único valor soportado). |
    | `deduplicate` | <code>bool</code> | No | <code>True</code> | Si True, elimina registros duplicados basándose en fecha/hora antes de calcular. Recomendado: True. |
    | `auto_download` | <code>bool</code> | No | <code>False</code> | Si True, intenta descargar datos faltantes automáticamente. Actualmente no implementado - los datos deben existir localmente. |

### Descarga

??? abstract "`scrape_station_data`"

    <a id="scrape_station_data"></a>

    Descarga datos históricos del SENAMHI para una estación y los guarda como CSV.

    **Prompt de ejemplo**

    ```text
    Descarga julio 2025 de la estación 108047
    ```

    **Cuándo usarla.** Descarga datos; no resume ni valida. Luego usa preview, resumen, comparación o validación.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `station_code` | <code>str</code> | Sí | <code>—</code> | Código interno de la estación (ej: '100090'). Usa search_stations primero si no tienes el código. |
    | `mode` | <code>str &#124; None</code> | No | <code>None</code> | Modo de descarga: 'month' = un mes específico (requiere year + month), 'year' = un año completo (requiere year), 'period' = rango de años (requiere start_year + end_year). Opcional si se usa el parámetro 'periods'. |
    | `year` | <code>int &#124; None</code> | No | <code>None</code> | Año (ej: 2025). Requerido para mode='month' o mode='year'. |
    | `month` | <code>int &#124; None</code> | No | <code>None</code> | Mes como número (1-12). Requerido para mode='month'. |
    | `start_year` | <code>int &#124; None</code> | No | <code>None</code> | Año de inicio del rango. Requerido para mode='period'. |
    | `end_year` | <code>int &#124; None</code> | No | <code>None</code> | Año de fin del rango. Requerido para mode='period'. |
    | `individual` | <code>bool</code> | No | <code>False</code> | True = genera un CSV por mes. False (por defecto) = CSV consolidado. |
    | `periods` | <code>list&#91;ScrapingPeriod&#93; &#124; None</code> | No | <code>None</code> | Lista de periodos específicos a descargar en una sola sesión de navegador (MÁS EFICIENTE para múltiples meses). Cada periodo debe tener 'year' y 'month'. Máximo 12 periodos. Ejemplo: ```{'year': 2025, 'month': 3}, {'year': 2026, 'month': 3}```. Si se provee, ignora mode/year/month/start_year/end_year. BENEFICIO: Abre el navegador UNA SOLA VEZ en lugar de N veces. |
    | `force_download` | <code>bool</code> | No | <code>False</code> | Si True, fuerza la descarga incluso si ya existe un archivo para ese periodo. Útil para obtener datos actualizados o corregidos. Por defecto: False. |

### Archivos CSV

??? abstract "`extract_month_from_csv`"

    <a id="extract_month_from_csv"></a>

    Extrae un mes desde un CSV anual o multianual y crea un CSV mensual.

    **Prompt de ejemplo**

    ```text
    Extrae julio 2025 desde el CSV consolidado de la estación 108047
    ```

    **Cuándo usarla.** Úsala cuando un mes está dentro de un CSV anual o multianual.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `year` | <code>int</code> | Sí | <code>—</code> | Año a extraer. |
    | `month` | <code>int</code> | Sí | <code>—</code> | Mes a extraer (1-12). |
    | `station_name` | <code>str &#124; None</code> | No | <code>None</code> | Nombre de la estación, por ejemplo 'Cajabamba'. |
    | `station_code` | <code>str &#124; None</code> | No | <code>None</code> | Código de estación. Recomendado para evitar ambigüedad. |
    | `station_type` | <code>str &#124; None</code> | No | <code>None</code> | Tipo de estación: M para meteorológica, H para hidrológica. |
    | `station_category` | <code>str &#124; None</code> | No | <code>None</code> | Categoría de estación, por ejemplo CO, EMA, HLM, EHA. |
    | `source_file` | <code>str &#124; None</code> | No | <code>None</code> | Archivo origen opcional. Puede ser filename dentro de la carpeta de estación o relative_path devuelto por list_downloaded_files. |
    | `overwrite` | <code>bool</code> | No | <code>False</code> | Si True, sobrescribe el CSV mensual si ya existe. |

??? abstract "`list_downloaded_files`"

    <a id="list_downloaded_files"></a>

    Lista archivos CSV descargados localmente por Garúa.

    **Prompt de ejemplo**

    ```text
    Lista archivos descargados para la estación 108047 en 2025
    ```

    **Cuándo usarla.** Úsala para confirmar si ya existen CSV locales antes de analizar.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `station_name` | <code>str &#124; None</code> | No | <code>None</code> | Nombre de la estación para filtrar (ej: 'Cabana', 'Cachicadan'). Si se omite, lista todas. |
    | `station_code` | <code>str &#124; None</code> | No | <code>None</code> | Código interno de la estación SENAMHI (ej: '107008', '100090') para filtrar. Obténlo primero con search_stations. Requiere station_name si se especifica. |
    | `station_type` | <code>str &#124; None</code> | No | <code>None</code> | Tipo de estación para filtrar (M para meteorológica, H para hidrológica). Requiere station_name si se especifica. |
    | `station_category` | <code>str &#124; None</code> | No | <code>None</code> | Categoría de estación para filtrar (ej: EMA, CO). Requiere station_name si se especifica. |
    | `year` | <code>int &#124; None</code> | No | <code>None</code> | Año para filtrar archivos que contengan datos de ese año (ej: 2025). |
    | `month` | <code>int &#124; None</code> | No | <code>None</code> | Mes para filtrar archivos individuales (1-12). Requiere year si se especifica. |
    | `csv_dir` | <code>str &#124; None</code> | No | <code>None</code> | Ruta del directorio CSV para listar archivos (opcional). Por defecto busca en la carpeta de salida configurada. |
    | `include_covering_files` | <code>bool</code> | No | <code>True</code> | Si es True, incluye archivos consolidados que cubren rangos de años, incluso si no son específicos del año/mes filtrado. Por defecto False. |
    | `mcp_response` | <code>bool</code> | No | <code>True</code> | Si True, devuelve una respuesta MCP completa. Por defecto False. |

??? abstract "`read_csv_preview`"

    <a id="read_csv_preview"></a>

    Muestra una vista previa tabular de un CSV descargado localmente.

    **Prompt de ejemplo**

    ```text
    Muestra una vista previa del CSV de julio 2025 para la estación 108047
    ```

    **Cuándo usarla.** Úsala para inspeccionar columnas y una muestra de filas antes de calcular métricas.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `file_path` | <code>str &#124; None</code> | No | <code>None</code> | Ruta completa o relativa del CSV dentro de la carpeta CSV de Garua. Recomendado usar el campo path devuelto por list_downloaded_files. |
    | `relative_path` | <code>str &#124; None</code> | No | <code>None</code> | Ruta relativa legacy del CSV dentro de la carpeta CSV de Garua (ej: 'Cajabamba_107008_M_CO/Cajabamba-2025.csv'). Se mantiene por compatibilidad; prefiere file_path. |
    | `station_name` | <code>str &#124; None</code> | No | <code>None</code> | Nombre de la estación para búsqueda automática del CSV. |
    | `station_code` | <code>str &#124; None</code> | No | <code>None</code> | Código de estación para búsqueda precisa del CSV. Recomendado si hay estaciones con el mismo nombre. |
    | `station_type` | <code>str &#124; None</code> | No | <code>None</code> | Tipo de estación: M para meteorológica, H para hidrológica. |
    | `station_category` | <code>str &#124; None</code> | No | <code>None</code> | Categoría de estación, por ejemplo CO, EMA, HLM, EHA. |
    | `year` | <code>int &#124; None</code> | No | <code>None</code> | Año a mostrar/filtrar dentro del CSV. |
    | `month` | <code>int &#124; None</code> | No | <code>None</code> | Mes a filtrar dentro del CSV (1-12). Requiere year. |
    | `max_rows` | <code>int</code> | No | <code>20</code> | — |
    | `max_columns` | <code>int</code> | No | <code>20</code> | — |

### Recomendación

??? abstract "`recommend_station_for_point_tool`"

    <a id="recommend_station_for_point_tool"></a>

    Recomienda las mejores estaciones SENAMHI para un punto geográfico dado.

    **Prompt de ejemplo**

    ```text
    Recomienda una estación para lat -7.61, lon -77.82 con altitud 3000 msnm
    ```

    **Cuándo usarla.** Úsala cuando la selección de estación debe justificarse por criterios múltiples.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `lat` | <code>float</code> | Sí | <code>—</code> | Latitud del punto de interés en grados decimales. Negativo para el hemisferio Sur. |
    | `lon` | <code>float</code> | Sí | <code>—</code> | Longitud del punto de interés en grados decimales. Negativo para el oeste. |
    | `radius_km` | <code>float</code> | No | <code>100.0</code> | Radio máximo de búsqueda en kilómetros. Por defecto 100 km. |
    | `station_type` | <code>Literal&#91;'M', 'H', 'all'&#93;</code> | No | <code>'M'</code> | Tipo de estación: 'M' (meteorológica), 'H' (hidrológica), 'all' (ambas). Por defecto 'M'. |
    | `target_altitude` | <code>float &#124; None</code> | No | <code>None</code> | Altitud del proyecto o punto de interés en metros sobre el nivel del mar (msnm). Si se proporciona, las estaciones con altitud similar tendrán mejor score. |
    | `prefer_status` | <code>list&#91;str&#93; &#124; None</code> | No | <code>None</code> | Lista de estados operativos en orden de prioridad. Ejemplo: &#91;'REAL', 'AUTOMATICA', 'DIFERIDO'&#93;. Si no se especifica, usa prioridades por defecto. |
    | `min_years_available` | <code>int &#124; None</code> | No | <code>None</code> | Mínimo de años de datos históricos requeridos. Excluye estaciones con menos años de historial. Ejemplo: 5 para proyectos que requieren series largas. |
    | `limit` | <code>int</code> | No | <code>5</code> | Cantidad máxima de recomendaciones a devolver. Por defecto 5, máximo 20. |

### Estaciones

??? abstract "`check_data_availability`"

    <a id="check_data_availability"></a>

    Consulta desde cuándo hay datos históricos disponibles para estaciones SENAMHI.

    **Prompt de ejemplo**

    ```text
    ¿Desde cuándo hay datos para la estación 108047?
    ```

    **Cuándo usarla.** Úsala antes de descargar o comparar periodos históricos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `station_code` | <code>str &#124; None</code> | No | <code>None</code> | Código de una estación específica (ej: '100090'). Si se provee, retorna info de esa estación. |
    | `before_year` | <code>int &#124; None</code> | No | <code>None</code> | Filtra estaciones con datos disponibles ANTES de este año (ej: 2010 para series largas). |
    | `after_year` | <code>int &#124; None</code> | No | <code>None</code> | Filtra estaciones con datos disponibles DESPUÉS de este año (ej: 2022 para series recientes). |

??? abstract "`export_all_stations_csv`"

    <a id="export_all_stations_csv"></a>

    Exporta el catálogo completo de estaciones SENAMHI a un archivo CSV.

    **Prompt de ejemplo**

    ```text
    Exporta el catálogo completo de estaciones a CSV
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `overwrite` | <code>bool</code> | No | <code>True</code> | Si es True, regenera el CSV aunque ya exista. Si es False, reutiliza el archivo existente cuando esté disponible. |

??? abstract "`filter_stations_advanced`"

    <a id="filter_stations_advanced"></a>

    Filtra estaciones SENAMHI combinando varios criterios en una sola consulta.

    **Prompt de ejemplo**

    ```text
    Busca estaciones meteorológicas activas en Puno sobre 3500 msnm
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `department` | <code>str &#124; None</code> | No | <code>None</code> | Departamento del Perú (ej: 'Arequipa', 'Puno'). Case-insensitive, parcial. |
    | `province` | <code>str &#124; None</code> | No | <code>None</code> | Provincia (ej: 'Caylloma'). Case-insensitive, parcial. |
    | `station_type` | <code>str &#124; None</code> | No | <code>None</code> | Tipo: 'M' = meteorológica, 'H' = hidrológica. Omitir para ambos. |
    | `status` | <code>str &#124; None</code> | No | <code>None</code> | Estado operativo: 'REAL' (transmisión en tiempo real), 'DIFERIDO', 'AUTOMATICA'. |
    | `min_altitude` | <code>float &#124; None</code> | No | <code>None</code> | Altitud mínima en msnm. |
    | `max_altitude` | <code>float &#124; None</code> | No | <code>None</code> | Altitud máxima en msnm. |
    | `data_before_year` | <code>int &#124; None</code> | No | <code>None</code> | Solo estaciones con datos disponibles desde ANTES de este año (para series largas). |

??? abstract "`filter_stations_by_altitude`"

    <a id="filter_stations_by_altitude"></a>

    Filtra estaciones SENAMHI por rango de altitud en msnm.

    **Prompt de ejemplo**

    ```text
    Busca estaciones sobre 3000 msnm
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `min_altitude` | <code>float &#124; None</code> | No | <code>None</code> | Altitud mínima en metros sobre el nivel del mar (msnm). Ej: 3000 para zonas altoandinas. |
    | `max_altitude` | <code>float &#124; None</code> | No | <code>None</code> | Altitud máxima en msnm. Ej: 500 para zonas costeras o valles bajos. |

??? abstract "`filter_stations_by_location`"

    <a id="filter_stations_by_location"></a>

    Filtra estaciones SENAMHI por ubicación administrativa del Perú.

    **Prompt de ejemplo**

    ```text
    Busca estaciones en Arequipa, provincia Caylloma
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `department` | <code>str &#124; None</code> | No | <code>None</code> | Nombre del departamento (ej: 'Cajamarca', 'Arequipa'). Case-insensitive, parcial. |
    | `province` | <code>str &#124; None</code> | No | <code>None</code> | Nombre de la provincia (ej: 'Contumaza', 'Caylloma'). Case-insensitive, parcial. |
    | `district` | <code>str &#124; None</code> | No | <code>None</code> | Nombre del distrito. Case-insensitive, parcial. |

??? abstract "`find_stations_near`"

    <a id="find_stations_near"></a>

    Encuentra estaciones SENAMHI cercanas a un punto geográfico.

    **Prompt de ejemplo**

    ```text
    Busca estaciones cerca de lat -7.61, lon -77.82
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `lat` | <code>float</code> | Sí | <code>—</code> | Latitud del punto central en grados decimales (ej: -9.5, -13.5). Negativo para el hemisferio Sur. |
    | `lon` | <code>float</code> | Sí | <code>—</code> | Longitud del punto central en grados decimales (ej: -77.5, -76.3). Negativo para el oeste. |
    | `radius_km` | <code>float</code> | No | <code>50.0</code> | Radio de búsqueda en kilómetros. Por defecto 50 km. |
    | `station_type` | <code>str</code> | No | <code>'all'</code> | Tipo de estación: 'all' (todas), 'M' (meteorológicas), 'H' (hidrológicas). |

??? abstract "`get_all_stations`"

    <a id="get_all_stations"></a>

    Devuelve una página del catálogo de estaciones SENAMHI disponibles.

    **Prompt de ejemplo**

    ```text
    Lista las primeras estaciones disponibles
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `limit` | <code>int</code> | No | <code>100</code> | Cantidad máxima de estaciones a devolver en esta página. Usa export_all_stations_csv si necesitas el catálogo completo. |
    | `offset` | <code>int</code> | No | <code>0</code> | Cantidad de estaciones a omitir antes de devolver resultados. |

??? abstract "`get_station_info`"

    <a id="get_station_info"></a>

    Obtiene la ficha completa de una estación SENAMHI por código.

    **Prompt de ejemplo**

    ```text
    Dame la ficha de la estación 108047
    ```

    **Cuándo usarla.** Úsala después de buscar cuando necesites confirmar metadatos de una estación.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `code` | <code>str</code> | Sí | <code>—</code> | Código interno de la estación (ej: '100090', '153209'). Obtenlo primero con search_stations si no lo tienes. |

??? abstract "`search_stations`"

    <a id="search_stations"></a>

    Busca estaciones SENAMHI por código o por nombre.

    **Prompt de ejemplo**

    ```text
    Busca estaciones llamadas Cabana
    ```

    **Cuándo usarla.** Úsala antes de descargar o analizar cuando el código de estación no esté confirmado.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `query` | <code>str</code> | Sí | <code>—</code> | Código exacto de la estación (ej: '100090') o nombre parcial (ej: 'Cabana', 'Juli'). La búsqueda por nombre es case-insensitive y admite coincidencias parciales. |

### Inventario

??? abstract "`get_departments_summary`"

    <a id="get_departments_summary"></a>

    Devuelve estadísticas de estaciones agrupadas por departamento del Perú.

    **Prompt de ejemplo**

    ```text
    ¿Qué departamentos tienen más estaciones?
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    Sin parámetros.

??? abstract "`get_location_hierarchy`"

    <a id="get_location_hierarchy"></a>

    Devuelve la jerarquía administrativa de ubicaciones con conteos de estaciones.

    **Prompt de ejemplo**

    ```text
    Muestra la jerarquía de ubicaciones con estaciones
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    Sin parámetros.

??? abstract "`stations_count`"

    <a id="stations_count"></a>

    Devuelve el número total de estaciones SENAMHI disponibles en el catálogo local.

    **Prompt de ejemplo**

    ```text
    ¿Cuántas estaciones tienes disponibles?
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    Sin parámetros.

??? abstract "`stations_summary`"

    <a id="stations_summary"></a>

    Devuelve un resumen global de estaciones por tipo y estado operativo.

    **Prompt de ejemplo**

    ```text
    Resume el inventario de estaciones por tipo y estado
    ```

    **Cuándo usarla.** Revisa la guía de usuario relacionada antes de usarla en flujos largos.

    **Parámetros**

    Sin parámetros.

### Resumen

??? abstract "`summarize_station_data_tool`"

    <a id="summarize_station_data_tool"></a>

    Resume datos SENAMHI de una estación para un mes, año o periodo individual.

    **Prompt de ejemplo**

    ```text
    Resume julio 2025 para la estación 108047
    ```

    **Cuándo usarla.** Úsala para un solo periodo. Para dos o más periodos usa comparación.

    **Parámetros**

    | Parámetro | Tipo | Requerido | Default | Descripción |
    | --- | --- | --- | --- | --- |
    | `station_code` | <code>str</code> | Sí | <code>—</code> | Código interno de la estación SENAMHI (ej: '107008', '100090'). Obténlo primero con search_stations o get_station_info. |
    | `year` | <code>int &#124; None</code> | No | <code>None</code> | Año específico a resumir (ej: 2025). |
    | `month` | <code>int &#124; None</code> | No | <code>None</code> | Mes específico (1-12). Requiere year. |
    | `start_year` | <code>int &#124; None</code> | No | <code>None</code> | Año inicial si se resume un rango de años. |
    | `end_year` | <code>int &#124; None</code> | No | <code>None</code> | Año final si se resume un rango de años. |
    | `metrics` | <code>list&#91;str&#93; &#124; None</code> | No | <code>None</code> | Métricas específicas a calcular. Si es None, usa las del esquema detectado. Meteorológica convencional: temp_max_avg, temp_min_avg, humidity_avg, precip_total, rainy_days, dry_days, missing_days, trace_days, max_daily_precip Meteorológica automática: temp_avg, precip_total, rainy_hours, rainy_days, dry_hours, wind_speed_avg, wind_speed_max Hidrológica: river_level_avg/max/min, precip_total, rainy_hours |
    | `include_quality` | <code>bool</code> | No | <code>True</code> | Si True, incluye diagnóstico resumido de calidad reutilizando validate_dataset (duplicados, S/D, T, fechas faltantes). |
    | `auto_download` | <code>bool</code> | No | <code>False</code> | Si True, intenta descargar datos faltantes. Actualmente no implementado — los datos deben existir localmente. |
    | `trace_policy` | <code>Literal&#91;'as_0_05', 'as_0', 'as_null'&#93;</code> | No | <code>'as_0_05'</code> | Política para trazas T en precipitación: as_0_05 (default), as_0 o as_null. |
