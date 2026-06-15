"""Tools MCP para recomendación de estaciones."""

from typing import Annotated, Literal

from pydantic import Field

from garua.services.recommendation import recommend_station_for_point
from garua.utils.helpers import haversine as haversine_fn
from garua.schemas.mcp import build_mcp_success_response


def register_recommendation_tools(mcp, stations):
    """Registra las tools de recomendación en el servidor MCP."""

    @mcp.tool()
    def recommend_station_for_point_tool(
        lat: Annotated[
            float,
            Field(
                description="Latitud del punto de interés en grados decimales. Negativo para el hemisferio Sur."
            ),
        ],
        lon: Annotated[
            float,
            Field(
                description="Longitud del punto de interés en grados decimales. Negativo para el oeste."
            ),
        ],
        radius_km: Annotated[
            float,
            Field(
                description="Radio máximo de búsqueda en kilómetros. Por defecto 100 km."
            ),
        ] = 100.0,
        station_type: Annotated[
            Literal["M", "H", "all"],
            Field(
                description="Tipo de estación: 'M' (meteorológica), 'H' (hidrológica), 'all' (ambas). Por defecto 'M'."
            ),
        ] = "M",
        target_altitude: Annotated[
            float | None,
            Field(
                description=(
                    "Altitud del proyecto o punto de interés en metros sobre el nivel del mar (msnm). "
                    "Si se proporciona, las estaciones con altitud similar tendrán mejor score."
                )
            ),
        ] = None,
        prefer_status: Annotated[
            list[str] | None,
            Field(
                description=(
                    "Lista de estados operativos en orden de prioridad. "
                    "Ejemplo: ['REAL', 'AUTOMATICA', 'DIFERIDO']. "
                    "Si no se especifica, usa prioridades por defecto."
                )
            ),
        ] = None,
        min_years_available: Annotated[
            int | None,
            Field(
                description=(
                    "Mínimo de años de datos históricos requeridos. "
                    "Excluye estaciones con menos años de historial. "
                    "Ejemplo: 5 para proyectos que requieren series largas."
                )
            ),
        ] = None,
        limit: Annotated[
            int,
            Field(
                description="Cantidad máxima de recomendaciones a devolver. Por defecto 5, máximo 20."
            ),
        ] = 5,
    ) -> dict:
        """
        Recomienda las mejores estaciones SENAMHI para un punto geográfico dado.

        Esta tool evalúa estaciones considerando múltiples criterios:
        - **Distancia**: Cercanía al punto de interés
        - **Historial**: Años de datos disponibles
        - **Estado**: Operativo, automático o diferido
        - **Altitud**: Similitud con la altitud objetivo (opcional)

        El score final (0-100) es explicable y defensible, ideal para:
        - Proyectos mineros, ambientales, agrícolas o hidrológicos
        - Estudios que requieren justificar la selección de estaciones
        - Análisis que necesitan series históricas específicas

        Devuelve:
        - `recommended`: Estación con mejor score
        - `alternatives`: Otras estaciones ordenadas por score
        - `score_breakdown`: Desglose detallado del score
        - `reason`: Explicación en español de por qué se recomienda

        USA ESTA TOOL cuando el usuario:
        - Necesite encontrar la mejor estación para un proyecto o ubicación
        - Pida recomendaciones defendibles o justificables
        - Requiera considerar múltiples criterios (no solo distancia)
        - Mencione un proyecto minero, ambiental, agrícola, etc.

        NUNCA calcules scores manualmente — esta tool ya implementa todo.
        """
        result = recommend_station_for_point(
            stations=stations,
            haversine_fn=haversine_fn,
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            station_type=station_type,
            target_altitude=target_altitude,
            prefer_status=prefer_status,
            min_years_available=min_years_available,
            limit=limit,
        )

        message = f"Recomendación de estaciones para punto ({lat}, {lon}) con radio {radius_km} km y tipo '{station_type}'"
        if target_altitude is not None:
            message += f", altitud objetivo {target_altitude} m"
        message += f". {result.message}"

        return build_mcp_success_response(
            message=message, structured_data=result.model_dump()
        )
