# Referencia de tools MCP

Este archivo se genera desde los docstrings en `src/garua/mcp_tools/*.py`.

Para actualizarlo:

```bash
python scripts/generate_tools_reference.py
```

La referencia es técnica. Para aprender por flujo de trabajo, usa las guías en `docs/guides/`.

## Tools disponibles (21)

### anomaly_tools

#### `detect_anomalies_tool`

Detecta anomalías y problemas de calidad en datos SENAMHI descargados para una estación y periodo.

- **Parametros:** `station_code`, `year`, `month`, `start_year`, `end_year`, `checks`, `severity`, `auto_download`, `trace_policy`
- **Ejemplo de prompt:** `Valida la calidad de datos de julio 2025 para la estacion 108047`
- **Nota de flujo:** Usala para auditoria de calidad; no reemplaza resumen ni comparacion.

### comparison_tools

#### `compare_periods_tool`

Compara dos o más periodos de datos de una estación SENAMHI con esquema autodetectado.

- **Parametros:** `station_code`, `periods`, `metrics`, `aggregation`, `deduplicate`, `auto_download`
- **Ejemplo de prompt:** `Compara marzo 2025 vs marzo 2026 para la estacion 108047`
- **Nota de flujo:** Usala solo para dos o mas periodos de una misma estacion.

### download_tools

#### `scrape_station_data`

Descarga datos históricos del SENAMHI para una estación y los guarda como CSV.

- **Parametros:** `station_code`, `mode`, `year`, `month`, `start_year`, `end_year`, `individual`, `periods`, `force_download`
- **Ejemplo de prompt:** `Descarga julio 2025 de la estacion 108047`
- **Nota de flujo:** Descarga datos; no resume ni valida. Luego usa preview, resumen, comparacion o validacion.

### file_tools

#### `extract_month_from_csv`

Extrae un mes desde un CSV anual o multianual y crea un CSV mensual.

- **Parametros:** `year`, `month`, `station_name`, `station_code`, `station_type`, `station_category`, `source_file`, `overwrite`
- **Ejemplo de prompt:** `Extrae julio 2025 desde el CSV consolidado de la estacion 108047`
- **Nota de flujo:** Usala cuando un mes esta dentro de un CSV anual o multianual.

#### `list_downloaded_files`

Lista archivos CSV descargados localmente por Garúa.

- **Parametros:** `station_name`, `station_code`, `station_type`, `station_category`, `year`, `month`, `csv_dir`, `include_covering_files`, `mcp_response`
- **Ejemplo de prompt:** `Lista archivos descargados para la estacion 108047 en 2025`
- **Nota de flujo:** Usala para confirmar si ya existen CSV locales antes de analizar.

#### `read_csv_preview`

Muestra una vista previa tabular de un CSV descargado localmente.

- **Parametros:** `file_path`, `relative_path`, `station_name`, `station_code`, `station_type`, `station_category`, `year`, `month`, `max_rows`, `max_columns`
- **Ejemplo de prompt:** `Muestra una vista previa del CSV de julio 2025 para la estacion 108047`
- **Nota de flujo:** Usala para inspeccionar columnas y una muestra de filas antes de calcular metricas.

### recommendation_tools

#### `recommend_station_for_point_tool`

Recomienda las mejores estaciones SENAMHI para un punto geográfico dado.

- **Parametros:** `lat`, `lon`, `radius_km`, `station_type`, `target_altitude`, `prefer_status`, `min_years_available`, `limit`
- **Ejemplo de prompt:** `Recomienda una estacion para lat -7.61, lon -77.82 con altitud 3000 msnm`
- **Nota de flujo:** Usala cuando la seleccion de estacion debe justificarse por criterios multiples.

### station_tools

#### `check_data_availability`

Consulta desde cuándo hay datos históricos disponibles para estaciones SENAMHI.

- **Parametros:** `station_code`, `before_year`, `after_year`
- **Ejemplo de prompt:** `Desde cuando hay datos para la estacion 108047?`
- **Nota de flujo:** Usala antes de descargar o comparar periodos historicos.

#### `export_all_stations_csv`

Exporta el catálogo completo de estaciones SENAMHI a un archivo CSV.

- **Parametros:** `overwrite`
- **Ejemplo de prompt:** `Exporta el catalogo completo de estaciones a CSV`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `filter_stations_advanced`

Filtra estaciones SENAMHI combinando varios criterios en una sola consulta.

- **Parametros:** `department`, `province`, `station_type`, `status`, `min_altitude`, `max_altitude`, `data_before_year`
- **Ejemplo de prompt:** `Busca estaciones meteorologicas activas en Puno sobre 3500 msnm`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `filter_stations_by_altitude`

Filtra estaciones SENAMHI por rango de altitud en msnm.

- **Parametros:** `min_altitude`, `max_altitude`
- **Ejemplo de prompt:** `Busca estaciones sobre 3000 msnm`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `filter_stations_by_location`

Filtra estaciones SENAMHI por ubicación administrativa del Perú.

- **Parametros:** `department`, `province`, `district`
- **Ejemplo de prompt:** `Busca estaciones en Arequipa, provincia Caylloma`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `find_stations_near`

Encuentra estaciones SENAMHI cercanas a un punto geográfico.

- **Parametros:** `lat`, `lon`, `radius_km`, `station_type`
- **Ejemplo de prompt:** `Busca estaciones cerca de lat -7.61, lon -77.82`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `get_all_stations`

Devuelve una página del catálogo de estaciones SENAMHI disponibles.

- **Parametros:** `limit`, `offset`
- **Ejemplo de prompt:** `Lista las primeras estaciones disponibles`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `get_station_info`

Obtiene la ficha completa de una estación SENAMHI por código.

- **Parametros:** `code`
- **Ejemplo de prompt:** `Dame la ficha de la estacion 108047`
- **Nota de flujo:** Usala despues de buscar cuando necesites confirmar metadatos de una estacion.

#### `search_stations`

Busca estaciones SENAMHI por código o por nombre.

- **Parametros:** `query`
- **Ejemplo de prompt:** `Busca estaciones llamadas Cabana`
- **Nota de flujo:** Usala antes de descargar o analizar cuando el codigo de estacion no este confirmado.

### stats_tools

#### `get_departments_summary`

Devuelve estadísticas de estaciones agrupadas por departamento del Perú.

- **Parametros:** sin parametros
- **Ejemplo de prompt:** `Que departamentos tienen mas estaciones?`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `get_location_hierarchy`

Devuelve la jerarquía administrativa de ubicaciones con conteos de estaciones.

- **Parametros:** sin parametros
- **Ejemplo de prompt:** `Muestra la jerarquia de ubicaciones con estaciones`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `stations_count`

Devuelve el número total de estaciones SENAMHI disponibles en el catálogo local.

- **Parametros:** sin parametros
- **Ejemplo de prompt:** `Cuantas estaciones tienes disponibles?`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

#### `stations_summary`

Devuelve un resumen global de estaciones por tipo y estado operativo.

- **Parametros:** sin parametros
- **Ejemplo de prompt:** `Resume el inventario de estaciones por tipo y estado`
- **Nota de flujo:** Revisa la guia de usuario relacionada antes de usarla en flujos largos.

### summary_tools

#### `summarize_station_data_tool`

Resume datos SENAMHI de una estación para un mes, año o periodo individual.

- **Parametros:** `station_code`, `year`, `month`, `start_year`, `end_year`, `metrics`, `include_quality`, `auto_download`, `trace_policy`
- **Ejemplo de prompt:** `Resume julio 2025 para la estacion 108047`
- **Nota de flujo:** Usala para un solo periodo. Para dos o mas periodos usa comparacion.
