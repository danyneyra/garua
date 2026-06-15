"""Modelos para detección de anomalías en datos SENAMHI."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from garua.models.station import StationSummary


Severity = Literal["info", "warning", "critical"]


class DataQualitySummary(BaseModel):
    """Resumen agregado de calidad de datos."""

    rows_analyzed: int = Field(..., ge=0)
    expected_rows: int | None = Field(default=None, ge=0)
    issues_found: int = Field(..., ge=0)
    critical: int = Field(default=0, ge=0)
    warning: int = Field(default=0, ge=0)
    info: int = Field(default=0, ge=0)
    duplicate_rows: int = Field(default=0, ge=0)
    missing_values: int = Field(default=0, ge=0)
    trace_values: int = Field(default=0, ge=0)
    invalid_values: int = Field(default=0, ge=0)
    completeness_pct: float | None = Field(default=None, ge=0, le=100)


class AnomalyIssue(BaseModel):
    """Issue puntual detectado durante validación."""

    code: str
    severity: Severity
    message: str
    field: str | None = None
    value: Any | None = None
    date: str | None = None
    hour: str | None = None
    rows: list[int] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)


class DetectAnomaliesResponse(BaseModel):
    """Respuesta principal de detect_anomalies."""

    station: StationSummary
    schema_data: dict
    period: dict
    checks: list[str]
    summary: DataQualitySummary
    issues: list[AnomalyIssue]
    recommendation: str | None = None
