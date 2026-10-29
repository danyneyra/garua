from fastmcp.tools import ToolResult
from garua.schemas.result import build_tool_result
from mcp.types import TextContent

from garua.models.comparison import ComparePeriodsResponse


def build_comparison_success_response(
    message: str,
    structured_data: ComparePeriodsResponse,
) -> ToolResult:
    """
    Construye una respuesta estructurada para la comparación de periodos, incluyendo contenido legible y datos estructurados.
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


def build_comparison_error_response(error_message: str) -> ToolResult:
    """
    Construye una respuesta de error para la comparación de periodos, incluyendo un mensaje legible.
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
