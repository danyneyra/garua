from typing import Annotated, Any, Literal, Optional

from pydantic import BaseModel, Field

from garua.models.responses import SuccessResponse, FileInfo


class ExtractFilesResponse(SuccessResponse):
    """Modelo específico para respuestas exitosas de extracción de archivos"""

    source_files: list[FileInfo] = Field(
        ...,
        description="Lista de archivos fuente utilizados para la extracción",
    )
    output_files: list[FileInfo] = Field(..., description="Lista de archivos extraídos")
    rows_extracted: int = Field(
        ..., description="Número total de filas extraídas de los archivos fuente"
    )
    overwrite: bool = Field(
        ...,
        description="Indica si los archivos de salida sobrescriben archivos existentes con el mismo nombre",
    )
    display_hint: Annotated[
        Optional[str],
        Field(
            None,
            description=(
                "Sugerencia de visualización para el cliente. "
                "Puede ser 'table', 'chart', 'file_list', etc., dependiendo de cómo se quieran mostrar los datos."
            ),
        ),
    ] = "Mostrar los archivos extraídos al usuario, con opciones para abrirlos o descargarlos."


class CsvPreviewResponse(BaseModel):
    """Respuesta estructurada para vistas previas de archivos CSV."""

    success: Literal[True] = True
    type: Literal["csv_preview"] = "csv_preview"
    message: str = Field(..., description="Mensaje legible de la vista previa")
    columns: list[str] = Field(..., description="Columnas incluidas en la vista previa")
    rows: list[dict[str, Any]] = Field(
        ..., description="Filas incluidas en la vista previa"
    )
    total_rows: int = Field(
        ..., description="Número total de filas disponibles para el periodo solicitado"
    )
    total_columns: int = Field(..., description="Número total de columnas del CSV")
    preview_rows: int = Field(..., description="Número de filas devueltas")
    preview_columns: int = Field(..., description="Número de columnas devueltas")
    truncated: bool = Field(
        ..., description="Indica si se limitaron filas o columnas en la respuesta"
    )
    truncated_reason: str | None = Field(
        None, description="Motivo por el cual se truncó la vista previa"
    )
