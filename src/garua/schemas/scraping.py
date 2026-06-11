from typing import Optional
from mcp.types import TextContent

from garua.models.scraping import (
    FileInfo,
    ScrapingErrorResponse,
    ScrapingSuccessResponse,
    Stats,
)
from garua.schemas.mcp import build_files_info


def _append_open_file_options(message: str, files_info: list[FileInfo]) -> str:
    """Agrega opciones legibles para abrir archivos aunque el cliente no renderice ResourceLink."""

    if not files_info:
        return message

    lines = ["", "Archivos disponibles para abrir:"]
    for file_info in files_info:
        lines.append(f"Archivo disponible: {file_info.name} \n")
        lines.append(f"Ruta: {file_info.uri} \n")
        lines.append("\n")

    lines.append(
        "\nLos archivos están disponibles como recursos adjuntos a esta respuesta. Puedes abrirlo desde el recurso adjunto o desde la ruta indicada."
    )
    return message.rstrip() + "\n" + "\n".join(lines)


def build_scraping_error_response(
    message: str,
    error_code: str,
    station_code: Optional[str] = None,
    station_name: Optional[str] = None,
    details: Optional[str] = None,
) -> dict:
    """
    Construye una respuesta de error para operaciones de scraping, incluyendo contenido legible y datos estructurados.
    """

    return {
        "content": [
            TextContent(
                text=message,
                type="text",
            )
        ],
        "structuredContent": ScrapingErrorResponse(
            message=message,
            station_code=station_code,
            station_name=station_name,
            error_code=error_code,
            details=details,
        ),
        "isError": True,
    }


def build_scraping_success_response(
    message: str,
    station_name: str,
    station_code: str,
    mode: str,
    period: str,
    stats: dict,
    files: Optional[list[str]] = None,
    extracted_from: Optional[str] = None,
) -> dict:
    """
    Construye una respuesta de éxito para operaciones de scraping, incluyendo contenido legible y datos estructurados.
    """
    content: list = []

    if files is not None and len(files) > 0:
        files_info, resource_links = build_files_info(files, kind="downloaded_file")
        message = _append_open_file_options(message, files_info)

    else:
        files_info = []
        resource_links = []

    content.append(
        TextContent(
            text=message,
            type="text",
        )
    )

    if resource_links:
        content.extend(resource_links)

    return {
        "content": content,
        "structuredContent": ScrapingSuccessResponse(
            message=message,
            station_name=station_name,
            station_code=station_code,
            mode=mode,
            period=period,
            stats=Stats(**stats),
            files=files_info,
            extracted_from=extracted_from,
        ).model_dump(),
        "isError": False,
    }
