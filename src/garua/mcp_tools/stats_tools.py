"""Tools para estadísticas y resúmenes de estaciones SENAMHI."""

from collections import defaultdict

from garua.services.station import stations
from garua.schemas.mcp import build_mcp_success_response


def register_stats_tools(mcp):
    """Registra las tools de estadísticas en el servidor MCP."""

    @mcp.tool()
    def stations_count() -> dict:
        """
        Devuelve el número total de estaciones SENAMHI disponibles en el catálogo local.

        Úsala cuando el usuario pregunte cuántas estaciones existen en Garúa, cuántas
        estaciones puede consultar el scraper o necesite una cifra global rápida del
        inventario. Esta tool no agrupa ni filtra resultados; solo retorna el total.

        Para desgloses por tipo, estado, departamento o ubicación administrativa,
        usa stations_summary, get_departments_summary o get_location_hierarchy.
        """
        return build_mcp_success_response(
            f"Total de estaciones: {len(stations)}", {"total_stations": len(stations)}
        )

    @mcp.tool()
    def stations_summary() -> dict:
        """
        Devuelve un resumen global de estaciones por tipo y estado operativo.

        Úsala cuando el usuario quiera una visión general del inventario SENAMHI:
        cuántas estaciones hay en total, cuántas son meteorológicas o hidrológicas,
        y cómo se distribuyen según su estado operativo. Es útil para reportes
        rápidos, diagnóstico del catálogo o contexto antes de aplicar filtros.

        La respuesta incluye:
        - total de estaciones
        - conteo por tipo de estación
        - conteo por estado operativo

        Para estadísticas por departamento, altitud promedio o lista de provincias,
        usa get_departments_summary.
        """
        summary = {
            "total": len(stations),
            "by_type": {"M": 0, "H": 0, "unknown": 0},
            "by_status": {"active": 0, "inactive": 0, "unknown": 0},
        }
        for s in stations:
            summary["by_type"].setdefault(s.station_type, 0)
            summary["by_type"][s.station_type] += 1
            summary["by_status"].setdefault(s.status, 0)
            summary["by_status"][s.status] += 1
        return build_mcp_success_response(
            "Resumen de estaciones por tipo y estado", {"summary": summary}
        )

    @mcp.tool()
    def get_departments_summary() -> dict:
        """
        Devuelve estadísticas de estaciones agrupadas por departamento del Perú.

        Úsala cuando el usuario quiera comparar departamentos, saber qué regiones
        tienen más estaciones, identificar cobertura meteorológica o hidrológica por
        departamento, revisar estaciones activas o explorar rangos de altitud por
        región.

        Para cada departamento devuelve:
        - total de estaciones
        - cantidad de estaciones meteorológicas e hidrológicas
        - cantidad de estaciones activas o automáticas
        - altitud promedio, mínima y máxima cuando exista información de altitud
        - lista de provincias con estaciones registradas

        Esta tool resume por departamento. Si el usuario necesita navegar la
        estructura Departamento -> Provincia -> Distrito, usa get_location_hierarchy.
        """
        summary = defaultdict(
            lambda: {
                "total": 0,
                "meteorological": 0,
                "hydrological": 0,
                "altitudes": [],
                "provinces": set(),
                "status_active": 0,
            }
        )

        for s in stations:
            if not s.department:
                continue

            dep = s.department
            summary[dep]["total"] += 1

            if s.station_type == "M":
                summary[dep]["meteorological"] += 1
            elif s.station_type == "H":
                summary[dep]["hydrological"] += 1

            if s.altitude is not None:
                summary[dep]["altitudes"].append(s.altitude)

            if s.province:
                summary[dep]["provinces"].add(s.province)

            if s.status in ["REAL", "AUTOMATICA"]:
                summary[dep]["status_active"] += 1

        result = {}
        for dep, data in summary.items():
            alts = data["altitudes"]
            result[dep] = {
                "total_stations": data["total"],
                "meteorological": data["meteorological"],
                "hydrological": data["hydrological"],
                "active_stations": data["status_active"],
                "altitude_avg": round(sum(alts) / len(alts), 1) if alts else None,
                "altitude_min": min(alts) if alts else None,
                "altitude_max": max(alts) if alts else None,
                "provinces": sorted(list(data["provinces"])),
            }

        return build_mcp_success_response(
            "Resumen de estaciones por departamento",
            {"departments": dict(sorted(result.items()))},
        )

    @mcp.tool()
    def get_location_hierarchy() -> dict:
        """
        Devuelve la jerarquía administrativa de ubicaciones con conteos de estaciones.

        Úsala cuando el usuario quiera explorar dónde existen estaciones SENAMHI por
        departamento, provincia y distrito, o cuando necesite construir una vista tipo
        árbol, selector geográfico o mapa administrativo. Esta tool no devuelve la
        ficha de cada estación; devuelve conteos agregados por nivel geográfico.

        La estructura de salida es:
        Departamento -> Provincias -> Distritos, con total_stations en departamento
        y provincia, y conteo de estaciones por distrito.

        Para métricas estadísticas por departamento como altitud promedio, estaciones
        activas o separación meteorológica/hidrológica, usa get_departments_summary.
        Para obtener estaciones concretas de una ubicación, usa filter_stations_by_location.
        """
        hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

        for s in stations:
            if not s.department:
                continue

            dep = s.department
            prov = s.province or "Sin provincia"
            dist = s.district or "Sin distrito"

            hierarchy[dep][prov][dist] += 1

        result = {}
        for dep, provinces in sorted(hierarchy.items()):
            result[dep] = {
                "total_stations": sum(
                    sum(districts.values()) for districts in provinces.values()
                ),
                "provinces": {},
            }

            for prov, districts in sorted(provinces.items()):
                result[dep]["provinces"][prov] = {
                    "total_stations": sum(districts.values()),
                    "districts": dict(sorted(districts.items())),
                }

        return build_mcp_success_response(
            "Jerarquía de ubicaciones", {"locations": result}
        )
