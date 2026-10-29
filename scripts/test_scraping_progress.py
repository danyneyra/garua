"""Progress transport and scraping behavior without SENAMHI or a browser."""

import sys
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import Client, FastMCP
from fastmcp.client.transports import PythonStdioTransport
from fastmcp.server.context import Context

from garua.mcp_tools.download_tools import register_download_tools
from garua.scraping.scraper import process_option
from garua.services.scraping import scrape_station_data_service
from garua.models.scraping import ScrapingServiceSuccessResponse

ROOT = Path(__file__).resolve().parents[1]


class ScrapingProgressTests(unittest.IsolatedAsyncioTestCase):
    async def test_stdio_partial_result_and_progress(self):
        for mode in ("legacy", "2026-07-28"):
            with self.subTest(mode=mode):
                events = []

                async def collect(progress, total, message):
                    events.append((progress, total, message))

                transport = PythonStdioTransport(
                    ROOT / "scripts/scraping_progress_fixture.py",
                    python_cmd=sys.executable,
                    cwd=str(ROOT),
                )
                async with Client(transport, mode=mode, timeout=30) as client:
                    tools = await client.list_tools()
                    schema = tools[0].input_schema
                    self.assertNotIn("ctx", schema["properties"])
                    self.assertNotIn("on_progress", schema["properties"])
                    result = await client.call_tool(
                        "scrape_station_data",
                        {
                            "station_code": "106145",
                            "mode": "year",
                            "year": 2025,
                            "force_download": True,
                        },
                        progress_handler=collect,
                    )
                self.assertFalse(result.is_error)
                self.assertEqual(result.structured_content["stats"]["successful"], 1)
                self.assertGreaterEqual(len(events), 8)
                self.assertEqual(
                    [e[0] for e in events], list(range(1, len(events) + 1))
                )
                self.assertTrue(all(e[1] is None for e in events))
                self.assertTrue(any("Reintentando" in e[2] for e in events))
                self.assertIn("1 fallidos", events[-1][2])

    async def test_local_extraction_never_starts_browser(self):
        response = ScrapingServiceSuccessResponse(
            message="Extraído localmente",
            station_name="Tingo De Ponaza",
            station_code="106145",
            mode="month",
            period="09/2025",
            stats={"successful": 1, "failed": 0, "total": 1},
            files=[],
        )
        events = AsyncMock()
        with (
            patch(
                "garua.services.scraping._try_extract_from_existing",
                return_value=response,
            ),
            patch(
                "garua.services.scraping._run_scraper", new_callable=AsyncMock
            ) as run,
        ):
            result = await scrape_station_data_service(
                "106145", mode="month", year=2025, month=9, on_progress=events
            )
        self.assertTrue(result.success)
        run.assert_not_awaited()
        self.assertIn("archivos locales", events.await_args.args[0])

    async def test_retry_does_not_save_until_response_succeeds(self):
        events = AsyncMock()
        manager = MagicMock()
        with (
            patch(
                "garua.scraping.scraper.capture_post_response",
                new=AsyncMock(
                    side_effect=[TimeoutError(), '<table id="dataTable"></table>']
                ),
            ),
            patch("garua.scraping.scraper.asyncio.sleep", new_callable=AsyncMock),
            patch("garua.scraping.scraper.ui"),
        ):
            result = await process_option(
                MagicMock(),
                MagicMock(),
                {"text": "09/2025", "value": "202509"},
                manager,
                on_progress=events,
                station_label="Estación X",
            )
        self.assertTrue(result)
        manager.save_individual_file.assert_called_once()
        self.assertIn("intento 2", events.await_args.args[0])

    async def test_without_progress_token(self):
        session = SimpleNamespace(send_progress_notification=AsyncMock())
        context = SimpleNamespace(
            request_context=SimpleNamespace(_srctx=SimpleNamespace(meta={})),
            session=session,
        )
        # Exercise the installed FastMCP implementation with an absent token.
        await Context.report_progress(context, 1, message="Preparando descarga")
        session.send_progress_notification.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
