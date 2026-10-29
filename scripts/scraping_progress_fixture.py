"""Offline stdio server exercising the real download tool and service."""

from fastmcp import FastMCP

from garua.mcp_tools.download_tools import register_download_tools
import garua.scraping.scraper as scraper


async def simulated_scraper(station, params, on_progress=None):
    from garua.scraping.progress import emit_progress

    for message in (
        f"Conectando con SENAMHI para {station.name}.",
        f"Descargando 09/2025 de {station.name}: periodo 1 de 2.",
        f"Reintentando 09/2025 de {station.name}: intento 2 de 3.",
        f"09/2025 de {station.name}: fallido; 1 de 2 periodos procesados.",
        f"Descargando 10/2025 de {station.name}: periodo 2 de 2.",
        f"Guardando archivo consolidado de {station.name}.",
    ):
        await emit_progress(on_progress, message)
    return {
        "success": True,
        "station_name": station.name,
        "mode": params.mode,
        "saved_files": [],
        "successful_count": 1,
        "total_options": 2,
    }


scraper.scraping_main = simulated_scraper
server = FastMCP("offline-scraping-progress")
register_download_tools(server)

if __name__ == "__main__":
    server.run()
