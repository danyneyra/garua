from pydantic import BaseModel, Field
from typing import Optional, Annotated

from garua.models.responses import ErrorResponse, SuccessResponse, FileInfo


class Stats(BaseModel):
    successful: int = Field(..., description="Número de descargas exitosas")
    failed: int = Field(..., description="Número de descargas fallidas")
    total: int = Field(..., description="Número total de intentos de descarga")


class ScrapingPeriod(BaseModel):
    year: int = Field(..., description="Año de periodo de scraping")
    month: int = Field(..., description="Mes de periodo de scraping")


class ScrapingQueryBaseParams(BaseModel):
    mode: Annotated[
        str,
        Field(
            None,
            description=(
                "Modo de descarga: "
                "'month' = un mes específico (requiere year + month), "
                "'year' = un año completo (requiere year), "
                "'period' = rango de años (requiere start_year + end_year). "
                "Opcional si se usa el parámetro 'periods'."
            ),
        ),
    ]
    year: Annotated[
        Optional[int],
        Field(
            None,
            description="Año (ej: 2025). Requerido para mode='month' o mode='year'.",
        ),
    ] = None
    month: Annotated[
        Optional[int],
        Field(None, description="Mes como número (1-12). Requerido para mode='month'."),
    ] = None
    start_year: Annotated[
        Optional[int],
        Field(
            None, description="Año de inicio del rango. Requerido para mode='period'."
        ),
    ] = None
    end_year: Annotated[
        Optional[int],
        Field(None, description="Año de fin del rango. Requerido para mode='period'."),
    ] = None


class ScrapingQueryParams(ScrapingQueryBaseParams):
    mode: Annotated[
        Optional[str],
        Field(
            None,
            description=(
                "Modo de descarga: "
                "'month' = un mes específico (requiere year + month), "
                "'year' = un año completo (requiere year), "
                "'period' = rango de años (requiere start_year + end_year). "
                "Opcional si se usa el parámetro 'periods'."
            ),
        ),
    ] = None
    individual: Annotated[
        bool,
        Field(
            False,
            description=(
                "Si es True, descarga cada periodo en archivos separados. "
                "Solo aplicable para mode='year' o mode='period'."
            ),
        ),
    ] = False
    output_dir: Annotated[
        Optional[str],
        Field(
            None, description="Directorio de salida para los archivos CSV generados."
        ),
    ] = None
    mcp_filter_periods: Annotated[
        Optional[list[ScrapingPeriod]],
        Field(None, description="Lista de periodos para filtrar en MCP"),
    ] = None

    # Validar que los parámetros requeridos estén presentes según el modo
    def validate(self):
        if self.mode == "month":
            if self.year is None or self.month is None:
                raise ValueError("Para mode='month', se requieren year y month.")
        elif self.mode == "year":
            if self.year is None:
                raise ValueError("Para mode='year', se requiere year.")
        elif self.mode == "period":
            if self.start_year is None or self.end_year is None:
                raise ValueError(
                    "Para mode='period', se requieren start_year y end_year."
                )
        else:
            raise ValueError("mode debe ser 'month', 'year' o 'period'.")


class ScrapingSuccessResponse(SuccessResponse):
    """Modelo específico para respuestas exitosas de scraping"""

    stats: Stats = Field(..., description="Estadísticas de la operación de scraping")
    files: Optional[list[FileInfo]] = Field(
        None, description="Lista de archivos generados por el scraping"
    )
    extracted_from: Optional[str] = Field(
        None,
        description="Fuente de donde se extrajeron los datos (e.g., 'cache', 'web')",
    )


class ScrapingErrorResponse(ErrorResponse):
    """Modelo específico para errores de scraping"""

    pass


class ScrapingServiceSuccessResponse(SuccessResponse):
    """Resultado exitoso del servicio de scraping, sin dependencias MCP."""

    stats: Stats = Field(..., description="Estadísticas de la operación de scraping")
    files: list[str] = Field(
        default_factory=list,
        description="Rutas de archivos generados por el scraping",
    )
    extracted_from: Optional[str] = Field(
        None,
        description="Fuente de donde se extrajeron los datos (e.g., 'cache', 'web')",
    )


class ScrapingServiceErrorResponse(ErrorResponse):
    """Resultado fallido del servicio de scraping, sin dependencias MCP."""

    pass
