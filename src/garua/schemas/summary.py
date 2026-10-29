from fastmcp.tools import ToolResult
from garua.schemas.result import build_tool_result
from mcp.types import TextContent

from garua.models.summary import SummaryResponse


def build_summary_success_response(
    message: str,
    structured_data: SummaryResponse,
) -> ToolResult:
    """Construye una respuesta de resumen exitosa."""
    content = TextContent(
        text=message,
        type="text",
    )
    return build_tool_result(
        content=content, structured_content=structured_data.model_dump(), is_error=False
    )


def build_summary_error_response(error_message: str) -> ToolResult:
    """Construye una respuesta de resumen con error."""
    content = TextContent(
        text=error_message,
        type="text",
    )
    return build_tool_result(
        content=content, structured_content={"error": error_message}, is_error=True
    )
