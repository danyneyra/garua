"""Tools para búsqueda y filtrado de estaciones SENAMHI."""

import csv
from datetime import datetime
from typing import Annotated

from mcp.types import TextContent
from pydantic import Field

from garua.schemas.station import station_response_serializer as _serialize
from garua.services.station import (
    check_data_availability as check_data_availability_service,
    find_station_by_code,
    search_stations_by_name,
    stations,
)
from garua.utils.helpers import haversine
from garua.schemas.mcp import (
    build_files_info,
    build_mcp_error_response,
    build_mcp_success_response,
)


_STATIONS_CSV_HEADERS = {
    "name": "Nombre",
    "code": "Código",
    "type": "Tipo",
    "category": "Categoría",
    "status": "Estado",
    "latitude": "Latitud",
    "longitude": "Longitud",
    "department": "Departamento",
    "province": "Provincia",
    "district": "Distrito",
    "altitude": "Altitud",
    "data_available_since": "Datos disponibles desde",
}


def register_station_tools(mcp):
    """Registra las tools de estaciones en el servidor MCP."""

    @mcp.tool()
    def search_stations(
        query: Annotated[
            str,
            Field(
                description=(
                    "Código exacto de la estación (ej: '100090') o nombre parcial "
                    "(ej: 'Cabana', 'Juli'). La búsqueda por nombre es case-insensitive "
                    "y admite coincidencias parciales."
                )
            ),
        ],
    ) -> dict:
        """
        Busca estaciones SENAMHI por código o por nombre.

        Úsala cuando el usuario mencione una estación específica pero no esté claro
        si proporcionó el código interno, código anterior, código visible en frontend
        o solo una parte del nombre. La búsqueda por código intenta coincidencia exacta;
        la búsqueda por nombre acepta coincidencias parciales sin distinguir mayúsculas.

        Devuelve una lista de estaciones candidatas con datos básicos para selección:
        nombre, código, tipo, categoría, estado operativo, coordenadas, ubicación
        administrativa, altitud y fecha inicial de disponibilidad de datos.

        Si devuelve varias estaciones, pide o infiere la estación correcta antes de
        descargar, resumir, comparar o validar datos. Si devuelve lista vacía, no
        inventes códigos ni estaciones.
        """
        exact = find_station_by_code(query)
        matches = [exact] if exact else search_stations_by_name(query)
        return build_mcp_success_response(
            f"{len(matches)} estación(es) encontrada(s) para '{query}'",
            {"stations": [_serialize(s) for s in matches]},
        )

    @mcp.tool()
    def get_station_info(
        code: Annotated[
            str,
            Field(
                description=(
                    "Código interno de la estación (ej: '100090', '153209'). "
                    "Obtenlo primero con search_stations si no lo tienes."
                )
            ),
        ],
    ) -> dict:
        """
        Obtiene la ficha completa de una estación SENAMHI por código.

        Úsala cuando ya tengas un código de estación y necesites confirmar sus
        metadatos antes de una operación posterior. Acepta el código interno,
        código anterior o código visible de frontend cuando existan equivalencias.

        Devuelve una sola estación con nombre, código, tipo, categoría, estado,
        coordenadas, departamento, provincia, distrito, altitud y disponibilidad
        histórica. Si el código no existe, devuelve una respuesta de error.

        Para búsquedas por nombre o cuando el código sea dudoso, usa primero
        search_stations.
        """
        station = find_station_by_code(code)
        if not station:
            return build_mcp_error_response(
                f"Estación con código '{code}' no encontrada"
            )
        return build_mcp_success_response(
            f"Estación encontrada para código '{code}'",
            {"station": _serialize(station)},
        )

    @mcp.tool()
    def get_all_stations(
        limit: Annotated[
            int,
            Field(
                ge=1,
                le=500,
                description=(
                    "Cantidad máxima de estaciones a devolver en esta página. "
                    "Usa export_all_stations_csv si necesitas el catálogo completo."
                ),
            ),
        ] = 100,
        offset: Annotated[
            int,
            Field(
                ge=0,
                description="Cantidad de estaciones a omitir antes de devolver resultados.",
            ),
        ] = 0,
    ) -> dict:
        """
        Devuelve una página del catálogo de estaciones SENAMHI disponibles.

        Úsala cuando el usuario quiera explorar o listar estaciones en el chat.
        La respuesta está paginada para evitar respuestas demasiado grandes en el
        cliente MCP. Para exportar o descargar el catálogo completo, usa
        export_all_stations_csv.

        La respuesta incluye cada estación con metadatos de identificación,
        ubicación, coordenadas, altitud, tipo, categoría, estado operativo y fecha
        inicial de datos disponibles, además de total, limit, offset y has_more.
        """
        total = len(stations)
        paginated_stations = stations[offset : offset + limit]
        has_more = offset + limit < total

        return build_mcp_success_response(
            f"{len(paginated_stations)} estación(es) devuelta(s) de {total}",
            {
                "stations": [_serialize(s) for s in paginated_stations],
                "total": total,
                "limit": limit,
                "offset": offset,
                "next_offset": offset + limit if has_more else None,
                "has_more": has_more,
            },
        )

    @mcp.tool()
    def export_all_stations_csv(
        overwrite: Annotated[
            bool,
            Field(
                description=(
                    "Si es True, regenera el CSV aunque ya exista. "
                    "Si es False, reutiliza el archivo existente cuando esté disponible."
                )
            ),
        ] = True,
    ) -> dict:
        """
        Exporta el catálogo completo de estaciones SENAMHI a un archivo CSV.

        Úsala cuando el usuario pida descargar, exportar, guardar o compartir el
        catálogo completo de estaciones. A diferencia de get_all_stations, esta
        tool no devuelve todas las filas dentro de structuredContent; genera un
        CSV en exports/estaciones_senamhi.csv y devuelve un enlace de recurso.

        El CSV incluye nombre, código, tipo, categoría, estado, coordenadas,
        ubicación administrativa, altitud y fecha inicial de disponibilidad de
        datos.
        """
        from garua.settings import EXPORTS_DIR

        output_path = EXPORTS_DIR / "estaciones_senamhi.csv"
        generated = False

        if overwrite or not output_path.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            rows = [
                {
                    csv_header: station_data.get(response_key)
                    for response_key, csv_header in _STATIONS_CSV_HEADERS.items()
                }
                for station_data in (_serialize(s) for s in stations)
            ]
            with output_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(
                    f, fieldnames=list(_STATIONS_CSV_HEADERS.values())
                )
                writer.writeheader()
                writer.writerows(rows)
            generated = True

        files_info, resource_links = build_files_info(
            [str(output_path)], kind="output_file"
        )
        file_info = files_info[0].model_dump(mode="json") if files_info else None
        message_action = "generado" if generated else "reutilizado"
        message = (
            f"CSV de estaciones {message_action}: {output_path} ({len(stations)} filas)"
        )

        content: list = [TextContent(text=message, type="text")]
        content.extend(resource_links)

        return {
            "content": content,
            "structuredContent": {
                "message": message,
                "total_rows": len(stations),
                "columns": list(_STATIONS_CSV_HEADERS.values()),
                "file": file_info,
                "generated": generated,
                "generated_at": datetime.now().isoformat(timespec="seconds"),
            },
            "isError": False,
        }

    @mcp.tool()
    def find_stations_near(
        lat: Annotated[
            float,
            Field(
                description="Latitud del punto central en grados decimales (ej: -9.5, -13.5). Negativo para el hemisferio Sur."
            ),
        ],
        lon: Annotated[
            float,
            Field(
                description="Longitud del punto central en grados decimales (ej: -77.5, -76.3). Negativo para el oeste."
            ),
        ],
        radius_km: Annotated[
            float,
            Field(description="Radio de búsqueda en kilómetros. Por defecto 50 km."),
        ] = 50.0,
        station_type: Annotated[
            str,
            Field(
                description="Tipo de estación: 'all' (todas), 'M' (meteorológicas), 'H' (hidrológicas)."
            ),
        ] = "all",
    ) -> dict:
        """
        Encuentra estaciones SENAMHI cercanas a un punto geográfico.

        Úsala cuando el usuario proporcione coordenadas, un punto de proyecto o
        pregunte por estaciones próximas a una ubicación ya georreferenciada. Filtra
        por radio en kilómetros y opcionalmente por tipo de estación: meteorológica,
        hidrológica o ambas.

        Devuelve estaciones ordenadas de menor a mayor distancia e incluye
        distance_km en cada resultado. Este cálculo de distancia ya está incorporado,
        así que no lo recalcules manualmente.

        Si el usuario necesita una recomendación justificable que combine distancia,
        historial, estado operativo y altitud, usa recommend_station_for_point_tool.
        """
        results = []
        for s in stations:
            if station_type != "all" and s.station_type != station_type:
                continue
            dist = haversine(lat, lon, s.latitude, s.longitude)
            if dist <= radius_km:
                results.append(_serialize(s, distance_km=dist))
        results.sort(key=lambda x: x["distance_km"])
        return build_mcp_success_response(
            f"{len(results)} estación(es) encontrada(s) dentro de {radius_km} km",
            {"stations": results},
        )

    @mcp.tool()
    def filter_stations_by_location(
        department: Annotated[
            str | None,
            Field(
                description="Nombre del departamento (ej: 'Cajamarca', 'Arequipa'). Case-insensitive, parcial."
            ),
        ] = None,
        province: Annotated[
            str | None,
            Field(
                description="Nombre de la provincia (ej: 'Contumaza', 'Caylloma'). Case-insensitive, parcial."
            ),
        ] = None,
        district: Annotated[
            str | None,
            Field(description="Nombre del distrito. Case-insensitive, parcial."),
        ] = None,
    ) -> dict:
        """
        Filtra estaciones SENAMHI por ubicación administrativa del Perú.

        Úsala cuando el usuario mencione un departamento, provincia o distrito y
        quiera conocer las estaciones disponibles allí. Los filtros aceptan
        coincidencias parciales y no distinguen mayúsculas, por lo que sirven para
        búsquedas exploratorias por región o localidad.

        Puedes combinar departamento, provincia y distrito para acotar resultados.
        Devuelve las estaciones que cumplen todos los filtros con sus metadatos
        principales. No filtres manualmente el catálogo completo para este caso.

        Si el usuario entrega coordenadas o pregunta por cercanía real en kilómetros,
        usa find_stations_near en lugar de esta tool.
        """
        results = []
        for s in stations:
            matches = True

            if department and s.department:
                if department.lower() not in s.department.lower():
                    matches = False
            elif department:
                matches = False

            if matches and province and s.province:
                if province.lower() not in s.province.lower():
                    matches = False
            elif matches and province:
                matches = False

            if matches and district and s.district:
                if district.lower() not in s.district.lower():
                    matches = False
            elif matches and district:
                matches = False

            if matches:
                results.append(_serialize(s))

        return build_mcp_success_response(
            f"{len(results)} estación(es) encontrada(s) para los filtros aplicados",
            {"stations": results},
        )

    @mcp.tool()
    def filter_stations_by_altitude(
        min_altitude: Annotated[
            float | None,
            Field(
                description="Altitud mínima en metros sobre el nivel del mar (msnm). Ej: 3000 para zonas altoandinas."
            ),
        ] = None,
        max_altitude: Annotated[
            float | None,
            Field(
                description="Altitud máxima en msnm. Ej: 500 para zonas costeras o valles bajos."
            ),
        ] = None,
    ) -> dict:
        """
        Filtra estaciones SENAMHI por rango de altitud en msnm.

        Úsala cuando el usuario necesite estaciones costeras, de valle, andinas,
        altoandinas o con una altitud mínima/máxima específica. Puedes proporcionar
        solo min_altitude, solo max_altitude o ambos límites.

        Devuelve estaciones con altitud conocida, ordenadas de menor a mayor altitud.
        Las estaciones sin altitud registrada se excluyen cuando se aplica este
        filtro.

        Ejemplos de intención:
        - estaciones costeras: max_altitude=500
        - estaciones altoandinas: min_altitude=3000
        - estaciones entre dos cotas: min_altitude y max_altitude
        """
        results = []
        for s in stations:
            if s.altitude is None:
                continue

            if min_altitude is not None and s.altitude < min_altitude:
                continue
            if max_altitude is not None and s.altitude > max_altitude:
                continue

            results.append(_serialize(s))

        results.sort(key=lambda x: x["altitude"] or 0)
        return build_mcp_success_response(
            f"{len(results)} estación(es) encontrada(s) para el rango de altitud especificado",
            {"stations": results},
        )

    @mcp.tool()
    def check_data_availability(
        station_code: Annotated[
            str | None,
            Field(
                description="Código de una estación específica (ej: '100090'). Si se provee, retorna info de esa estación."
            ),
        ] = None,
        before_year: Annotated[
            int | None,
            Field(
                description="Filtra estaciones con datos disponibles ANTES de este año (ej: 2010 para series largas)."
            ),
        ] = None,
        after_year: Annotated[
            int | None,
            Field(
                description="Filtra estaciones con datos disponibles DESPUÉS de este año (ej: 2022 para series recientes)."
            ),
        ] = None,
    ) -> dict:
        """
        Consulta desde cuándo hay datos históricos disponibles para estaciones SENAMHI.

        Úsala antes de descargar, resumir, comparar o validar datos para confirmar
        que la estación tiene cobertura suficiente para el periodo solicitado. También
        sirve para encontrar estaciones con series largas o con disponibilidad reciente.

        Modos de uso:
        - station_code: devuelve disponibilidad de una estación específica, incluyendo
          data_available_since y years_available.
        - before_year: lista estaciones cuyo inicio de datos es anterior al año dado,
          útil para encontrar series históricas largas.
        - after_year: lista estaciones cuyo inicio de datos es posterior al año dado,
          útil para ubicar estaciones con disponibilidad reciente.
        - before_year + after_year: acota estaciones por ventana de inicio de datos.

        Si el usuario pide descargar un periodo concreto, llama esta tool primero
        cuando no estés seguro de que el periodo esté cubierto por la estación.
        """
        if station_code:
            availability = check_data_availability_service(station_code=station_code)
            if availability is None or availability.station is None:
                return build_mcp_error_response(
                    f"Estación con código '{station_code}' no encontrada"
                )

            return build_mcp_success_response(
                f"Estación encontrada para código '{station_code}'",
                availability.station.model_dump(),
            )

        availability = check_data_availability_service(
            before_year=before_year,
            after_year=after_year,
        )
        results = (
            availability.stations if availability and availability.stations else []
        )

        return build_mcp_success_response(
            f"{len(results)} estación(es) encontrada(s) para los filtros de disponibilidad de datos aplicados",
            availability.model_dump() if availability else {"stations": []},
        )

    @mcp.tool()
    def filter_stations_advanced(
        department: Annotated[
            str | None,
            Field(
                description="Departamento del Perú (ej: 'Arequipa', 'Puno'). Case-insensitive, parcial."
            ),
        ] = None,
        province: Annotated[
            str | None,
            Field(description="Provincia (ej: 'Caylloma'). Case-insensitive, parcial."),
        ] = None,
        station_type: Annotated[
            str | None,
            Field(
                description="Tipo: 'M' = meteorológica, 'H' = hidrológica. Omitir para ambos."
            ),
        ] = None,
        status: Annotated[
            str | None,
            Field(
                description="Estado operativo: 'REAL' (transmisión en tiempo real), 'DIFERIDO', 'AUTOMATICA'."
            ),
        ] = None,
        min_altitude: Annotated[
            float | None,
            Field(description="Altitud mínima en msnm."),
        ] = None,
        max_altitude: Annotated[
            float | None,
            Field(description="Altitud máxima en msnm."),
        ] = None,
        data_before_year: Annotated[
            int | None,
            Field(
                description="Solo estaciones con datos disponibles desde ANTES de este año (para series largas)."
            ),
        ] = None,
    ) -> dict:
        """
        Filtra estaciones SENAMHI combinando varios criterios en una sola consulta.

        Úsala cuando el usuario especifique dos o más condiciones al mismo tiempo,
        por ejemplo ubicación, tipo de estación, estado operativo, altitud y
        disponibilidad histórica. Esta tool evita encadenar filtros separados y
        devuelve directamente las estaciones que cumplen todos los criterios.

        Criterios disponibles:
        departamento, provincia, tipo de estación, estado operativo, altitud mínima,
        altitud máxima y año máximo de inicio de datos.

        Ejemplos de intención:
        - estaciones meteorológicas en Arequipa sobre 2000 msnm
        - estaciones REAL en Puno con datos desde antes de 2020
        - estaciones hidrológicas de una provincia con rango altitudinal específico

        Si la consulta solo tiene un criterio simple, usa la tool específica de
        ubicación, altitud o disponibilidad.
        """
        results = []

        for s in stations:
            if department and s.department:
                if department.lower() not in s.department.lower():
                    continue
            elif department:
                continue

            if province and s.province:
                if province.lower() not in s.province.lower():
                    continue
            elif province:
                continue

            if station_type and s.station_type != station_type:
                continue

            if status and s.status != status:
                continue

            if s.altitude is not None:
                if min_altitude is not None and s.altitude < min_altitude:
                    continue
                if max_altitude is not None and s.altitude > max_altitude:
                    continue
            elif min_altitude is not None or max_altitude is not None:
                continue

            if data_before_year and s.data_available_since:
                try:
                    year = int(s.data_available_since.split("-")[0])
                    if year >= data_before_year:
                        continue
                except (ValueError, IndexError):
                    continue
            elif data_before_year:
                continue

            results.append(_serialize(s))

        return build_mcp_success_response(
            f"{len(results)} estación(es) encontrada(s) para los filtros avanzados aplicados",
            {"stations": results},
        )
