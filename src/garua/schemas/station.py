from garua.models.station import Station

_STATION_TYPE_LABEL = {"M": "METEOROLOGICA", "H": "HIDROLOGICA"}


def station_tracking_serializer(station: Station) -> dict:
    return {
        "catalog_status": station.catalog_status,
        "availability_status": station.availability_status,
        "catalog_checked_at": station.catalog_checked_at.isoformat() if station.catalog_checked_at else None,
        "availability_checked_at": station.availability_checked_at.isoformat() if station.availability_checked_at else None,
        "note": station.note,
    }


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
        **station_tracking_serializer(station),
    }
    if distance_km is not None:
        d["distance_km"] = round(distance_km, 2)
    return d
