from garua.models.station import Station

_STATION_TYPE_LABEL = {"M": "METEOROLOGICA", "H": "HIDROLOGICA"}


def station_response_serializer(
    station: Station, distance_km: float | None = None
) -> dict:
    """Convierte un objeto Station a dict serializable para la API."""
    d = {
        "name": station.name,
        "code": station.code,
        "type": _STATION_TYPE_LABEL.get(station.station_type, station.station_type),
        "category": station.category,
        "status": station.status,
        "latitude": station.latitude,
        "longitude": station.longitude,
        "department": station.department,
        "province": station.province,
        "district": station.district,
        "altitude": station.altitude,
        "data_available_since": station.data_available_since,
    }
    if distance_km is not None:
        d["distance_km"] = round(distance_km, 2)
    return d
