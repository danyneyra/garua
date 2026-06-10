"""Tools para búsqueda y filtrado de estaciones SENAMHI."""

from typing import Annotated

from pydantic import Field

from garua.schemas.station import station_response_serializer as _serialize
from garua.services.station import (
    find_station_by_code,
    search_stations_by_name,
    stations,
)
from garua.utils.helpers import haversine
from garua.schemas.mcp import build_mcp_success_response, build_mcp_error_response


def _calculate_years_available(data_since: str | None) -> int | None:
    """Calcula cuántos años de datos están disponibles desde data_since hasta hoy."""
    if not data_since:
        return None
    try:
        year, month = map(int, data_since.split("-"))
        from datetime import datetime

        current = datetime.now()
        years = current.year - year
        if current.month < month:
            years -= 1
        return max(0, years)
    except (ValueError, IndexError):
        return None


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
        Busca estaciones SENAMHI por código exacto o nombre parcial.
        USA ESTA TOOL cuando el usuario mencione el nombre o código de una estación.
        Devuelve: nombre, código, tipo (M/H), categoría, estado, coordenadas,
        departamento, provincia, distrito, altitud y periodo de disponibilidad de datos.
        Si no hay resultados, devuelve lista vacía — no intentes buscar de otra forma.
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
        Devuelve el detalle completo de una estación dado su código interno.
        USA ESTA TOOL para obtener todos los datos de una estación específica.
        Si no se encuentra, devuelve un dict con clave 'error' — no busques de otra forma.
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
    def get_all_stations() -> dict:
        """Devuelve la lista completa de estaciones con sus detalles."""
        return build_mcp_success_response(
            "Lista completa de estaciones",
            {"stations": [_serialize(s) for s in stations]},
        )

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
        Devuelve las estaciones SENAMHI dentro de un radio (km) de las coordenadas dadas.
        USA ESTA TOOL cuando el usuario pregunte por estaciones cercanas a un lugar.
        Resultados ordenados de más cercana a más lejana, con campo 'distance_km'.
        NUNCA calcules distancias manualmente — esta tool ya lo hace.
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
        Filtra estaciones por departamento, provincia o distrito.
        USA ESTA TOOL cuando el usuario mencione una región, ciudad o lugar de Perú.
        La búsqueda es case-insensitive y parcial. Puedes combinar filtros.
        NUNCA filtres la lista manualmente — esta tool ya lo hace.
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
        USA ESTA TOOL cuando el usuario mencione altitud, zonas costeras, andinas, etc.
        Resultados ordenados por altitud ascendente.
        Ejemplos: costeras → max_altitude=500 | altoandinas → min_altitude=3000
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
        Consulta la disponibilidad de datos históricos. USA ESTA TOOL antes de descargar.

        Modo 1 — estación específica: check_data_availability(station_code='100090')
          → retorna desde qué año/mes hay datos y cuántos años disponibles.

        Modo 2 — filtro: check_data_availability(before_year=2010)
          → lista estaciones con series históricas largas (datos desde antes de 2010).

        Modo 3 — rango: check_data_availability(after_year=2022)
          → lista estaciones con datos recientes.
        """
        if station_code:
            station = find_station_by_code(station_code)
            if not station:
                return build_mcp_error_response(
                    f"Estación con código '{station_code}' no encontrada"
                )

            return build_mcp_success_response(
                f"Estación encontrada para código '{station_code}'",
                {
                    "name": station.name,
                    "code": station.code,
                    "data_available_since": station.data_available_since,
                    "years_available": _calculate_years_available(
                        station.data_available_since
                    ),
                },
            )

        results = []
        for s in stations:
            if not s.data_available_since:
                continue

            try:
                year = int(s.data_available_since.split("-")[0])

                if before_year and year >= before_year:
                    continue
                if after_year and year <= after_year:
                    continue

                results.append(
                    {
                        **_serialize(s),
                        "years_available": _calculate_years_available(
                            s.data_available_since
                        ),
                    }
                )
            except (ValueError, IndexError):
                continue

        results.sort(key=lambda x: x["data_available_since"] or "9999")
        return build_mcp_success_response(
            f"{len(results)} estación(es) encontrada(s) para los filtros de disponibilidad de datos aplicados",
            {"stations": results},
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
        Filtro avanzado que combina múltiples criterios en una sola llamada.
        USA ESTA TOOL cuando el usuario especifique dos o más condiciones simultáneas.
        PREFIERE esta tool sobre encadenar múltiples tools de filtro.
        Ejemplo: meteorológicas activas en Arequipa sobre 2000 msnm con datos desde antes de 2020.
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
