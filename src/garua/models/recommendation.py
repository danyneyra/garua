"""Modelos para el sistema de recomendación de estaciones."""

from typing import Literal

from pydantic import BaseModel, Field


class RecommendationCriteria(BaseModel):
    """Criterios para recomendar estaciones cercanas a un punto."""

    lat: float = Field(..., ge=-90, le=90, description="Latitud del punto de interés")
    lon: float = Field(
        ..., ge=-180, le=180, description="Longitud del punto de interés"
    )
    radius_km: float = Field(
        default=100, gt=0, le=500, description="Radio máximo de búsqueda en kilómetros"
    )
    station_type: Literal["M", "H", "all"] = Field(
        default="M",
        description="Tipo de estación: M (meteorológica), H (hidrológica), all (ambas)",
    )
    target_altitude: float | None = Field(
        default=None,
        ge=-500,
        le=7000,
        description="Altitud del proyecto o punto de interés en msnm",
    )
    prefer_status: list[str] | None = Field(
        default=None,
        description="Orden de prioridad de estados operativos",
    )
    min_years_available: int | None = Field(
        default=None, ge=0, description="Mínimo de años de datos históricos requeridos"
    )
    limit: int = Field(
        default=5, ge=1, le=20, description="Cantidad máxima de recomendaciones"
    )


class StationRecommendation(BaseModel):
    """Recomendación de estación con score y explicación."""

    name: str
    code: str
    type: str
    category: str | None = None
    status: str
    latitude: float
    longitude: float
    department: str | None = None
    province: str | None = None
    district: str | None = None
    altitude: float | None = None
    data_available_since: str | None = None
    years_available: int | None = None
    distance_km: float = Field(..., description="Distancia al punto de interés en km")
    altitude_difference_m: float | None = Field(
        None, description="Diferencia de altitud con el punto objetivo en metros"
    )
    score: float = Field(..., ge=0, le=100, description="Score total de 0 a 100")
    reason: str = Field(..., description="Explicación de por qué se recomienda")
    score_breakdown: dict[str, float] = Field(
        ..., description="Desglose detallado del score por componente"
    )


class RecommendationResponse(BaseModel):
    """Respuesta del sistema de recomendación."""

    recommended: StationRecommendation | None = Field(
        None, description="Estación recomendada principal, si existe"
    )
    alternatives: list[StationRecommendation] = Field(
        default_factory=list, description="Estaciones alternativas ordenadas por score"
    )
    criteria: dict = Field(..., description="Criterios utilizados para la búsqueda")
    total_candidates: int = Field(
        ..., description="Total de estaciones candidatas encontradas"
    )
    message: str = Field(..., description="Mensaje descriptivo del resultado")
