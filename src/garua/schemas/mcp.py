from mcp.types import TextContent, ResourceLink
from pathlib import Path
from pydantic import AnyUrl

from garua.models.responses import ErrorResponse
from garua.models.scraping import (
    FileInfo,
)

_KIND_MESSAGE_MAP = {
    "downloaded_file": "Archivo generado por el proceso de scraping",
    "source_file": "Archivo fuente utilizado para la extracción",
    "output_file": "Archivo de salida generado por la extracción",
    "csv_preview": "Archivo CSV usado para la vista previa",
}

_MIME_TYPE_BY_SUFFIX = {
    ".csv": "text/csv",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def build_files_info(
    list_dir: list[str], kind: str
) -> tuple[list[FileInfo], list[ResourceLink]]:
    """
    Construye un objeto FileInfo a partir de los parámetros proporcionados.
    """
    if not list_dir or len(list_dir) == 0:
        return [], []

    files_info = []
    resource_links = []

    for file_path in list_dir:
        path_obj = Path(file_path)
        file_name = path_obj.name
        resolved_path = path_obj.resolve()

        absolute_path = str(resolved_path)
        uri_target = resolved_path.as_uri()

        file_uri = AnyUrl(uri_target)
        mime_type = _MIME_TYPE_BY_SUFFIX.get(path_obj.suffix.lower(), "text/plain")
        description = _KIND_MESSAGE_MAP.get(kind, "Archivo CSV generado")

        files_info.append(
            FileInfo(
                name=file_name,
                path=absolute_path,
                uri=file_uri,
                mime_type=mime_type,
                description=description,
            )
        )
        resource_links.append(
            ResourceLink(
                type="resource_link",
                name=file_name,
                title=file_name,
                uri=file_uri,
                description=description,
                mimeType=mime_type,
            )
        )

    return files_info, resource_links


def build_mcp_success_response(
    message: str,
    structured_data: dict,
) -> dict:
    """Construye una respuesta MCP exitosa."""
    content = TextContent(
        text=message,
        type="text",
    )
    return {
        "content": content,
        "structuredContent": structured_data,
        "isError": False,
    }


def build_mcp_error_response(
    error_message: str,
    error_code: str | None = None,
    station_name: str | None = None,
    station_code: str | None = None,
    error_details: str | None = None,
) -> dict:
    """Construye una respuesta MCP con error."""
    content = TextContent(
        text=error_message,
        type="text",
    )
    return {
        "content": content,
        "structuredContent": ErrorResponse(
            message=error_message,
            station_name=station_name,
            station_code=station_code,
            error_code=error_code or "UNKNOWN_ERROR",
            details=error_details if error_details else None,
        ).model_dump(),
        "isError": True,
    }
