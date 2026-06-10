"""Modelos para resumen de datos de estaciones SENAMHI."""

from typing import Any

from pydantic import BaseModel, Field

from garua.models.station import StationSummary


class SummaryPeriod(BaseModel):
    """Periodo resumido."""

    year: int | None = None
    month: int | None = Field(default=None, ge=1, le=12)
    start_year: int | None = None
    end_year: int | None = None
    label: str | None = None


class SummaryQuality(BaseModel):
    """Resumen compacto de calidad de datos."""

    completeness_pct: float | None = None
    issues_found: int = 0
    critical: int = 0
    warning: int = 0
    info: int = 0
    missing_values: int = 0
    trace_values: int = 0
    duplicate_rows: int = 0
    invalid_values: int = 0


class SummaryWarning(BaseModel):
    """Warning emitido durante el resumen."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class SummaryResponse(BaseModel):
    """Respuesta de summarize_station_data."""

    station: StationSummary
    schema_info: dict = Field(..., alias="schema")
    period: SummaryPeriod
    rows: int = Field(..., ge=0)
    metrics: dict[str, float | int | None] = Field(default_factory=dict)
    quality: SummaryQuality | None = None
    warnings: list[SummaryWarning] = Field(default_factory=list)
    summary: str | None = None

    class Config:
        populate_by_name = True
