from fastmcp.tools import ToolResult
from garua.schemas.result import build_tool_result
from mcp.types import TextContent
from garua.models.anomaly import DetectAnomaliesResponse


def build_anomaly_error_response(error_message: str) -> ToolResult:
    """
    Construye una respuesta de error para operaciones de detección de anomalías, incluyendo un mensaje legible.
    """
    content = [
        TextContent(
            text=error_message,
            type="text",
        )
    ]

    return build_tool_result(
        content=content, structured_content={"error": error_message}, is_error=True
    )


def build_anomaly_sucess_response(
    message: str, structured_data: DetectAnomaliesResponse
) -> ToolResult:
    """
    Construye una respuesta de éxito para operaciones de detección de anomalías, incluyendo contenido legible y datos estructurados.
    """
    content = [
        TextContent(
            text=message,
            type="text",
        )
    ]

    return build_tool_result(
        content=content, structured_content=structured_data.model_dump(), is_error=False
    )
