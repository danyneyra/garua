from mcp.types import TextContent

from garua.models.comparison import ComparePeriodsResponse


def build_comparison_success_response(
    message: str,
    structured_data: ComparePeriodsResponse,
) -> dict:
    """
    Construye una respuesta estructurada para la comparación de periodos, incluyendo contenido legible y datos estructurados.
    """
    content = [
        TextContent(
            text=message,
            type="text",
        )
    ]

    return {
        "content": content,
        "structuredContent": structured_data.model_dump(),
        "isError": False,
    }


def build_comparison_error_response(error_message: str) -> dict:
    """
    Construye una respuesta de error para la comparación de periodos, incluyendo un mensaje legible.
    """
    content = [
        TextContent(
            text=error_message,
            type="text",
        )
    ]

    return {
        "content": content,
        "structuredContent": {"error": error_message},
        "isError": True,
    }
