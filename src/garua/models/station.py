"""
Modelos de datos para representar estaciones meteorológicas e hidrológicas del SENAMHI.
Estos modelos se utilizan para estructurar la información de las estaciones, incluyendo su ubicación, categoría, tipo, estado operativo y disponibilidad de datos. También se incluyen validaciones para asegurar la integridad de los datos y métodos auxiliares para facilitar el acceso a la información relevante."""

from pydantic import BaseModel, Field, field_validator
from typing import Annotated, Optional, List
from enum import Enum


class StationCategory(str, Enum):
    """Categorías de estaciones meteorológicas e hidrológicas"""

    EAA = "EAA"  # Estación Agroclimática Automática
    PE = "PE"  # Pluviométrica Especial
    CP = "CP"  # Climatológica Principal
    HLM = "HLM"  # Hidrológica Limnimétrica
    MAP = "MAP"  # Meteorológica Automática Principal
    EHA = "EHA"  # Estación Hidrológica Automática
    EHMA = "EHMA"  # Estación Hidrometeorológica Automática
    CO = "CO"  # Climatológica Ordinaria
    EMA = "EMA"  # Estación Meteorológica Automática
    PLU = "PLU"  # Pluviométrica
    EAMA = "EAMA"  # Estación Agroclimática Automática (Modificada/Avanzada)
    HLG = "HLG"  # Hidrológica Limnigráfica


class StationType(str, Enum):
    """Tipo de estación: Meteorológica o Hidrológica"""

    METEOROLOGICAL = "M"  # Meteorológica
    HYDROLOGICAL = "H"  # Hidrológica


class StationStatus(str, Enum):
    """Estado operativo de la estación"""

    REAL_TIME = "REAL"  # Tiempo real
    DEFERRED = "DIFERIDO"  # Diferido
    AUTOMATIC = "AUTOMATICA"  # Automática


class Station(BaseModel):
    """
    Modelo que representa una estación meteorológica o hidrológica del SENAMHI.

    Atributos:
        name: Nombre de la estación
        category: Categoría de la estación (EMA, CO, etc.)
        latitude: Latitud en grados decimales
        longitude: Longitud en grados decimales
        altitude: Altitud en metros sobre el nivel del mar (opcional)
        station_type: Tipo M (Meteorológica) o H (Hidrológica)
        code: Código único de la estación
        legacy_code: Código anterior (opcional)
        frontend_code: Nuevo código de frontend para compatibilidad con versiones anteriores
        department: Departamento donde se ubica la estación
        province: Provincia donde se ubica la estación
        district: Distrito donde se ubica la estación
        status: Estado operativo de la estación
        data_available_since: Fecha desde la cual hay datos disponibles (opcional)
    """

    name: str = Field(..., alias="nom", description="Nombre de la estación")
    category: StationCategory = Field(
        ..., alias="cate", description="Categoría de la estación"
    )
    latitude: float = Field(
        ..., alias="lat", ge=-90, le=90, description="Latitud en grados decimales"
    )
    longitude: float = Field(
        ..., alias="lon", ge=-180, le=180, description="Longitud en grados decimales"
    )
    altitude: Optional[float] = Field(
        None,
        alias="alt",
        ge=-500,
        description="Altitud en metros sobre el nivel del mar",
    )
    department: Optional[str] = Field(
        None, alias="dep", description="Departamento donde se ubica la estación"
    )
    province: Optional[str] = Field(
        None, alias="prov", description="Provincia donde se ubica la estación"
    )
    district: Optional[str] = Field(
        None, alias="dist", description="Distrito donde se ubica la estación"
    )
    station_type: StationType = Field(..., alias="ico", description="Tipo de estación")
    code: str = Field(
        ..., alias="cod", min_length=1, description="Código único de la estación"
    )
    legacy_code: Optional[str] = Field(
        "", alias="cod_old", description="Código anterior de la estación"
    )
    frontend_code: Optional[str] = Field(
        None,
        alias="cod_ui",
        description="Nuevo código de frontend para compatibilidad con versiones anteriores",
    )
    status: StationStatus = Field(..., alias="estado", description="Estado operativo")
    data_available_since: Optional[str] = Field(
        None,
        alias="data_since",
        description="Fecha desde la cual hay datos disponibles",
    )

    class Config:
        validate_by_name = True
        use_enum_values = True

    @field_validator("code")
    def validate_code(cls, v):
        """Valida que el código de estación no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El código de estación no puede estar vacío")
        return v.strip().upper()

    @field_validator("name")
    def validate_name(cls, v):
        """Valida que el nombre no esté vacío"""
        if not v or not v.strip():
            raise ValueError("El nombre de la estación no puede estar vacío")
        return v.strip().title()

    def is_meteorological(self) -> bool:
        """Retorna True si es una estación meteorológica"""
        return self.station_type == StationType.METEOROLOGICAL

    def is_hydrological(self) -> bool:
        """Retorna True si es una estación hidrológica"""
        return self.station_type == StationType.HYDROLOGICAL

    def is_automatic(self) -> bool:
        """Retorna True si la estación es automática"""
        return self.status == StationStatus.AUTOMATIC

    def get_coordinates(self) -> tuple[float, float]:
        """Retorna las coordenadas como tupla (latitud, longitud)"""
        return (self.latitude, self.longitude)

    def get_csv_headers(self) -> List[str]:
        """Retorna los headers CSV apropiados según el tipo y estado de la estación"""
        from .data_schema import get_headers_for_station_type

        return get_headers_for_station_type(self.station_type, self.status)

    def __str__(self) -> str:
        return f"{self.name} ({self.code}) - {self.category}"


class StationSummary(BaseModel):
    """Resumen de información clave de una estación para mostrar al usuario."""

    name: str = Field(..., description="Nombre de la estación")
    code: str = Field(..., description="Código único de la estación")
    category: StationCategory = Field(..., description="Categoría de la estación")
    type: StationType = Field(..., description="Tipo de estación")
    status: StationStatus = Field(..., description="Estado operativo")


class StationDataAvailability(BaseModel):
    """Modelo para representar la disponibilidad de datos de una estación."""

    name: str = Field(..., description="Nombre de la estación")
    code: str = Field(..., description="Código único de la estación")
    data_available_since: Optional[str] = Field(
        None, description="Fecha desde la cual hay datos disponibles"
    )
    years_available: Optional[int] = Field(
        None, description="Cantidad de años de datos disponibles"
    )


class StationDataAvailabilityResponse(BaseModel):
    """Modelo para representar la respuesta de disponibilidad de datos, que puede incluir una estación puntual o un conjunto filtrado."""

    station: Annotated[
        Optional[StationDataAvailability],
        Field(description="Disponibilidad de datos para una estación específica"),
    ] = None
    stations: Annotated[
        Optional[List[StationDataAvailability]],
        Field(description="Lista de disponibilidad de datos para estaciones filtradas"),
    ] = None
