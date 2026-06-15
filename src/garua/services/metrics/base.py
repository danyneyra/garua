"""Sistema de cálculo de métricas para diferentes esquemas de estaciones."""

from abc import ABC, abstractmethod

from garua.utils.special_values import TracePolicy, normalize_special_value


class BaseMetricsCalculator(ABC):
    """Calculador base de métricas para un esquema específico."""

    schema_kind: str = ""
    frequency: str = ""

    def __init__(self):
        self.warnings = []
        self._trace_policy: TracePolicy = "as_0_05"

    @abstractmethod
    def get_available_metrics(self) -> list[str]:
        """Retorna lista de métricas disponibles para este esquema."""
        pass

    @abstractmethod
    def calculate_metric(
        self,
        metric_name: str,
        rows: list[dict],
        column_name: str | list[str],
        trace_policy: TracePolicy = "as_0_05",
    ) -> float | int | None:
        """
        Calcula una métrica específica.

        Args:
            metric_name: Nombre de la métrica
            rows: Registros del periodo
            column_name: Nombre(s) de columna(s) a procesar
            trace_policy: Política para trazas T en precipitación

        Returns:
            Valor calculado o None si no hay datos
        """
        pass

    def summarize(
        self,
        rows: list[dict],
        metrics: list[str],
        trace_policy: TracePolicy = "as_0_05",
    ) -> dict[str, float | int | None]:
        """
        Calcula todas las métricas solicitadas.

        Args:
            rows: Registros del periodo
            metrics: Lista de métricas a calcular
            trace_policy: Política para trazas T en precipitación

        Returns:
            Diccionario con resultados
        """
        self._trace_policy = trace_policy
        results = {}
        schema_map = self._get_schema_map()

        for metric in metrics:
            if metric not in schema_map:
                self.warnings.append(
                    {
                        "code": "INVALID_METRIC_FOR_SCHEMA",
                        "message": f"La métrica '{metric}' no aplica para {self.schema_kind}.",
                        "details": {"metric": metric, "schema": self.schema_kind},
                    }
                )
                continue

            column_name = schema_map[metric]
            results[metric] = self.calculate_metric(
                metric, rows, column_name, trace_policy=trace_policy
            )

        return results

    @abstractmethod
    def _get_schema_map(self) -> dict[str, str | list[str]]:
        """Retorna el mapeo de métricas a columnas."""
        pass

    def _extract_numeric_values(
        self, rows: list[dict], column_name: str
    ) -> list[float]:
        """Extrae valores numéricos válidos de una columna (excluye S/D y T)."""
        values = []
        for row in rows:
            val = row.get(column_name, "")
            if val == "" or val is None:
                continue

            try:
                num_val = float(str(val).replace(",", ".").strip())
                values.append(num_val)
            except (ValueError, AttributeError):
                continue

        return values

    def _extract_precip_values(
        self,
        rows: list[dict],
        column_name: str,
        trace_policy: TracePolicy = "as_0_05",
    ) -> list[dict]:
        """Normaliza valores de precipitación respetando S/D y T."""
        normalized = []
        for row in rows:
            result = normalize_special_value(
                row.get(column_name), column_name, trace_policy
            )
            normalized.append(result)
        return normalized

    def _extract_numeric_values_multi_columns(
        self, rows: list[dict], column_names: list[str]
    ) -> list[float]:
        """Extrae valores numéricos de múltiples columnas."""
        values = []
        for col in column_names:
            values.extend(self._extract_numeric_values(rows, col))
        return values

    def _calculate_average(self, values: list[float]) -> float | None:
        """Calcula promedio."""
        if not values:
            return None
        return round(sum(values) / len(values), 2)

    def _calculate_sum(self, values: list[float]) -> float | None:
        """Calcula suma."""
        if not values:
            return None
        return round(sum(values), 2)

    def _calculate_max(self, values: list[float]) -> float | None:
        """Calcula máximo."""
        if not values:
            return None
        return round(max(values), 2)

    def _calculate_min(self, values: list[float]) -> float | None:
        """Calcula mínimo."""
        if not values:
            return None
        return round(min(values), 2)

    def _count_positive(self, values: list[float]) -> int:
        """Cuenta valores mayores a 0."""
        return sum(1 for v in values if v > 0)

    def _count_precip_rainy(self, rows: list[dict], column_name: str) -> int:
        """Cuenta registros con lluvia (>0 o traza T)."""
        count = 0
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, self._trace_policy
            )
            if norm["flag"] == "trace":
                count += 1
            elif norm["flag"] == "valid" and norm["value"] is not None and norm["value"] > 0:
                count += 1
        return count

    def _count_precip_dry(self, rows: list[dict], column_name: str) -> int:
        """Cuenta registros secos (0.0 exacto, no S/D ni T)."""
        count = 0
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, self._trace_policy
            )
            if norm["flag"] == "valid" and norm["value"] == 0.0:
                count += 1
        return count

    def _count_precip_missing(self, rows: list[dict], column_name: str) -> int:
        """Cuenta registros con dato faltante S/D."""
        count = 0
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, self._trace_policy
            )
            if norm["flag"] == "missing":
                count += 1
        return count

    def _count_precip_trace(self, rows: list[dict], column_name: str) -> int:
        """Cuenta registros con traza T."""
        count = 0
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, self._trace_policy
            )
            if norm["flag"] == "trace":
                count += 1
        return count

    def _sum_precip(self, rows: list[dict], column_name: str) -> float | None:
        """Suma precipitación normalizada (T según trace_policy, S/D excluido)."""
        total = 0.0
        has_value = False
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, self._trace_policy
            )
            if norm["value"] is not None:
                total += norm["value"]
                has_value = True
        return round(total, 2) if has_value else None

    def _max_precip(self, rows: list[dict], column_name: str) -> float | None:
        """Máximo de precipitación normalizada."""
        values = []
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, self._trace_policy
            )
            if norm["value"] is not None:
                values.append(norm["value"])
        return self._calculate_max(values)

    def _count_unique_days(
        self, rows: list[dict], column_name: str, trace_policy: TracePolicy = "as_0_05"
    ) -> int:
        """Cuenta días únicos con precipitación > 0 o traza T."""
        rainy_days = set()
        for row in rows:
            norm = normalize_special_value(
                row.get(column_name), column_name, trace_policy
            )
            is_rainy = norm["flag"] == "trace" or (
                norm["flag"] == "valid"
                and norm["value"] is not None
                and norm["value"] > 0
            )
            if is_rainy:
                year = row.get("Año", "")
                month = row.get("Mes", "")
                day = row.get("Día", "")
                if year and month and day:
                    rainy_days.add(f"{year}-{month}-{day}")

        return len(rainy_days)
