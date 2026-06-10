from typing import Optional
from mcp.types import TextContent

from garua.models.file_tools import CsvPreviewResponse, ExtractFilesResponse
from garua.schemas.mcp import build_files_info


def build_extracted_data_success_response(
    message: str,
    station_name: str,
    station_code: str,
    mode: str,
    period: str,
    rows_extracted: int,
    source_files: Optional[list[str]] = None,
    output_files: Optional[list[str]] = None,
    overwrite: bool = True,
) -> dict:
    """Construye una respuesta exitosa para datos extraídos."""
    content: list = [
        TextContent(
            text=message,
            type="text",
        )
    ]

    # Construir información de archivos fuente y enlaces de recursos
    source_files_info = []
    if source_files is not None and len(source_files) > 0:
        source_files_info, resource_links = build_files_info(
            source_files, kind="source_file"
        )

        if resource_links:
            content.extend(resource_links)

    # Construir información de archivos de salida y enlaces de recursos
    output_files_info = []
    if output_files is not None and len(output_files) > 0:
        output_files_info, resource_links = build_files_info(
            output_files, kind="output_file"
        )

        if resource_links:
            content.extend(resource_links)

    return {
        "content": content,
        "structuredContent": ExtractFilesResponse(
            message=message,
            station_name=station_name,
            station_code=station_code,
            mode=mode,
            period=period,
            rows_extracted=rows_extracted,
            source_files=source_files_info or [],
            output_files=output_files_info or [],
            overwrite=overwrite,
        ),
        "isError": False,
    }


def build_csv_preview_success_response(
    message: str,
    columns: list[str],
    rows: list[dict],
    total_rows: int,
    total_columns: int,
    truncated: bool,
    truncated_reason: str | None,
    source_file: str,
) -> dict:
    """Construye una respuesta MCP para vistas previas de CSV."""
    content: list = [
        TextContent(
            text=message,
            type="text",
        )
    ]

    _, resource_links = build_files_info([source_file], kind="csv_preview")
    if resource_links:
        content.extend(resource_links)

    return {
        "content": content,
        "structuredContent": CsvPreviewResponse(
            message=message,
            columns=columns,
            rows=rows,
            total_rows=total_rows,
            total_columns=total_columns,
            preview_rows=len(rows),
            preview_columns=len(columns),
            truncated=truncated,
            truncated_reason=truncated_reason,
        ).model_dump(),
        "isError": False,
    }
