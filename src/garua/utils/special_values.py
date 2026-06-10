"""Normalización de valores especiales SENAMHI (S/D, T)."""

from typing import Any, Literal

TracePolicy = Literal["as_0_05", "as_0", "as_null"]


def normalize_special_value(
    raw_value: object, field: str, trace_policy: TracePolicy = "as_0_05"
) -> dict[str, Any]:
    """Normaliza valores especiales reportados por SENAMHI."""
    if raw_value is None:
        return {"raw": raw_value, "value": None, "flag": "missing"}

    text = str(raw_value).strip()
    text_upper = text.upper()

    if text_upper in {"", "S/D", "SD", "SIN DATOS"}:
        return {"raw": raw_value, "value": None, "flag": "missing"}

    if text_upper == "T":
        if "PRECIP" not in field.upper():
            return {"raw": raw_value, "value": None, "flag": "invalid_trace_field"}
        trace_value = (
            0.05
            if trace_policy == "as_0_05"
            else (0.0 if trace_policy == "as_0" else None)
        )
        return {"raw": raw_value, "value": trace_value, "flag": "trace"}

    try:
        return {
            "raw": raw_value,
            "value": float(text.replace(",", ".")),
            "flag": "valid",
        }
    except ValueError:
        return {"raw": raw_value, "value": None, "flag": "invalid"}
