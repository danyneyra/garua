"""Exercise FastMCP argument validation without browser or network downloads."""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import ANY, AsyncMock, patch

from fastmcp import Client, FastMCP

from garua.mcp_tools.download_tools import register_download_tools
from garua.models.scraping import (
    ScrapingServiceErrorResponse,
    ScrapingServiceSuccessResponse,
)
from garua.schemas.mcp import build_files_info


class ScrapingMCPArgumentTests(unittest.IsolatedAsyncioTestCase):
    async def test_consecutive_months_reach_scraper_in_one_session(self):
        server = FastMCP("scraping-batch-test")
        register_download_tools(server)
        periods = [{"year": 2025, "month": month} for month in (1, 2, 3)]
        with patch(
            "garua.services.scraping._run_scraper",
            new=AsyncMock(
                return_value={"success": False, "error": "Simulación sin navegador"}
            ),
        ) as scraper:
            async with Client(server) as client:
                result = await client.call_tool(
                    "scrape_station_data",
                    {
                        "station_code": "106145",
                        "periods": periods,
                        "force_download": True,
                    },
                    raise_on_error=False,
                )
        scraper.assert_awaited_once()
        query = scraper.await_args.args[1]
        self.assertEqual([p.model_dump() for p in query.mcp_filter_periods], periods)
        self.assertTrue(result.is_error)
        self.assertEqual(sum(b.type == "text" for b in result.content), 1)

    async def test_success_with_file_returns_serializable_links(self):
        server = FastMCP("scraping-success-test")
        register_download_tools(server)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "estación prueba-202609.csv"
            path.write_text("Año;Mes;Día\n2026;9;1\n", encoding="utf-8")
            response = ScrapingServiceSuccessResponse(
                message="Archivo descargado",
                station_name="Tingo De Ponaza",
                station_code="106145",
                mode="month",
                period="09/2026",
                stats={"successful": 1, "failed": 0, "total": 1},
                files=[str(path)],
            )
            with patch(
                "garua.mcp_tools.download_tools.scrape_station_data_service",
                new=AsyncMock(return_value=response),
            ):
                async with Client(server) as client:
                    result = await client.call_tool(
                        "scrape_station_data",
                        {
                            "mode": "month",
                            "month": 9,
                            "station_code": "106145",
                            "year": 2026,
                        },
                        raise_on_error=False,
                    )
            self.assertFalse(result.is_error)
            payload = result.structured_content
            self.assertTrue(payload["success"])
            self.assertEqual(payload["files"][0]["uri"], path.as_uri())
            links = [item for item in result.content if item.type == "resource_link"]
            self.assertEqual(links[0].uri, path.as_uri())
            text_payload = json.loads(result.content[-1].text)
            self.assertEqual(text_payload, payload)
            json.dumps(payload)

    async def test_reported_payload_reaches_service(self):
        server = FastMCP("scraping-argument-test")
        register_download_tools(server)
        response = ScrapingServiceErrorResponse(
            message="Simulación sin descarga",
            error_code="diagnostic",
            station_code="106145",
        )
        payload = {"mode": "month", "month": 9, "station_code": "106145", "year": 2026}
        with patch(
            "garua.mcp_tools.download_tools.scrape_station_data_service",
            new=AsyncMock(return_value=response),
        ) as service:
            async with Client(server) as client:
                result = await client.call_tool(
                    "scrape_station_data", payload, raise_on_error=False
                )
        self.assertTrue(result.is_error)
        self.assertEqual(result.structured_content["error_code"], "DIAGNOSTIC")
        service.assert_awaited_once_with(
            station_code="106145",
            mode="month",
            year=2026,
            month=9,
            start_year=None,
            end_year=None,
            individual=False,
            periods=None,
            force_download=False,
            on_progress=ANY,
        )

    async def test_numeric_station_code_is_rejected_before_service(self):
        server = FastMCP("scraping-invalid-argument-test")
        register_download_tools(server)
        with patch(
            "garua.mcp_tools.download_tools.scrape_station_data_service",
            new=AsyncMock(),
        ) as service:
            async with Client(server) as client:
                result = await client.call_tool(
                    "scrape_station_data",
                    {
                        "mode": "month",
                        "month": 9,
                        "station_code": 106145,
                        "year": 2026,
                    },
                    raise_on_error=False,
                )
        self.assertTrue(result.is_error)
        service.assert_not_awaited()
        message = " ".join(
            item.text for item in result.content if hasattr(item, "text")
        )
        self.assertIn("station_code", message)


class FileLinkTests(unittest.TestCase):
    def test_resource_link_uri_is_text(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "prueba.csv"
            path.write_text("test", encoding="utf-8")
            files, links = build_files_info([str(path)], kind="downloaded_file")
            self.assertIsInstance(links[0].uri, str)
            self.assertEqual(links[0].uri, path.as_uri())
            self.assertEqual(files[0].size_bytes, 4)


if __name__ == "__main__":
    unittest.main()
