from pydantic import AnyUrl, BaseModel, Field, AfterValidator
from typing import Optional, Literal, Annotated


def to_upper(v: str) -> str:
    return v.upper()


UpperStr = Annotated[str, AfterValidator(to_upper)]


class FileInfo(BaseModel):
    name: str = Field(..., description="Nombre del archivo generado")
    path: str = Field(
        ...,
        description=("Ruta absoluta del archivo en el filesystem local."),
    )
    uri: AnyUrl = Field(
        ...,
        description=(
            "URI del archivo generado. Si el archivo pertenece a la carpeta CSV "
            "configurada, se usa el esquema file://csv/..."
        ),
    )
    mime_type: Annotated[
        Optional[str],
        Field(None, description="Tipo MIME del archivo, e.g., 'text/csv'"),
    ] = None
    description: Annotated[
        Optional[str], Field(None, description="Descripción adicional del archivo")
    ] = None
    open_label: Annotated[
        Optional[str],
        Field(
            None,
            description="Texto sugerido para mostrar una acción de apertura del archivo.",
        ),
    ] = None
    clickable_hint: Annotated[
        bool,
        Field(
            None,
            alias="clickableHint",
            description="Indica si el enlace es clickeable (e.g., True para 'Haz clic para descargar')",
        ),
    ] = True


class ResponseBase(BaseModel):
    """Modelo base para respuestas de scraping"""

    success: bool = Field(..., description="Indica si la operación fue exitosa o no")
    message: str = Field(..., description="Mensaje sobre el resultado")
    station_name: Optional[str] = Field(
        None, description="Nombre de la estación relacionada"
    )
    station_code: Optional[str] = Field(
        None, description="Código de la estación relacionada"
    )


class SuccessResponse(ResponseBase):
    """Modelo específico para respuestas exitosas"""

    success: Annotated[
        Literal[True],
        Field(default=True, description="Indica que la operación fue exitosa"),
    ] = True
    station_name: str = Field(..., description="Nombre de la estación relacionada")
    station_code: str = Field(..., description="Código de la estación relacionada")
    mode: str = Field(..., description="Modo de descarga utilizado")
    period: str = Field(
        ..., description="Periodo de datos descargados (e.g., '2020', '2020-2021')"
    )


class ErrorResponse(ResponseBase):
    """Modelo específico para errores de scraping"""

    success: Annotated[
        Literal[False],
        Field(default=False, description="Indica que la operación falló"),
    ] = False
    error_code: UpperStr = Field(
        ..., description="Código de error específico en mayúsculas"
    )
    details: Optional[str] = Field(
        None, description="Detalles adicionales sobre el error"
    )
