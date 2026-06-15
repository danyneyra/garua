from mcp.types import TextContent
from garua.models.anomaly import DetectAnomaliesResponse


def build_anomaly_error_response(error_message: str) -> dict:
    """
    Construye una respuesta de error para operaciones de detección de anomalías, incluyendo un mensaje legible.
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


def build_anomaly_sucess_response(
    message: str, structured_data: DetectAnomaliesResponse
) -> dict:
    """
    Construye una respuesta de éxito para operaciones de detección de anomalías, incluyendo contenido legible y datos estructurados.
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
