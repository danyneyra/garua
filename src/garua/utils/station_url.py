"""Station page URL construction, independent of catalog loading."""

from urllib.parse import urlencode

from garua import settings


def build_scraping_url_for_station(station) -> str:
    params = {
        "cod": station.code,
        "estado": station.status,
        "tipo_esta": station.station_type,
        "cate": station.category,
        "cod_old": station.legacy_code,
    }
    return f"{settings.BASE_URL}?{urlencode(params)}"
