"""Servicio de comparación de periodos de datos."""

import csv
from pathlib import Path

from garua import settings
from garua.models.comparison import (
    ComparisonPeriod,
    ComparisonWarning,
    ComparePeriodsResponse,
    PeriodDifference,
    PeriodSummary,
    SchemaInfo,
)
from garua.models.data_schema import (
    HYDROLOGICAL_AUTOMATIC_HEADERS,
    HYDROLOGICAL_CONVENTIONAL_HEADERS,
    METEOROLOGICAL_AUTOMATIC_HEADERS,
    METEOROLOGICAL_CONVENTIONAL_HEADERS,
)
from garua.models.station import Station, StationSummary
from garua.services.metrics import get_metrics_calculator
from garua.services.station import find_station_by_code
from garua.utils.helpers import (
    build_station_folder_name,
    normalize_station_slug,
    parse_csv_period,
)

# Mapeo de esquemas con sus configuraciones
STATION_SCHEMA_MAP = {
    "meteorological_conventional": {
        "headers": METEOROLOGICAL_CONVENTIONAL_HEADERS,
        "frequency": "daily",
        "dedup_keys": ["Año", "Mes", "Día"],
    },
    "meteorological_automatic": {
        "headers": METEOROLOGICAL_AUTOMATIC_HEADERS,
        "frequency": "hourly",
        "dedup_keys": ["Año", "Mes", "Día", "Hora"],
    },
    "hydrological_conventional": {
        "headers": HYDROLOGICAL_CONVENTIONAL_HEADERS,
        "frequency": "daily_observations",
        "dedup_keys": ["Año", "Mes", "Día"],
    },
    "hydrological_automatic": {
        "headers": HYDROLOGICAL_AUTOMATIC_HEADERS,
        "frequency": "hourly",
        "dedup_keys": ["Año", "Mes", "Día", "Hora"],
    },
}


class UnsupportedSchemaError(Exception):
    """Error cuando no se puede detectar el esquema."""

    pass


def detect_schema(headers: list[str]) -> str:
    """
    Detecta el esquema basándose en los headers del CSV.

    Args:
        headers: Headers del CSV

    Returns:
        Tipo de esquema detectado

    Raises:
        UnsupportedSchemaError: Si no se puede detectar el esquema
    """
    header_set = set(headers)

    # Orden de prioridad: más específico primero
    if set(METEOROLOGICAL_AUTOMATIC_HEADERS).issubset(header_set):
        return "meteorological_automatic"

    if set(HYDROLOGICAL_AUTOMATIC_HEADERS).issubset(header_set):
        return "hydrological_automatic"

    if set(METEOROLOGICAL_CONVENTIONAL_HEADERS).issubset(header_set):
        return "meteorological_conventional"

    if set(HYDROLOGICAL_CONVENTIONAL_HEADERS).issubset(header_set):
        return "hydrological_conventional"

    raise UnsupportedSchemaError(
        f"No se pudo detectar el esquema. Headers encontrados: {headers}"
    )


def find_csv_file(station: Station, year: int, month: int | None = None) -> Path | None:
    """
    Busca un archivo CSV para una estación y periodo.

    Args:
        station: Estación
        year: Año
        month: Mes (opcional)

    Returns:
        Path del archivo o None si no existe
    """
    # Normalizar nombre de la estación (igual que en download_tools y file_tools)
    station_normalized = normalize_station_slug(station.name)
    station_folder_name = build_station_folder_name(station)
    csv_dir = Path(settings.CSV_DIR).resolve() / station_folder_name

    if not csv_dir.exists():
        return None

    candidates: list[tuple[int, int, str, Path]] = []

    for csv_file in csv_dir.glob("*.csv"):
        period = parse_csv_period(csv_file.stem)
        if period is None:
            continue

        if month and period["kind"] == "month":
            if period["year"] == year and period["month"] == month:
                priority = 0
            else:
                continue
        elif period["kind"] == "year":
            if period["year"] == year:
                priority = 1
            else:
                continue
        elif period["kind"] == "period":
            if period["start_year"] <= year <= period["end_year"]:
                priority = 2
            else:
                continue
        else:
            continue

        station_part = normalize_station_slug(period.get("station_part", ""))
        name_priority = 0 if station_part == station_normalized else 1
        candidates.append((priority, name_priority, csv_file.name, csv_file))

    if candidates:
        return sorted(candidates)[0][3]

    return None


def read_csv_data(file_path: Path) -> tuple[list[str], list[dict]]:
    """
    Lee un archivo CSV y retorna headers y registros.

    Args:
        file_path: Path del archivo CSV

    Returns:
        Tupla (headers, rows)
    """
    with open(file_path, "r", encoding=settings.CSV_ENCODING) as f:
        reader = csv.DictReader(f, delimiter=settings.CSV_SEPARATOR)
        headers = list(reader.fieldnames or [])
        rows = list(reader)

    return headers, rows


def filter_rows_by_period(
    rows: list[dict], year: int, month: int | None = None
) -> list[dict]:
    """
    Filtra registros por año y mes.

    Args:
        rows: Registros del CSV
        year: Año a filtrar
        month: Mes a filtrar (opcional)

    Returns:
        Registros filtrados
    """
    filtered = []
    for row in rows:
        try:
            row_year = int(row.get("Año", 0))
            if row_year != year:
                continue

            if month:
                row_month = int(row.get("Mes", 0))
                if row_month != month:
                    continue

            filtered.append(row)
        except (ValueError, TypeError):
            continue

    return filtered


def deduplicate_rows(rows: list[dict], dedup_keys: list[str]) -> tuple[list[dict], int]:
    """
    Elimina registros duplicados basándose en claves.

    Args:
        rows: Registros
        dedup_keys: Claves para identificar duplicados

    Returns:
        Tupla (registros únicos, cantidad de duplicados)
    """
    seen = set()
    unique_rows = []
    duplicates = 0

    for row in rows:
        # Crear clave única
        key_parts = [str(row.get(k, "")) for k in dedup_keys]
        key = "|".join(key_parts)

        if key in seen:
            duplicates += 1
            continue

        seen.add(key)
        unique_rows.append(row)

    return unique_rows, duplicates


def calculate_differences(
    periods: list[PeriodSummary],
) -> list[PeriodDifference]:
    """
    Calcula diferencias entre periodos consecutivos.

    Args:
        periods: Lista de periodos

    Returns:
        Lista de diferencias
    """
    differences = []

    for i in range(len(periods) - 1):
        from_period = periods[i]
        to_period = periods[i + 1]

        deltas = {}
        percent_changes = {}

        for metric in from_period.metrics.keys():
            from_val = from_period.metrics.get(metric)
            to_val = to_period.metrics.get(metric)

            if from_val is None or to_val is None:
                deltas[metric] = None
                percent_changes[metric] = None
                continue

            delta = to_val - from_val
            deltas[metric] = round(delta, 2)

            # Calcular cambio porcentual
            if from_val != 0:
                pct_change = (delta / abs(from_val)) * 100
                percent_changes[metric] = round(pct_change, 1)
            else:
                percent_changes[metric] = None if to_val == 0 else float("inf")

        differences.append(
            PeriodDifference(
                from_label=from_period.label,
                to_label=to_period.label,
                deltas=deltas,
                percent_changes=percent_changes,
            )
        )

    return differences


def generate_summary(
    schema_kind: str, differences: list[PeriodDifference]
) -> str | None:
    """
    Genera un resumen interpretativo en español.

    Args:
        schema_kind: Tipo de esquema
        differences: Diferencias calculadas

    Returns:
        Texto del resumen o None
    """
    if not differences:
        return None

    # Tomar la primera diferencia (más relevante)
    diff = differences[0]

    summaries = []

    # Análisis según el esquema
    if "meteorological" in schema_kind:
        # Precipitación
        precip_delta = diff.deltas.get("precip_total")
        if precip_delta is not None and abs(precip_delta) > 10:
            if precip_delta < 0:
                summaries.append(
                    f"{diff.to_label} fue más seco que {diff.from_label}, con {abs(precip_delta):.1f} mm menos de precipitación"
                )
            else:
                summaries.append(
                    f"{diff.to_label} fue más lluvioso que {diff.from_label}, con {precip_delta:.1f} mm más de precipitación"
                )

        # Temperatura
        temp_delta = diff.deltas.get("temp_max_avg") or diff.deltas.get("temp_avg")
        if temp_delta is not None and abs(temp_delta) > 1:
            if temp_delta > 0:
                summaries.append(f"temperaturas {temp_delta:.1f}°C más altas")
            else:
                summaries.append(f"temperaturas {abs(temp_delta):.1f}°C más bajas")

        # Días con lluvia
        rainy_days_delta = diff.deltas.get("rainy_days")
        if rainy_days_delta is not None and abs(rainy_days_delta) > 3:
            if rainy_days_delta < 0:
                summaries.append(f"{abs(rainy_days_delta)} días menos con lluvia")
            else:
                summaries.append(f"{rainy_days_delta} días más con lluvia")

    elif "hydrological" in schema_kind:
        # Nivel del río
        level_delta = diff.deltas.get("river_level_avg")
        if level_delta is not None and abs(level_delta) > 0.1:
            if level_delta < 0:
                summaries.append(f"nivel del río {abs(level_delta):.2f} m más bajo")
            else:
                summaries.append(f"nivel del río {level_delta:.2f} m más alto")

    if not summaries:
        return "Los periodos presentan condiciones similares."

    return (
        f"{diff.to_label} comparado con {diff.from_label}: "
        + ", ".join(summaries)
        + "."
    )


def compare_periods(
    station_code: str,
    periods: list[dict],
    metrics: list[str] | None = None,
    aggregation: str = "auto",
    deduplicate: bool = True,
    auto_download: bool = True,
) -> ComparePeriodsResponse:
    """
    Compara periodos de datos para una estación.

    Args:
        station_code: Código de la estación
        periods: Lista de periodos a comparar
        metrics: Métricas a calcular (None = todas)
        aggregation: Tipo de agregación (no usado aún)
        deduplicate: Si eliminar duplicados
        auto_download: Si descargar datos faltantes

    Returns:
        Respuesta con comparación completa

    Raises:
        ValueError: Si la estación no existe o faltan datos
        UnsupportedSchemaError: Si el esquema no es reconocido
    """
    warnings = []

    # 1. Validar y obtener información de estación
    station = find_station_by_code(station_code)
    if not station:
        raise ValueError(f"Estación '{station_code}' no encontrada")

    station_info = StationSummary(
        name=station.name,
        code=station.code,
        category=station.category,
        type=station.station_type,
        status=station.status,
    )

    # 2. Validar periodos
    validated_periods = []
    for p in periods:
        try:
            validated_periods.append(ComparisonPeriod(**p))
        except Exception as e:
            warnings.append(
                ComparisonWarning(
                    code="INVALID_PERIOD",
                    message=f"Periodo inválido: {e}",
                    details={"period": p},
                )
            )

    if not validated_periods:
        raise ValueError("No hay periodos válidos para comparar")

    # 3. Resolver archivos CSV
    csv_files = []
    for period in validated_periods:
        csv_file = find_csv_file(station, period.year, period.month)

        if not csv_file:
            if auto_download:
                warnings.append(
                    ComparisonWarning(
                        code="FILE_NOT_FOUND_AUTO_DOWNLOAD",
                        message=f"Archivo para {period.label} no encontrado. Se requiere descarga manual.",
                        details={"period": period.model_dump()},
                    )
                )
                raise ValueError(
                    f"Archivo para {period.label} no encontrado. "
                    f"Descarga los datos primero con scrape_station_data."
                )
            else:
                raise ValueError(
                    f"Archivo para {period.label} no encontrado y auto_download=False"
                )

        csv_files.append((period, csv_file))

    # 4. Leer primer archivo para detectar esquema
    headers, _ = read_csv_data(csv_files[0][1])
    schema_kind = detect_schema(headers)
    schema_config = STATION_SCHEMA_MAP[schema_kind]

    # 5. Obtener calculador de métricas
    calculator = get_metrics_calculator(schema_kind)
    available_metrics = calculator.get_available_metrics()

    # 6. Resolver métricas a calcular
    if metrics is None:
        metrics_to_calculate = available_metrics
    else:
        metrics_to_calculate = [m for m in metrics if m in available_metrics]
        invalid_metrics = set(metrics) - set(available_metrics)
        if invalid_metrics:
            warnings.append(
                ComparisonWarning(
                    code="INVALID_METRICS",
                    message=f"Métricas no disponibles para {schema_kind}: {', '.join(invalid_metrics)}",
                    details={
                        "invalid_metrics": list(invalid_metrics),
                        "available_metrics": available_metrics,
                    },
                )
            )

    if not metrics_to_calculate:
        raise ValueError("No hay métricas válidas para calcular")

    # 7. Procesar cada periodo
    period_summaries = []

    for period, csv_file in csv_files:
        # Leer datos
        _, all_rows = read_csv_data(csv_file)

        # Filtrar por periodo
        filtered_rows = filter_rows_by_period(all_rows, period.year, period.month)

        if not filtered_rows:
            warnings.append(
                ComparisonWarning(
                    code="NO_DATA_FOR_PERIOD",
                    message=f"No se encontraron datos para {period.label}",
                    details={"period": period.model_dump()},
                )
            )
            continue

        total_rows = len(filtered_rows)

        # Deduplicar si se solicita
        duplicates = 0
        if deduplicate:
            filtered_rows, duplicates = deduplicate_rows(
                filtered_rows, schema_config["dedup_keys"]
            )

            if duplicates > 0:
                warnings.append(
                    ComparisonWarning(
                        code="DUPLICATE_ROWS",
                        message=f"Se detectaron {duplicates} registros duplicados en {period.label} y fueron eliminados.",
                        details={"count": duplicates, "period": period.label},
                    )
                )

        # Calcular métricas
        calculator_warnings_before = len(calculator.warnings)
        metrics_result = calculator.summarize(filtered_rows, metrics_to_calculate)

        # Capturar warnings del calculador
        new_warnings = calculator.warnings[calculator_warnings_before:]
        for w in new_warnings:
            warnings.append(ComparisonWarning(**w))

        period_summaries.append(
            PeriodSummary(
                label=period.label,
                year=period.year,
                month=period.month,
                rows=total_rows,
                valid_rows=len(filtered_rows),
                metrics=metrics_result,
            )
        )

    if not period_summaries:
        raise ValueError("No se pudieron procesar los periodos")

    # 8. Calcular diferencias
    differences = calculate_differences(period_summaries)

    # 9. Generar resumen
    summary = generate_summary(schema_kind, differences)

    # 10. Construir respuesta
    return ComparePeriodsResponse(
        station=station_info,
        schema=SchemaInfo(
            kind=schema_kind,
            frequency=schema_config["frequency"],
            headers=list(headers),
            available_metrics=available_metrics,
        ),
        periods=period_summaries,
        differences=differences,
        warnings=warnings,
        summary=summary,
    )
