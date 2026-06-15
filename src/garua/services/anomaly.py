"""Servicio de deteccion de anomalias para datasets SENAMHI."""

import calendar
from collections import Counter
from pathlib import Path
from typing import Any, Literal

from garua import settings
from garua.models.anomaly import (
    AnomalyIssue,
    DataQualitySummary,
    DetectAnomaliesResponse,
)
from garua.models.data_schema import (
    HYDROLOGICAL_AUTOMATIC_HEADERS,
    HYDROLOGICAL_CONVENTIONAL_HEADERS,
    METEOROLOGICAL_AUTOMATIC_HEADERS,
    METEOROLOGICAL_CONVENTIONAL_HEADERS,
)
from garua.models.station import Station, StationSummary
from garua.services.comparison import (
    detect_schema,
    find_csv_file,
    read_csv_data,
)
from garua.services.station import find_station_by_code

from garua.utils.special_values import TracePolicy, normalize_special_value
from garua.utils.helpers import build_station_folder_name

DEFAULT_CHECKS: dict[str, list[str]] = {
    "meteorological_conventional": [
        "schema_headers",
        "duplicates",
        "missing_dates",
        "missing_values",
        "trace_values",
        "invalid_numeric",
        "invalid_ranges",
        "negative_precipitation",
        "temp_max_below_temp_min",
    ],
    "meteorological_automatic": [
        "schema_headers",
        "duplicates",
        "missing_hours",
        "missing_values",
        "trace_values",
        "invalid_numeric",
        "invalid_ranges",
        "negative_precipitation",
    ],
    "hydrological_conventional": [
        "schema_headers",
        "duplicates",
        "missing_dates",
        "missing_values",
        "invalid_numeric",
        "invalid_ranges",
    ],
    "hydrological_automatic": [
        "schema_headers",
        "duplicates",
        "missing_hours",
        "missing_values",
        "trace_values",
        "invalid_numeric",
        "invalid_ranges",
        "negative_precipitation",
    ],
}

SCHEMA_HEADERS = {
    "meteorological_conventional": METEOROLOGICAL_CONVENTIONAL_HEADERS,
    "meteorological_automatic": METEOROLOGICAL_AUTOMATIC_HEADERS,
    "hydrological_conventional": HYDROLOGICAL_CONVENTIONAL_HEADERS,
    "hydrological_automatic": HYDROLOGICAL_AUTOMATIC_HEADERS,
}

SCHEMA_CONFIG = {
    "meteorological_conventional": {
        "frequency": "daily",
        "dedup_keys": ["Año", "Mes", "Día"],
    },
    "meteorological_automatic": {
        "frequency": "hourly",
        "dedup_keys": ["Año", "Mes", "Día", "Hora"],
    },
    "hydrological_conventional": {
        "frequency": "daily_observations",
        "dedup_keys": ["Año", "Mes", "Día"],
    },
    "hydrological_automatic": {
        "frequency": "hourly",
        "dedup_keys": ["Año", "Mes", "Día", "Hora"],
    },
}

VALID_RANGES: dict[str, tuple[float, float]] = {
    "Temp. Máx (°C)": (-30, 60),
    "Temp. Mín (°C)": (-40, 50),
    "Temperatura (°C)": (-40, 60),
    "Humedad (%)": (0, 100),
    "Precipitación (mm)": (0, 1000),
    "Precipitación (mm/hora)": (0, 300),
    "Dir. Viento (°)": (0, 360),
    "Vel. Viento (m/s)": (0, 100),
    "Nivel del río (m)": (0, 100),
    "Nivel del río (m) 06": (0, 100),
    "Nivel del río (m) 10": (0, 100),
    "Nivel del río (m) 14": (0, 100),
    "Nivel del río (m) 18": (0, 100),
}


SeverityFilter = Literal["all", "info", "warning", "critical"]


def _parse_row_datetime(row: dict) -> tuple[int, int, int, int | None] | None:
    try:
        year = int(row.get("Año", 0))
        month = int(row.get("Mes", 0))
        day = int(row.get("Día", 0))
        hour_raw = row.get("Hora")
        hour = (
            None
            if hour_raw is None or str(hour_raw).strip() == ""
            else int(str(hour_raw).strip().split(":")[0])
        )
        return (year, month, day, hour)
    except (ValueError, TypeError):
        return None


def _row_date_iso(row: dict) -> str | None:
    parsed = _parse_row_datetime(row)
    return None if not parsed else f"{parsed[0]:04d}-{parsed[1]:02d}-{parsed[2]:02d}"


def _row_hour_label(row: dict) -> str | None:
    parsed = _parse_row_datetime(row)
    return None if not parsed or parsed[3] is None else f"{parsed[3]:02d}:00"


def _filter_rows_by_period(
    rows: list[dict],
    year: int | None,
    month: int | None,
    start_year: int | None,
    end_year: int | None,
) -> list[dict]:
    filtered = []
    for row in rows:
        parsed = _parse_row_datetime(row)
        if not parsed:
            continue
        row_year, row_month, _row_day, _row_hour = parsed
        if year is not None and row_year != year:
            continue
        if month is not None and row_month != month:
            continue
        if start_year is not None and row_year < start_year:
            continue
        if end_year is not None and row_year > end_year:
            continue
        filtered.append(row)
    return filtered


def _get_expected_keys(
    frequency: str,
    year: int | None,
    month: int | None,
    start_year: int | None,
    end_year: int | None,
) -> set[tuple[int, int, int, int | None]]:
    if year is not None:
        min_year = max_year = year
    else:
        min_year = start_year
        max_year = end_year
    if min_year is None or max_year is None:
        return set()

    expected = set()
    for y in range(min_year, max_year + 1):
        months = (
            [month] if year is not None and month is not None else list(range(1, 13))
        )
        for m in months:
            if m is None:
                continue
            for d in range(1, calendar.monthrange(y, m)[1] + 1):
                if frequency == "hourly":
                    for h in range(24):
                        expected.add((y, m, d, h))
                else:
                    expected.add((y, m, d, None))
    return expected


def _build_recommendation(summary: DataQualitySummary) -> str:
    if summary.critical > 0:
        return "El periodo presenta problemas criticos. No se recomienda usarlo sin revision."
    if summary.warning > 0:
        return "El periodo puede usarse con precaucion. Revise los warnings antes de comparar o reportar."
    if summary.info > 0:
        return "El periodo es utilizable. Existen observaciones informativas de calidad de datos."
    return "No se detectaron anomalias relevantes en el periodo evaluado."


def _find_primary_csv_file(
    station: Station, year: int | None, month: int | None, start_year: int | None
) -> Path | None:
    if year is not None:
        return find_csv_file(station, year, month)
    if start_year is not None:
        return find_csv_file(station, start_year, None)
    station_folder_name = build_station_folder_name(station)
    station_dir = Path(settings.CSV_DIR).resolve() / station_folder_name
    if not station_dir.exists():
        return None
    files = sorted(station_dir.glob("*.csv"))
    return files[0] if files else None


def validate_dataset(
    rows: list[dict],
    headers: list[str],
    schema_kind: str,
    year: int | None = None,
    month: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    checks: list[str] | None = None,
    trace_policy: TracePolicy = "as_0_05",
    severity: SeverityFilter = "all",
) -> tuple[DataQualitySummary, list[AnomalyIssue]]:
    """
    Valida calidad de datos sobre filas ya cargadas y filtradas por periodo.

    Reutilizable por summarize_station_data sin volver a leer el CSV.
    """
    schema_frequency = SCHEMA_CONFIG[schema_kind]["frequency"]
    active_checks = checks or DEFAULT_CHECKS[schema_kind]
    period_rows = rows

    issues: list[AnomalyIssue] = []
    duplicate_rows = 0
    missing_values = 0
    trace_values = 0
    invalid_values = 0

    if "schema_headers" in active_checks:
        missing_headers = [h for h in SCHEMA_HEADERS[schema_kind] if h not in headers]
        if missing_headers:
            issues.append(
                AnomalyIssue(
                    code="SCHEMA_NOT_SUPPORTED",
                    severity="critical",
                    message="El esquema del CSV no coincide con un formato soportado.",
                    details={
                        "missing_headers": missing_headers,
                        "expected": SCHEMA_HEADERS[schema_kind],
                    },
                )
            )

    if "duplicates" in active_checks:
        dedup_keys = SCHEMA_CONFIG[schema_kind]["dedup_keys"]
        grouped: dict[tuple[str, ...], list[int]] = {}
        for row_idx, row in enumerate(period_rows, start=1):
            key = tuple(str(row.get(k, "")).strip() for k in dedup_keys)
            grouped.setdefault(key, []).append(row_idx)
        for key, idxs in grouped.items():
            if len(idxs) < 2:
                continue
            duplicate_rows += len(idxs) - 1
            date_label = None
            hour_label = None
            try:
                date_label = f"{int(key[0]):04d}-{int(key[1]):02d}-{int(key[2]):02d}"
                if len(key) > 3 and str(key[3]).strip() != "":
                    hour_label = f"{int(str(key[3]).split(':')[0]):02d}:00"
            except (ValueError, IndexError):
                pass
            if schema_frequency == "hourly":
                code = "DUPLICATE_DATETIME"
                message = f"La fecha-hora {date_label or key} {hour_label or ''} aparece {len(idxs)} veces.".strip()
            else:
                code = "DUPLICATE_DATE"
                message = f"La fecha {date_label or key} aparece {len(idxs)} veces."
            issues.append(
                AnomalyIssue(
                    code=code,
                    severity="warning",
                    message=message,
                    value=date_label or str(key),
                    date=date_label,
                    hour=hour_label,
                    rows=idxs,
                    details={"dedup_key": dedup_keys},
                )
            )

    check_missing_dates = (
        "missing_dates" in active_checks and schema_frequency != "hourly"
    )
    check_missing_hours = (
        "missing_hours" in active_checks and schema_frequency == "hourly"
    )
    if check_missing_dates or check_missing_hours:
        expected = _get_expected_keys(
            schema_frequency, year, month, start_year, end_year
        )
        present = set()
        for row in period_rows:
            parsed = _parse_row_datetime(row)
            if not parsed:
                continue
            present.add(
                parsed
                if schema_frequency == "hourly"
                else (parsed[0], parsed[1], parsed[2], None)
            )
        for y, m, d, h in sorted(expected - present):
            if h is None:
                issues.append(
                    AnomalyIssue(
                        code="MISSING_DATE",
                        severity="warning",
                        message=f"Falta el registro para {y:04d}-{m:02d}-{d:02d}.",
                        date=f"{y:04d}-{m:02d}-{d:02d}",
                    )
                )
            else:
                issues.append(
                    AnomalyIssue(
                        code="MISSING_HOUR",
                        severity="warning",
                        message=f"Falta el registro para {y:04d}-{m:02d}-{d:02d} {h:02d}:00.",
                        date=f"{y:04d}-{m:02d}-{d:02d}",
                        hour=f"{h:02d}:00",
                    )
                )

    numeric_fields = [h for h in headers if h not in {"Año", "Mes", "Día", "Hora"}]
    missing_occurrences: list[tuple[int, str, str | None, str | None]] = []

    for row_idx, row in enumerate(period_rows, start=1):
        row_date = _row_date_iso(row)
        row_hour = _row_hour_label(row)
        normalized_values: dict[str, dict[str, Any]] = {}

        for field in numeric_fields:
            normalized = normalize_special_value(row.get(field), field, trace_policy)
            normalized_values[field] = normalized
            flag = normalized["flag"]

            if flag == "missing":
                missing_values += 1
                missing_occurrences.append((row_idx, field, row_date, row_hour))
                continue
            if flag == "trace":
                trace_values += 1
                if "trace_values" in active_checks:
                    issues.append(
                        AnomalyIssue(
                            code="TRACE_PRECIPITATION",
                            severity="info",
                            message=f"Se detecto T en {field}. Fue tratado como {normalized['value']} para analisis.",
                            field=field,
                            value="T",
                            date=row_date,
                            hour=row_hour,
                            rows=[row_idx],
                            details={"trace_policy": trace_policy},
                        )
                    )
                continue
            if flag == "invalid_trace_field":
                invalid_values += 1
                issues.append(
                    AnomalyIssue(
                        code="INVALID_TRACE_FIELD",
                        severity="warning",
                        message=f"Se detecto T en campo no compatible: {field}.",
                        field=field,
                        value="T",
                        date=row_date,
                        hour=row_hour,
                        rows=[row_idx],
                    )
                )
                continue
            if flag == "invalid":
                invalid_values += 1
                if "invalid_numeric" in active_checks:
                    issues.append(
                        AnomalyIssue(
                            code="INVALID_NUMERIC_VALUE",
                            severity="warning",
                            message=f"Valor no numerico no reconocido en {field}.",
                            field=field,
                            value=row.get(field),
                            date=row_date,
                            hour=row_hour,
                            rows=[row_idx],
                        )
                    )
                continue

            value = normalized["value"]
            if value is None:
                continue

            if "invalid_ranges" in active_checks and field in VALID_RANGES:
                min_v, max_v = VALID_RANGES[field]
                if value < min_v or value > max_v:
                    issues.append(
                        AnomalyIssue(
                            code="VALUE_OUT_OF_RANGE",
                            severity="warning",
                            message=f"El valor {value} esta fuera del rango esperado para {field}.",
                            field=field,
                            value=value,
                            date=row_date,
                            hour=row_hour,
                            rows=[row_idx],
                            details={"min": min_v, "max": max_v},
                        )
                    )

            if (
                "negative_precipitation" in active_checks
                and "PRECIP" in field.upper()
                and value < 0
            ):
                issues.append(
                    AnomalyIssue(
                        code="NEGATIVE_PRECIPITATION",
                        severity="warning",
                        message=f"Se detecto precipitacion negativa en {field}.",
                        field=field,
                        value=value,
                        date=row_date,
                        hour=row_hour,
                        rows=[row_idx],
                    )
                )

        if (
            schema_kind == "meteorological_conventional"
            and "temp_max_below_temp_min" in active_checks
        ):
            tmax = normalized_values.get("Temp. Máx (°C)")
            tmin = normalized_values.get("Temp. Mín (°C)")
            if (
                tmax
                and tmin
                and tmax["value"] is not None
                and tmin["value"] is not None
                and tmax["value"] < tmin["value"]
            ):
                issues.append(
                    AnomalyIssue(
                        code="TEMP_MAX_BELOW_TEMP_MIN",
                        severity="warning",
                        message="La temperatura maxima es menor que la temperatura minima.",
                        date=row_date,
                        rows=[row_idx],
                        details={"temp_max": tmax["value"], "temp_min": tmin["value"]},
                    )
                )

    if "missing_values" in active_checks and missing_occurrences:
        per_field = Counter(field for _idx, field, _d, _h in missing_occurrences)
        total_missing = sum(per_field.values())
        missing_severity: Literal["info", "warning"] = (
            "warning"
            if total_missing >= max(5, int(len(period_rows) * 0.3))
            else "info"
        )
        if numeric_fields and total_missing >= len(period_rows) * len(numeric_fields):
            issues.append(
                AnomalyIssue(
                    code="FULL_PERIOD_MISSING",
                    severity="critical",
                    message=(
                        "El periodo analizado no presenta datos numericos "
                        "utilizables en ningun campo observado."
                    ),
                    details={
                        "missing_values": total_missing,
                        "fields": numeric_fields,
                    },
                )
            )
        for field, count in per_field.items():
            if count >= len(period_rows):
                issues.append(
                    AnomalyIssue(
                        code="FIELD_FULLY_MISSING",
                        severity="warning",
                        message=(
                            f"El campo {field} no tiene datos disponibles "
                            "en todo el periodo analizado."
                        ),
                        field=field,
                        details={"count": count, "rows_analyzed": len(period_rows)},
                    )
                )
                continue
            issues.append(
                AnomalyIssue(
                    code="MISSING_VALUE",
                    severity=missing_severity,
                    message=f"El campo {field} contiene {count} valor(es) faltante(s) (S/D o vacios).",
                    field=field,
                    details={"count": count},
                )
            )

    if severity != "all":
        issues = [issue for issue in issues if issue.severity == severity]

    expected_rows = None
    if (year is not None and month is not None) or (
        start_year is not None and end_year is not None
    ):
        expected_rows = len(
            _get_expected_keys(schema_frequency, year, month, start_year, end_year)
        )
    completeness_pct = (
        round((len(period_rows) / expected_rows) * 100, 1) if expected_rows else None
    )

    summary = DataQualitySummary(
        rows_analyzed=len(period_rows),
        expected_rows=expected_rows,
        issues_found=len(issues),
        critical=sum(1 for issue in issues if issue.severity == "critical"),
        warning=sum(1 for issue in issues if issue.severity == "warning"),
        info=sum(1 for issue in issues if issue.severity == "info"),
        duplicate_rows=duplicate_rows,
        missing_values=missing_values,
        trace_values=trace_values,
        invalid_values=invalid_values,
        completeness_pct=completeness_pct,
    )

    return summary, issues


def detect_anomalies(
    station_code: str,
    year: int | None = None,
    month: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    checks: list[str] | None = None,
    severity: SeverityFilter = "all",
    auto_download: bool = False,
    trace_policy: TracePolicy = "as_0_05",
) -> DetectAnomaliesResponse:
    """Detecta anomalias y problemas de calidad en datos descargados."""

    if month is not None and year is None:
        raise ValueError("month requiere year")
    if year is not None and (start_year is not None or end_year is not None):
        raise ValueError("Usa year/month o start_year/end_year, no ambos")
    if (start_year is None) != (end_year is None):
        raise ValueError("Debes enviar start_year y end_year juntos")
    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValueError("start_year no puede ser mayor que end_year")
    if severity not in {"all", "info", "warning", "critical"}:
        raise ValueError("severity debe ser all, info, warning o critical")
    if trace_policy not in {"as_0_05", "as_0", "as_null"}:
        raise ValueError("trace_policy debe ser as_0_05, as_0 o as_null")

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

    csv_file = _find_primary_csv_file(station, year, month, start_year)
    if not csv_file:
        if auto_download:
            raise ValueError(
                "No se encontró archivo local para el periodo. auto_download aún no está implementado."
            )
        raise ValueError(
            "No se encontró archivo local para el periodo solicitado. Descarga primero con scrape_station_data."
        )

    headers, all_rows = read_csv_data(csv_file)
    if not all_rows:
        summary = DataQualitySummary(
            rows_analyzed=0,
            expected_rows=0,
            issues_found=1,
            critical=1,
            warning=0,
            info=0,
            completeness_pct=0.0,
        )
        return DetectAnomaliesResponse(
            station=StationSummary(
                name=station.name,
                code=station.code,
                type=station.station_type,
                category=station.category,
                status=station.status,
            ),
            schema_data={"kind": "unknown", "frequency": "unknown"},
            period={
                "year": year,
                "month": month,
                "start_year": start_year,
                "end_year": end_year,
            },
            checks=checks or [],
            summary=summary,
            issues=[
                AnomalyIssue(
                    code="EMPTY_DATASET",
                    severity="critical",
                    message="El archivo CSV está vacío.",
                )
            ],
            recommendation=_build_recommendation(summary),
        )

    schema_kind = detect_schema(headers)
    schema_frequency = SCHEMA_CONFIG[schema_kind]["frequency"]
    active_checks = checks or DEFAULT_CHECKS[schema_kind]
    period_rows = _filter_rows_by_period(all_rows, year, month, start_year, end_year)
    if not period_rows:
        raise ValueError("No se encontraron filas para el periodo solicitado")

    summary, issues = validate_dataset(
        rows=period_rows,
        headers=headers,
        schema_kind=schema_kind,
        year=year,
        month=month,
        start_year=start_year,
        end_year=end_year,
        checks=active_checks,
        trace_policy=trace_policy,
        severity=severity,
    )

    return DetectAnomaliesResponse(
        station=station_info,
        schema_data={"kind": schema_kind, "frequency": schema_frequency},
        period={
            "year": year,
            "month": month,
            "start_year": start_year,
            "end_year": end_year,
        },
        checks=active_checks,
        summary=summary,
        issues=issues,
        recommendation=_build_recommendation(summary),
    )
