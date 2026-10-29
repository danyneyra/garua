"""Both MCP output channels must preserve the same data and native links."""

import json
import unittest
from datetime import date

from fastmcp.tools import ToolResult
from mcp.types import ResourceLink, TextContent
from pydantic import BaseModel

from garua.schemas.result import build_tool_result


class Payload(BaseModel):
    name: str
    checked: date


class ResultFallbackTests(unittest.TestCase):
    def test_native_result_normalizes_models_and_preserves_links(self):
        link = ResourceLink(
            type="resource_link", name="datos.csv", uri="file:///datos.csv"
        )
        result = build_tool_result(
            content=[TextContent(type="text", text="Archivo generado"), link],
            structured_content=Payload(
                name="Estación Perú", checked=date(2026, 10, 28)
            ),
        )
        self.assertIs(type(result), ToolResult)
        self.assertEqual(result.content[0], link)
        self.assertEqual(len(result.content), 2)
        self.assertEqual(json.loads(result.content[1].text), result.structured_content)
        self.assertIn("Estación Perú", result.content[1].text)
        self.assertEqual(result.structured_content["message"], "Archivo generado")

    def test_error_details_are_also_available_as_text(self):
        result = build_tool_result(
            content=TextContent(type="text", text="Falló la descarga"),
            structured_content={"error_code": "DOWNLOAD_FAILED", "details": "Timeout"},
            is_error=True,
        )
        self.assertTrue(result.is_error)
        self.assertEqual(len(result.content), 1)
        self.assertEqual(json.loads(result.content[-1].text), result.structured_content)

    def test_existing_message_is_not_duplicated_or_overwritten(self):
        result = build_tool_result(
            content=[TextContent(type="text", text="Resumen")],
            structured_content={"message": "Mensaje completo", "stations": []},
        )
        self.assertEqual(len(result.content), 1)
        self.assertEqual(
            json.loads(result.content[0].text),
            {"message": "Mensaje completo", "stations": []},
        )


if __name__ == "__main__":
    unittest.main()
