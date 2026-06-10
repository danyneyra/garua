"""Tools para estadísticas y resúmenes de estaciones SENAMHI."""

from collections import defaultdict

from garua.services.station import stations
from garua.schemas.mcp import build_mcp_success_response


def register_stats_tools(mcp):
    """Registra las tools de estadísticas en el servidor MCP."""

    @mcp.tool()
    def stations_count() -> dict:
        """Devuelve el número total de estaciones disponibles en el scraper."""
        return build_mcp_success_response(
            f"Total de estaciones: {len(stations)}", {"total_stations": len(stations)}
        )

    @mcp.tool()
    def stations_summary() -> dict:
        """Devuelve un resumen con el conteo de estaciones por tipo y estado."""
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
        Devuelve un resumen estadístico agrupado por departamento:
        - Cantidad total de estaciones
        - Estaciones por tipo (meteorológicas/hidrológicas)
        - Altitud promedio, mínima y máxima
        - Lista de provincias
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
        Devuelve la estructura jerárquica completa de ubicaciones:
        Departamento → Provincias → Distritos con conteo de estaciones en cada nivel.
        Útil para explorar la distribución geográfica de estaciones.
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
