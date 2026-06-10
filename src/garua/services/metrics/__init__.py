"""Calculadores de métricas para cada tipo de esquema."""

from garua.utils.special_values import normalize_special_value

from .base import BaseMetricsCalculator, TracePolicy


class MeteorologicalConventionalCalculator(BaseMetricsCalculator):
    """Calculador para estaciones meteorológicas convencionales (datos diarios)."""

    schema_kind = "meteorological_conventional"
    frequency = "daily"

    def get_available_metrics(self) -> list[str]:
        return [
            "temp_max_avg",
            "temp_min_avg",
            "humidity_avg",
            "precip_total",
            "rainy_days",
            "dry_days",
            "missing_days",
            "trace_days",
            "max_daily_precip",
        ]

    def _get_schema_map(self) -> dict[str, str | list[str]]:
        precip = "Precipitación (mm)"
        return {
            "temp_max_avg": "Temp. Máx (°C)",
            "temp_min_avg": "Temp. Mín (°C)",
            "humidity_avg": "Humedad (%)",
            "precip_total": precip,
            "rainy_days": precip,
            "dry_days": precip,
            "missing_days": precip,
            "trace_days": precip,
            "max_daily_precip": precip,
        }

    def calculate_metric(
        self,
        metric_name: str,
        rows: list[dict],
        column_name: str | list[str],
        trace_policy: TracePolicy = "as_0_05",
    ) -> float | int | None:
        if isinstance(column_name, list):
            column_name = column_name[0]

        if metric_name in {"temp_max_avg", "temp_min_avg", "humidity_avg"}:
            values = self._extract_numeric_values(rows, column_name)
            return self._calculate_average(values)

        precip_metrics = {
            "precip_total": self._sum_precip,
            "rainy_days": self._count_precip_rainy,
            "dry_days": self._count_precip_dry,
            "missing_days": self._count_precip_missing,
            "trace_days": self._count_precip_trace,
            "max_daily_precip": self._max_precip,
        }
        if metric_name in precip_metrics:
            return precip_metrics[metric_name](rows, column_name)

        return None


class MeteorologicalAutomaticCalculator(BaseMetricsCalculator):
    """Calculador para estaciones meteorológicas automáticas (datos horarios)."""

    schema_kind = "meteorological_automatic"
    frequency = "hourly"

    def get_available_metrics(self) -> list[str]:
        return [
            "temp_avg",
            "temp_max",
            "temp_min",
            "humidity_avg",
            "precip_total",
            "rainy_hours",
            "rainy_days",
            "dry_hours",
            "missing_hours",
            "trace_hours",
            "wind_speed_avg",
            "wind_speed_max",
            "wind_direction_avg",
        ]

    def _get_schema_map(self) -> dict[str, str | list[str]]:
        precip = "Precipitación (mm)"
        return {
            "temp_avg": "Temperatura (°C)",
            "temp_max": "Temperatura (°C)",
            "temp_min": "Temperatura (°C)",
            "humidity_avg": "Humedad (%)",
            "precip_total": precip,
            "rainy_hours": precip,
            "rainy_days": precip,
            "dry_hours": precip,
            "missing_hours": precip,
            "trace_hours": precip,
            "wind_speed_avg": "Vel. Viento (m/s)",
            "wind_speed_max": "Vel. Viento (m/s)",
            "wind_direction_avg": "Dir. Viento (°)",
        }

    def calculate_metric(
        self,
        metric_name: str,
        rows: list[dict],
        column_name: str | list[str],
        trace_policy: TracePolicy = "as_0_05",
    ) -> float | int | None:
        if isinstance(column_name, list):
            column_name = column_name[0]

        if metric_name == "temp_avg":
            return self._calculate_average(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "temp_max":
            return self._calculate_max(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "temp_min":
            return self._calculate_min(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "humidity_avg":
            return self._calculate_average(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "precip_total":
            return self._sum_precip(rows, column_name)
        if metric_name == "rainy_hours":
            return self._count_precip_rainy(rows, column_name)
        if metric_name == "rainy_days":
            return self._count_unique_days(rows, column_name, trace_policy)
        if metric_name == "dry_hours":
            return self._count_precip_dry(rows, column_name)
        if metric_name == "missing_hours":
            return self._count_precip_missing(rows, column_name)
        if metric_name == "trace_hours":
            return self._count_precip_trace(rows, column_name)
        if metric_name == "wind_speed_avg":
            return self._calculate_average(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "wind_speed_max":
            return self._calculate_max(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "wind_direction_avg":
            return self._calculate_average(
                self._extract_numeric_values(rows, column_name)
            )

        return None


class HydrologicalConventionalCalculator(BaseMetricsCalculator):
    """Calculador para estaciones hidrológicas convencionales."""

    schema_kind = "hydrological_conventional"
    frequency = "daily_observations"

    def get_available_metrics(self) -> list[str]:
        return [
            "river_level_06_avg",
            "river_level_10_avg",
            "river_level_14_avg",
            "river_level_18_avg",
            "river_level_max",
            "river_level_min",
            "missing_days",
        ]

    def _get_schema_map(self) -> dict[str, str | list[str]]:
        level_cols = [
            "Nivel del río (m) 06",
            "Nivel del río (m) 10",
            "Nivel del río (m) 14",
            "Nivel del río (m) 18",
        ]
        return {
            "river_level_06_avg": "Nivel del río (m) 06",
            "river_level_10_avg": "Nivel del río (m) 10",
            "river_level_14_avg": "Nivel del río (m) 14",
            "river_level_18_avg": "Nivel del río (m) 18",
            "river_level_max": level_cols,
            "river_level_min": level_cols,
            "missing_days": level_cols,
        }

    def calculate_metric(
        self,
        metric_name: str,
        rows: list[dict],
        column_name: str | list[str],
        trace_policy: TracePolicy = "as_0_05",
    ) -> float | int | None:
        if metric_name == "missing_days":
            if isinstance(column_name, list):
                missing_dates = set()
                for col in column_name:
                    for row in rows:
                        norm = normalize_special_value(
                            row.get(col), col, trace_policy
                        )
                        if norm["flag"] == "missing":
                            year = row.get("Año", "")
                            month = row.get("Mes", "")
                            day = row.get("Día", "")
                            if year and month and day:
                                missing_dates.add(f"{year}-{month}-{day}")
                return len(missing_dates)
            return self._count_precip_missing(rows, column_name)

        if isinstance(column_name, list):
            values = self._extract_numeric_values_multi_columns(rows, column_name)
        else:
            values = self._extract_numeric_values(rows, column_name)

        if metric_name.endswith("_avg"):
            return self._calculate_average(values)
        if metric_name == "river_level_max":
            return self._calculate_max(values)
        if metric_name == "river_level_min":
            return self._calculate_min(values)

        return None


class HydrologicalAutomaticCalculator(BaseMetricsCalculator):
    """Calculador para estaciones hidrológicas automáticas (datos horarios)."""

    schema_kind = "hydrological_automatic"
    frequency = "hourly"

    def get_available_metrics(self) -> list[str]:
        return [
            "river_level_avg",
            "river_level_max",
            "river_level_min",
            "precip_total",
            "rainy_hours",
            "rainy_days",
            "dry_hours",
            "missing_hours",
            "trace_hours",
            "max_hourly_precip",
        ]

    def _get_schema_map(self) -> dict[str, str | list[str]]:
        precip = "Precipitación (mm/hora)"
        return {
            "river_level_avg": "Nivel del río (m)",
            "river_level_max": "Nivel del río (m)",
            "river_level_min": "Nivel del río (m)",
            "precip_total": precip,
            "rainy_hours": precip,
            "rainy_days": precip,
            "dry_hours": precip,
            "missing_hours": precip,
            "trace_hours": precip,
            "max_hourly_precip": precip,
        }

    def calculate_metric(
        self,
        metric_name: str,
        rows: list[dict],
        column_name: str | list[str],
        trace_policy: TracePolicy = "as_0_05",
    ) -> float | int | None:
        if isinstance(column_name, list):
            column_name = column_name[0]

        if metric_name == "river_level_avg":
            return self._calculate_average(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "river_level_max":
            return self._calculate_max(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "river_level_min":
            return self._calculate_min(
                self._extract_numeric_values(rows, column_name)
            )
        if metric_name == "precip_total":
            return self._sum_precip(rows, column_name)
        if metric_name == "rainy_hours":
            return self._count_precip_rainy(rows, column_name)
        if metric_name == "rainy_days":
            return self._count_unique_days(rows, column_name, trace_policy)
        if metric_name == "dry_hours":
            return self._count_precip_dry(rows, column_name)
        if metric_name == "missing_hours":
            return self._count_precip_missing(rows, column_name)
        if metric_name == "trace_hours":
            return self._count_precip_trace(rows, column_name)
        if metric_name == "max_hourly_precip":
            return self._max_precip(rows, column_name)

        return None


def get_metrics_calculator(schema_kind: str) -> BaseMetricsCalculator:
    """
    Retorna el calculador apropiado para un esquema.

    Args:
        schema_kind: Tipo de esquema

    Returns:
        Calculador de métricas

    Raises:
        ValueError: Si el esquema no es soportado
    """
    calculators = {
        "meteorological_conventional": MeteorologicalConventionalCalculator,
        "meteorological_automatic": MeteorologicalAutomaticCalculator,
        "hydrological_conventional": HydrologicalConventionalCalculator,
        "hydrological_automatic": HydrologicalAutomaticCalculator,
    }

    calculator_class = calculators.get(schema_kind)
    if not calculator_class:
        raise ValueError(f"Esquema no soportado: {schema_kind}")

    return calculator_class()
