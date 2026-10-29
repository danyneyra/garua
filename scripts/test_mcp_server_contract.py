"""Exercise the complete server over native FastMCP and real stdio transports."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import fastmcp
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport

from garua.mcp_server import mcp

ROOT = Path(__file__).resolve().parents[1]


class ServerContractTests(unittest.IsolatedAsyncioTestCase):
    def assert_text_payload_matches(self, result):
        self.assertEqual(sum(block.type == "text" for block in result.content), 1)
        payloads = []
        for block in result.content:
            if block.type == "text":
                try:
                    payloads.append(json.loads(block.text))
                except json.JSONDecodeError:
                    pass
        self.assertEqual(payloads, [result.structured_content])

    async def exercise(self, client):
        tools = await client.list_tools()
        names = {tool.name for tool in tools}
        self.assertIn("scrape_station_data", names)
        self.assertIn("read_csv_preview", names)
        for tool in tools:
            self.assertIsInstance(tool.input_schema, dict)
        result = await client.call_tool("get_station_info", {"code": "106145"})
        self.assertFalse(result.is_error)
        self.assertEqual(result.structured_content["station"]["code"], "106145")
        self.assertNotIn("structuredContent", result.structured_content)
        self.assert_text_payload_matches(result)
        search = await client.call_tool("search_stations", {"query": "106145"})
        self.assert_text_payload_matches(search)
        self.assertEqual(search.structured_content["stations"][0]["code"], "106145")
        empty = await client.call_tool(
            "search_stations", {"query": "NO-SUCH-STATION-XYZ"}
        )
        self.assert_text_payload_matches(empty)
        self.assertEqual(empty.structured_content["stations"], [])
        error = await client.call_tool(
            "get_station_info", {"code": "NOT-A-STATION"}, raise_on_error=False
        )
        self.assertTrue(error.is_error)
        self.assertTrue(error.structured_content["error_code"])
        self.assert_text_payload_matches(error)
        resources = await client.list_resources()
        self.assertTrue(resources)
        contents = await client.read_resource("garua://about")
        about = json.loads(contents[0].text)
        self.assertGreater(about["catalog"]["stations"], 1000)
        templates = await client.list_resource_templates()
        self.assertTrue(templates)
        prompts = await client.list_prompts()
        self.assertTrue(prompts)
        prompt = await client.get_prompt(
            "analizar_periodo_estacion",
            {
                "station": "106145",
                "period": "septiembre de 2026",
            },
        )
        self.assertTrue(prompt.messages)

    async def test_server_without_camelcase_bridge(self):
        previous = fastmcp.settings.mcp_camelcase_compat
        fastmcp.settings.mcp_camelcase_compat = False
        try:
            for mode in ("2026-07-28", "legacy"):
                with self.subTest(mode=mode):
                    async with Client(mcp, mode=mode) as client:
                        await self.exercise(client)
        finally:
            fastmcp.settings.mcp_camelcase_compat = previous

    async def test_actual_stdio_entrypoint(self):
        with tempfile.TemporaryDirectory() as folder:
            transport = PythonStdioTransport(
                ROOT / "src/garua_mcp/__main__.py",
                python_cmd=sys.executable,
                cwd=str(ROOT),
                env={
                    "GARUA_OUTPUT_DIR": folder,
                    "FASTMCP_MCP_CAMELCASE_COMPAT": "false",
                },
            )
            async with Client(transport, timeout=30, init_timeout=30) as client:
                await self.exercise(client)


if __name__ == "__main__":
    unittest.main()
