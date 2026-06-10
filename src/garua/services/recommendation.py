"""Servicio de recomendación de estaciones basado en múltiples criterios."""

from datetime import date
from typing import Literal

from garua.models.recommendation import (
    RecommendationCriteria,
    RecommendationResponse,
    StationRecommendation,
)
from garua.models.station import Station

# Scores por defecto para estados operativos
DEFAULT_STATUS_SCORES = {
    "REAL": 100.0,
    "AUTOMATICA": 90.0,
    "DIFERIDO": 65.0,
}


def calculate_years_available(data_available_since: str | None) -> int | None:
    """
    Calcula cuántos años de datos están disponibles desde data_since hasta hoy.

    Args:
        data_available_since: Fecha en formato "YYYY-MM" o "YYYY"

    Returns:
        Número de años completos o None si no hay información
    """
    if not data_available_since:
        return None

    try:
        parts = data_available_since.split("-")
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1

        current = date.today()
        years = current.year - year

        # Ajustar si aún no hemos llegado al mes de inicio en el año actual
        if current.month < month:
            years -= 1

        return max(0, years)
    except (ValueError, IndexError):
        return None


def distance_score(distance_km: float, radius_km: float) -> float:
    """
    Calcula score basado en distancia (0-100).
    Estaciones más cercanas obtienen mayor score.

    Args:
        distance_km: Distancia de la estación al punto de interés
        radius_km: Radio máximo de búsqueda

    Returns:
        Score de 0 a 100
    """
    if distance_km >= radius_km:
        return 0.0
    return max(0.0, 100.0 * (1.0 - distance_km / radius_km))


def history_score(years_available: int | None) -> float:
    """
    Calcula score basado en años de historial disponible (0-100).
    Más años de datos = mayor score.

    Args:
        years_available: Años de datos históricos disponibles

    Returns:
        Score de 0 a 100
    """
    if years_available is None:
        return 30.0  # Score neutro para estaciones sin información

    if years_available >= 10:
        return 100.0
    if years_available >= 7:
        return 85.0
    if years_available >= 5:
        return 70.0
    if years_available >= 3:
        return 50.0
    if years_available >= 1:
        return 30.0
    return 0.0


def status_score(status: str, prefer_status: list[str] | None = None) -> float:
    """
    Calcula score basado en estado operativo (0-100).
    Prioriza estaciones operativas y automáticas.

    Args:
        status: Estado operativo de la estación
        prefer_status: Lista opcional de estados en orden de prioridad

    Returns:
        Score de 0 a 100
    """
    normalized = status.upper()

    # Si el usuario especificó preferencias, usarlas
    if prefer_status:
        preferred = [s.upper() for s in prefer_status]
        if normalized in preferred:
            index = preferred.index(normalized)
            # Primer elemento = 100, luego decrementa 15 puntos por posición
            return max(50.0, 100.0 - index * 15.0)

    # Usar scores por defecto
    return DEFAULT_STATUS_SCORES.get(normalized, 40.0)


def altitude_score(
    station_altitude: float | None, target_altitude: float | None
) -> float:
    """
    Calcula score basado en similitud de altitud (0-100).
    Solo aplica cuando se conoce la altitud objetivo.

    Args:
        station_altitude: Altitud de la estación en msnm
        target_altitude: Altitud objetivo en msnm

    Returns:
        Score de 0 a 100
    """
    if station_altitude is None or target_altitude is None:
        return 50.0  # Score neutro si no hay información

    diff = abs(station_altitude - target_altitude)

    if diff <= 100:
        return 100.0
    if diff <= 250:
        return 85.0
    if diff <= 500:
        return 70.0
    if diff <= 1000:
        return 45.0
    if diff <= 1500:
        return 25.0
    return 10.0


def build_reason(
    station: dict, score_breakdown: dict[str, float], has_target_altitude: bool
) -> str:
    """
    Construye una explicación en español de por qué se recomienda esta estación.

    Args:
        station: Datos de la estación
        score_breakdown: Desglose de scores por componente
        has_target_altitude: Si se especificó altitud objetivo

    Returns:
        Texto explicativo en español
    """
    reasons = []

    # Distancia
    if station.get("distance_km") is not None:
        dist = station["distance_km"]
        reasons.append(f"está a {dist:.1f} km del punto")

    # Historial
    years = station.get("years_available")
    if years and years > 0:
        if years == 1:
            reasons.append("cuenta con 1 año de datos")
        else:
            reasons.append(f"cuenta con aproximadamente {years} años de datos")

    # Estado operativo
    status = station.get("status")
    if status:
        status_lower = status.lower()
        reasons.append(f"su estado es {status_lower}")

    # Similitud altitudinal (solo si se especificó)
    if has_target_altitude:
        altitude_diff = station.get("altitude_difference_m")
        if altitude_diff is not None:
            if altitude_diff == 0:
                reasons.append("está a la misma altitud")
            else:
                reasons.append(
                    f"tiene una diferencia de altitud de {altitude_diff:.0f} m"
                )

    if not reasons:
        return "Recomendación basada en el mejor score disponible."

    return "Mejor balance: " + ", ".join(reasons) + "."


def calculate_final_score(
    dist_score: float,
    hist_score: float,
    stat_score: float,
    alt_score: float,
    has_target_altitude: bool,
) -> tuple[float, dict[str, float]]:
    """
    Calcula el score final ponderado y devuelve el desglose.

    Args:
        dist_score: Score de distancia
        hist_score: Score de historial
        stat_score: Score de estado
        alt_score: Score de altitud
        has_target_altitude: Si se especificó altitud objetivo

    Returns:
        Tupla (score_final, breakdown)
    """
    if has_target_altitude:
        # Con altitud objetivo
        weights = {
            "distancia": 0.35,
            "historial": 0.30,
            "estado": 0.20,
            "altitud": 0.15,
        }
        final_score = (
            dist_score * weights["distancia"]
            + hist_score * weights["historial"]
            + stat_score * weights["estado"]
            + alt_score * weights["altitud"]
        )
    else:
        # Sin altitud objetivo - redistribuir peso
        weights = {
            "distancia": 0.45,
            "historial": 0.35,
            "estado": 0.20,
        }
        final_score = (
            dist_score * weights["distancia"]
            + hist_score * weights["historial"]
            + stat_score * weights["estado"]
        )

    breakdown = {
        "distancia": round(dist_score, 1),
        "historial": round(hist_score, 1),
        "estado": round(stat_score, 1),
    }

    if has_target_altitude:
        breakdown["altitud"] = round(alt_score, 1)

    return round(final_score, 1), breakdown


def recommend_station_for_point(
    stations: list[Station],
    haversine_fn,
    lat: float,
    lon: float,
    radius_km: float = 100,
    station_type: Literal["M", "H", "all"] = "M",
    target_altitude: float | None = None,
    prefer_status: list[str] | None = None,
    min_years_available: int | None = None,
    limit: int = 5,
) -> RecommendationResponse:
    """
    Recomienda estaciones SENAMHI cercanas a un punto geográfico.

    Evalúa estaciones considerando:
    - Distancia al punto de interés
    - Historial de datos disponible
    - Estado operativo
    - Similitud altitudinal (opcional)

    Args:
        stations: Lista de estaciones disponibles
        haversine_fn: Función para calcular distancia entre coordenadas
        lat: Latitud del punto de interés
        lon: Longitud del punto de interés
        radius_km: Radio máximo de búsqueda en km
        station_type: Tipo de estación ("M", "H", "all")
        target_altitude: Altitud objetivo en msnm (opcional)
        prefer_status: Preferencia de estados operativos
        min_years_available: Años mínimos de historial requeridos
        limit: Número máximo de recomendaciones

    Returns:
        RecommendationResponse con estación recomendada y alternativas
    """
    # Validar criterios
    criteria = RecommendationCriteria(
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        station_type=station_type,
        target_altitude=target_altitude,
        prefer_status=prefer_status,
        min_years_available=min_years_available,
        limit=limit,
    )

    # Buscar estaciones candidatas dentro del radio
    candidates = []
    for station in stations:
        # Filtrar por tipo
        if station_type != "all" and station.station_type != station_type:
            continue

        # Calcular distancia
        dist = haversine_fn(lat, lon, station.latitude, station.longitude)
        if dist > radius_km:
            continue

        # Calcular años disponibles
        years = calculate_years_available(station.data_available_since)

        # Aplicar filtro de años mínimos
        if min_years_available is not None:
            if years is None or years < min_years_available:
                continue

        candidates.append((station, dist, years))

    # Si no hay candidatos
    if not candidates:
        return RecommendationResponse(
            recommended=None,
            alternatives=[],
            criteria=criteria.model_dump(),
            total_candidates=0,
            message="No se encontraron estaciones dentro del radio indicado con los criterios especificados.",
        )

    # Calcular scores para cada candidato
    scored_stations = []
    has_target_alt = target_altitude is not None

    for station, dist, years in candidates:
        # Calcular componentes del score
        dist_sc = distance_score(dist, radius_km)
        hist_sc = history_score(years)
        stat_sc = status_score(station.status, prefer_status)
        alt_sc = altitude_score(station.altitude, target_altitude)

        # Score final ponderado
        final_score, breakdown = calculate_final_score(
            dist_sc, hist_sc, stat_sc, alt_sc, has_target_alt
        )

        # Calcular diferencia de altitud
        alt_diff = None
        if target_altitude is not None and station.altitude is not None:
            alt_diff = abs(station.altitude - target_altitude)

        # Construir datos de recomendación
        station_data = {
            "name": station.name,
            "code": station.code,
            "type": "METEOROLOGICA" if station.station_type == "M" else "HIDROLOGICA",
            "category": station.category,
            "status": station.status,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "department": station.department,
            "province": station.province,
            "district": station.district,
            "altitude": station.altitude,
            "data_available_since": station.data_available_since,
            "years_available": years,
            "distance_km": round(dist, 2),
            "altitude_difference_m": round(alt_diff, 0)
            if alt_diff is not None
            else None,
            "score": final_score,
            "score_breakdown": breakdown,
        }

        # Generar razón
        reason = build_reason(station_data, breakdown, has_target_alt)
        station_data["reason"] = reason

        recommendation = StationRecommendation(**station_data)
        scored_stations.append(recommendation)

    # Ordenar por score descendente
    scored_stations.sort(key=lambda x: x.score, reverse=True)

    # Limitar resultados
    limited = scored_stations[:limit]

    # Separar recomendada y alternativas
    recommended = limited[0] if limited else None
    alternatives = limited[1:] if len(limited) > 1 else []

    # Construir mensaje
    if recommended:
        if alternatives:
            message = (
                f"Se encontró {len(limited)} estación{'es' if len(limited) > 1 else ''} "
                f"recomendada{'s' if len(limited) > 1 else ''} dentro del radio indicado."
            )
        else:
            message = "Se encontró una estación recomendada dentro del radio indicado."
    else:
        message = "No se encontraron estaciones dentro del radio indicado."

    # Preparar criterios para la respuesta
    criteria_dict = criteria.model_dump()
    # Agregar información sobre pesos utilizados
    if has_target_alt:
        criteria_dict["weights"] = {
            "distancia": 0.35,
            "historial": 0.30,
            "estado": 0.20,
            "altitud": 0.15,
        }
    else:
        criteria_dict["weights"] = {
            "distancia": 0.45,
            "historial": 0.35,
            "estado": 0.20,
        }

    return RecommendationResponse(
        recommended=recommended,
        alternatives=alternatives,
        criteria=criteria_dict,
        total_candidates=len(candidates),
        message=message,
    )
