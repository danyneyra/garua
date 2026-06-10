"""
Modelos para consultas y operaciones de scraping.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

YEAR_NOW = datetime.now().year


class QueryMode(str, Enum):
    """Modos de consulta disponibles"""

    MONTH = "month"  # Consulta por mes específico
    YEAR = "year"  # Consulta por año completo
    PERIOD = "period"  # Consulta por periodo de años


class OutputFormat(str, Enum):
    """Formatos de salida disponibles"""

    CSV = "csv"
    JSON = "json"
    EXCEL = "xlsx"


class DateRange(BaseModel):
    """Rango de fechas para consultas"""

    start_year: int = Field(..., ge=2000, le=YEAR_NOW, description="Año inicial")
    end_year: Optional[int] = Field(
        None, ge=2000, le=YEAR_NOW, description="Año final (para periodo)"
    )
    month: Optional[int] = Field(
        None, ge=1, le=12, description="Mes específico (para consulta mensual)"
    )

    @field_validator("end_year")
    def validate_end_year(cls, v, values):
        """Valida que el año final sea mayor o igual al inicial"""
        if v is not None and "start_year" in values and v < values["start_year"]:
            raise ValueError("El año final debe ser mayor o igual al inicial")
        return v

    @field_validator("month")
    def validate_month_with_mode(cls, v, values):
        """Valida que el mes solo se use en consultas mensuales"""
        # Esta validación se hará en el modelo de consulta principal
        return v


class QueryRequest(BaseModel):
    """Solicitud de consulta completa"""

    station_code: str = Field(..., min_length=1, description="Código de la estación")
    mode: QueryMode = Field(..., description="Modo de consulta")
    date_range: DateRange = Field(..., description="Rango de fechas")
    consolidated_output: bool = Field(
        False, description="¿Generar archivo consolidado?"
    )
    output_format: OutputFormat = Field(
        OutputFormat.CSV, description="Formato de salida"
    )
    output_filename: Optional[str] = Field(
        None, description="Nombre personalizado del archivo"
    )

    @field_validator("date_range")
    def validate_date_range_with_mode(cls, v, values):
        """Valida que el rango de fechas sea compatible con el modo"""
        if "mode" not in values:
            return v

        mode = values["mode"]

        # Validación para modo MONTH
        if mode == QueryMode.MONTH:
            cls._validate_month_mode(v)

        # Validación para modo YEAR
        elif mode == QueryMode.YEAR:
            cls._validate_year_mode(v)

        # Validación para modo PERIOD
        elif mode == QueryMode.PERIOD:
            cls._validate_period_mode(v)

        return v

    @classmethod
    def _validate_month_mode(cls, date_range):
        """Valida rango de fechas para modo mensual"""
        if date_range.month is None:
            raise ValueError("El mes es requerido para consultas mensuales")
        if date_range.end_year is not None:
            raise ValueError(
                "No se debe especificar año final para consultas mensuales"
            )

    @classmethod
    def _validate_year_mode(cls, date_range):
        """Valida rango de fechas para modo anual"""
        if date_range.month is not None:
            raise ValueError("No se debe especificar mes para consultas anuales")
        if date_range.end_year is not None:
            raise ValueError("No se debe especificar año final para consultas anuales")

    @classmethod
    def _validate_period_mode(cls, date_range):
        """Valida rango de fechas para modo periodo"""
        if date_range.month is not None:
            raise ValueError("No se debe especificar mes para consultas de periodo")
        if date_range.end_year is None:
            raise ValueError("El año final es requerido para consultas de periodo")

    def get_filename_prefix(self) -> str:
        """Genera el prefijo del archivo basado en el código de estación"""
        return self.station_code.upper()

    def get_suggested_filename(self) -> str:
        """Genera un nombre sugerido para el archivo de salida"""
        if self.output_filename:
            return self.output_filename

        prefix = self.get_filename_prefix()

        if self.mode == QueryMode.MONTH:
            return f"{prefix}-{self.date_range.start_year:04d}{self.date_range.month:02d}.{self.output_format.value}"
        elif self.mode == QueryMode.YEAR:
            return f"{prefix}-{self.date_range.start_year}.{self.output_format.value}"
        elif self.mode == QueryMode.PERIOD:
            return f"{prefix}-{self.date_range.start_year}-{self.date_range.end_year}.{self.output_format.value}"

        return f"{prefix}-data.{self.output_format.value}"


class ScrapingResult(BaseModel):
    """Resultado de una operación de scraping"""

    station_code: str = Field(..., description="Código de la estación procesada")
    success: bool = Field(..., description="¿La operación fue exitosa?")
    records_count: int = Field(0, description="Número de registros procesados")
    files_generated: List[str] = Field(
        default_factory=list, description="Archivos generados"
    )
    errors: List[str] = Field(default_factory=list, description="Errores encontrados")
    processing_time: Optional[float] = Field(
        None, description="Tiempo de procesamiento en segundos"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Timestamp de la operación"
    )

    def add_error(self, error: str) -> None:
        """Añade un error a la lista"""
        self.errors.append(error)
        self.success = False

    def add_file(self, filepath: str) -> None:
        """Añade un archivo generado a la lista"""
        self.files_generated.append(filepath)

    def get_summary(self) -> str:
        """Retorna un resumen legible del resultado"""
        status = "✅ Exitoso" if self.success else "❌ Falló"
        return f"{status} - {self.records_count} registros, {len(self.files_generated)} archivos"
