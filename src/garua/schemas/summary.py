from mcp.types import TextContent

from garua.models.summary import SummaryResponse


def build_summary_success_response(
    message: str,
    structured_data: SummaryResponse,
) -> dict:
    """Construye una respuesta de resumen exitosa."""
    content = TextContent(
        text=message,
        type="text",
    )
    return {
        "content": content,
        "structuredContent": structured_data.model_dump(),
        "isError": False,
    }


def build_summary_error_response(error_message: str) -> dict:
    """Construye una respuesta de resumen con error."""
    content = TextContent(
        text=error_message,
        type="text",
    )
    return {
        "content": content,
        "structuredContent": {"error": error_message},
        "isError": True,
    }
