"""Modelos para comparación de periodos de datos."""

from typing import Any

from pydantic import BaseModel, Field

from garua.models.station import StationSummary


class ComparisonPeriod(BaseModel):
    """Periodo a comparar."""

    label: str = Field(..., description="Etiqueta descriptiva del periodo")
    year: int = Field(..., ge=1900, le=2100, description="Año del periodo")
    month: int | None = Field(
        default=None, ge=1, le=12, description="Mes específico (opcional)"
    )


class ComparisonWarning(BaseModel):
    """Warning detectado durante la comparación."""

    code: str = Field(..., description="Código del warning")
    message: str = Field(..., description="Mensaje descriptivo")
    details: dict[str, Any] | None = Field(
        default=None, description="Información adicional"
    )


class PeriodSummary(BaseModel):
    """Resumen de métricas para un periodo."""

    label: str = Field(..., description="Etiqueta del periodo")
    year: int = Field(..., description="Año del periodo")
    month: int | None = Field(default=None, description="Mes del periodo")
    rows: int = Field(..., ge=0, description="Número de registros procesados")
    valid_rows: int = Field(
        ..., ge=0, description="Número de registros válidos para cálculos"
    )
    metrics: dict[str, float | int | None] = Field(
        default_factory=dict, description="Métricas calculadas"
    )


class PeriodDifference(BaseModel):
    """Diferencia entre dos periodos."""

    from_label: str = Field(..., description="Periodo de referencia")
    to_label: str = Field(..., description="Periodo de comparación")
    deltas: dict[str, float | int | None] = Field(
        default_factory=dict, description="Diferencias por métrica"
    )
    percent_changes: dict[str, float | None] = Field(
        default_factory=dict, description="Cambios porcentuales"
    )


class SchemaInfo(BaseModel):
    """Información del esquema detectado."""

    kind: str = Field(..., description="Tipo de esquema detectado")
    frequency: str = Field(..., description="Frecuencia de datos (daily/hourly)")
    headers: list[str] = Field(default_factory=list, description="Headers del CSV")
    available_metrics: list[str] = Field(
        default_factory=list, description="Métricas disponibles para este esquema"
    )


class ComparePeriodsResponse(BaseModel):
    """Respuesta de la comparación de periodos."""

    station: StationSummary = Field(..., description="Información de la estación")
    schema_info: SchemaInfo = Field(
        ..., description="Esquema detectado", alias="schema"
    )
    periods: list[PeriodSummary] = Field(
        default_factory=list, description="Resúmenes de cada periodo"
    )
    differences: list[PeriodDifference] = Field(
        default_factory=list, description="Diferencias entre periodos consecutivos"
    )
    warnings: list[ComparisonWarning] = Field(
        default_factory=list, description="Warnings detectados"
    )
    summary: str | None = Field(
        default=None, description="Resumen interpretativo en español"
    )
