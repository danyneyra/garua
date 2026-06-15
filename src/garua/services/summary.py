"""Servicio de resumen de datos para una estación y periodo."""

from garua.models.summary import (
    SummaryPeriod,
    SummaryQuality,
    SummaryResponse,
    SummaryWarning,
    StationSummary,
)
from garua.services.anomaly import (
    _filter_rows_by_period,
    _find_primary_csv_file,
    validate_dataset,
)
from garua.services.comparison import (
    STATION_SCHEMA_MAP,
    deduplicate_rows,
    detect_schema,
    read_csv_data,
)
from garua.services.metrics import get_metrics_calculator
from garua.services.station import find_station_by_code
from garua.utils.special_values import TracePolicy
from garua.utils.helpers import fmt, plural

_MONTH_NAMES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def resolve_summary_period(
    year: int | None,
    month: int | None,
    start_year: int | None,
    end_year: int | None,
) -> SummaryPeriod:
    """Valida y resuelve el periodo solicitado con etiqueta legible."""
    if month is not None and year is None:
        raise ValueError("month requiere year")
    if year is not None and (start_year is not None or end_year is not None):
        raise ValueError("Usa year/month o start_year/end_year, no ambos")
    if (start_year is None) != (end_year is None):
        raise ValueError("Debes enviar start_year y end_year juntos")
    if start_year is not None and end_year is not None and start_year > end_year:
        raise ValueError("start_year no puede ser mayor que end_year")
    if year is None and start_year is None:
        raise ValueError("Debes especificar year o start_year/end_year")

    label = _build_period_label(year, month, start_year, end_year)
    return SummaryPeriod(
        year=year,
        month=month,
        start_year=start_year,
        end_year=end_year,
        label=label,
    )


def _build_period_label(
    year: int | None,
    month: int | None,
    start_year: int | None,
    end_year: int | None,
) -> str:
    if year is not None and month is not None:
        return f"{_MONTH_NAMES[month]} {year}"
    if year is not None:
        return str(year)
    if start_year is not None and end_year is not None:
        if start_year == end_year:
            return str(start_year)
        return f"{start_year}-{end_year}"
    return "Periodo"


def _compact_quality_warnings(issues: list) -> list[SummaryWarning]:
    """Convierte issues de calidad en warnings compactos para el resumen."""
    warnings: list[SummaryWarning] = []
    seen_codes: set[str] = set()

    for issue in issues:
        if issue.severity == "info" and issue.code in {
            "TRACE_PRECIPITATION",
            "MISSING_VALUE",
        }:
            continue
        key = f"{issue.code}:{issue.field or ''}"
        if key in seen_codes:
            continue
        seen_codes.add(key)
        warnings.append(
            SummaryWarning(
                code=issue.code,
                message=issue.message,
                details={"severity": issue.severity, **(issue.details or {})},
            )
        )
        if len(warnings) >= 10:
            break

    return warnings


def build_summary_text(
    period: SummaryPeriod,
    schema_kind: str,
    metrics: dict[str, float | int | None],
    quality: SummaryQuality | None,
) -> str:
    """Genera un resumen narrativo breve según el esquema detectado."""
    label = period.label or "El periodo"
    parts: list[str] = []

    if schema_kind == "meteorological_conventional":
        precip = metrics.get("precip_total")
        rainy = metrics.get("rainy_days")
        humidity = metrics.get("humidity_avg")

        if precip is not None:
            parts.append(f"precipitación acumulada de {fmt(precip)} mm")
        if rainy is not None:
            day_word = plural(rainy, "día", "días")
            parts.append(f"{fmt(rainy, 0)} {day_word} con lluvia")
        if humidity is not None:
            parts.append(f"humedad promedio de {fmt(humidity)}%")

    elif schema_kind == "meteorological_automatic":
        temp = metrics.get("temp_avg")
        rainy_hours = metrics.get("rainy_hours")
        wind_max = metrics.get("wind_speed_max")

        if temp is not None:
            parts.append(f"temperatura promedio de {fmt(temp, 2)} °C")
        if rainy_hours is not None:
            hour_word = plural(rainy_hours, "hora", "horas")
            parts.append(f"{fmt(rainy_hours, 0)} {hour_word} con lluvia")
        if wind_max is not None:
            parts.append(f"velocidad máxima de viento de {fmt(wind_max, 2)} m/s")

    elif schema_kind == "hydrological_conventional":
        level_min = metrics.get("river_level_min")
        level_max = metrics.get("river_level_max")

        if level_min is not None and level_max is not None:
            parts.append(
                f"el nivel del río se mantuvo entre {fmt(level_min)} m y {fmt(level_max)} m"
            )

        levels = {
            "06": metrics.get("river_level_06_avg"),
            "10": metrics.get("river_level_10_avg"),
            "14": metrics.get("river_level_14_avg"),
            "18": metrics.get("river_level_18_avg"),
        }
        valid_levels = {
            hour: value for hour, value in levels.items() if value is not None
        }

        if valid_levels:
            peak_hour, peak_value = max(valid_levels.items(), key=lambda item: item[1])
            parts.append(
                f"el mayor promedio se registró a las {peak_hour} horas ({fmt(peak_value)} m)"
            )

    elif schema_kind == "hydrological_automatic":
        level_avg = metrics.get("river_level_avg")
        level_max = metrics.get("river_level_max")
        rainy_hours = metrics.get("rainy_hours")

        if level_avg is not None:
            parts.append(f"nivel promedio de {fmt(level_avg, 2)} m")
        if level_max is not None:
            parts.append(f"máximo de {fmt(level_max, 2)} m")
        if rainy_hours is not None:
            hour_word = plural(rainy_hours, "hora", "horas")
            parts.append(f"{fmt(rainy_hours, 0)} {hour_word} con precipitación")

    if not parts:
        return f"{label} no tiene suficientes métricas para generar un resumen."

    text = f"{label} presentó " + ", ".join(parts) + "."
    if quality and quality.critical > 0:
        text += " Se detectaron problemas críticos de calidad de datos."
    elif quality and quality.warning > 0:
        text += " Revise los warnings de calidad antes de usar estos valores."
    elif (
        quality
        and quality.completeness_pct is not None
        and quality.completeness_pct < 90
    ):
        text += f" La completitud de datos fue de {fmt(quality.completeness_pct, 2)}%."

    return text


def summarize_station_data(
    station_code: str,
    year: int | None = None,
    month: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    metrics: list[str] | None = None,
    include_quality: bool = True,
    auto_download: bool = False,
    trace_policy: TracePolicy = "as_0_05",
) -> SummaryResponse:
    """Resume datos SENAMHI de una estación para un periodo específico."""
    if trace_policy not in {"as_0_05", "as_0", "as_null"}:
        raise ValueError("trace_policy debe ser as_0_05, as_0 o as_null")

    warnings: list[SummaryWarning] = []
    period = resolve_summary_period(year, month, start_year, end_year)

    station = find_station_by_code(station_code)
    if not station:
        raise ValueError(f"Estación '{station_code}' no encontrada")

    station_info = StationSummary(
        name=station.name,
        code=station.code,
        type=station.station_type,
        category=station.category,
        status=station.status,
    )

    csv_file = _find_primary_csv_file(station, year, month, start_year)
    if not csv_file:
        if auto_download:
            raise ValueError(
                "No se encontró archivo local para el periodo. "
                "auto_download aún no está implementado."
            )
        raise ValueError(
            "No se encontró archivo local para el periodo solicitado. "
            "Descarga primero con scrape_station_data."
        )

    headers, all_rows = read_csv_data(csv_file)
    if not all_rows:
        raise ValueError("El archivo CSV está vacío")

    schema_kind = detect_schema(headers)
    schema_config = STATION_SCHEMA_MAP[schema_kind]

    period_rows = _filter_rows_by_period(all_rows, year, month, start_year, end_year)
    if not period_rows:
        raise ValueError("No se encontraron filas para el periodo solicitado")

    clean_rows, duplicates = deduplicate_rows(period_rows, schema_config["dedup_keys"])
    if duplicates > 0:
        warnings.append(
            SummaryWarning(
                code="DUPLICATE_ROWS",
                message=(
                    f"Se detectaron {duplicates} registros duplicados "
                    "y fueron eliminados antes de calcular métricas."
                ),
                details={"count": duplicates},
            )
        )

    calculator = get_metrics_calculator(schema_kind)
    available_metrics = calculator.get_available_metrics()

    if metrics is None:
        metrics_to_calculate = available_metrics
    else:
        metrics_to_calculate = [m for m in metrics if m in available_metrics]
        invalid_metrics = set(metrics) - set(available_metrics)
        for metric in sorted(invalid_metrics):
            warnings.append(
                SummaryWarning(
                    code="INVALID_METRIC_FOR_SCHEMA",
                    message=(f"La métrica {metric} no aplica para {schema_kind}."),
                    details={"metric": metric, "schema": schema_kind},
                )
            )

    if not metrics_to_calculate:
        raise ValueError("No hay métricas válidas para calcular")

    calculator_warnings_before = len(calculator.warnings)
    metric_values = calculator.summarize(
        clean_rows, metrics_to_calculate, trace_policy=trace_policy
    )
    for w in calculator.warnings[calculator_warnings_before:]:
        warnings.append(SummaryWarning(**w))

    quality: SummaryQuality | None = None
    if include_quality:
        quality_report, quality_issues = validate_dataset(
            rows=period_rows,
            headers=headers,
            schema_kind=schema_kind,
            year=year,
            month=month,
            start_year=start_year,
            end_year=end_year,
            trace_policy=trace_policy,
        )
        quality = SummaryQuality(
            completeness_pct=quality_report.completeness_pct,
            issues_found=quality_report.issues_found,
            critical=quality_report.critical,
            warning=quality_report.warning,
            info=quality_report.info,
            missing_values=quality_report.missing_values,
            trace_values=quality_report.trace_values,
            duplicate_rows=quality_report.duplicate_rows,
            invalid_values=quality_report.invalid_values,
        )
        warnings.extend(_compact_quality_warnings(quality_issues))

    summary_text = build_summary_text(
        period=period,
        schema_kind=schema_kind,
        metrics=metric_values,
        quality=quality,
    )

    return SummaryResponse(
        station=station_info,
        schema={
            "kind": schema_kind,
            "frequency": schema_config["frequency"],
        },
        period=period,
        rows=len(clean_rows),
        metrics=metric_values,
        quality=quality,
        warnings=warnings,
        summary=summary_text,
    )
