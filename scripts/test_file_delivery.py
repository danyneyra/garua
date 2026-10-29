"""Portable file delivery, bounded embedding and resource access control."""

import base64
import json
import tempfile
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastmcp import Client, FastMCP
from fastmcp.client.transports import PythonStdioTransport

from garua import settings
from garua.mcp_resources import register_resources
from garua.schemas.mcp import build_files_info
from garua.schemas.result import build_tool_result
from garua.services.file_delivery import file_resource_uri, resolve_file_resource
from garua.services.downloaded_files import (
    list_downloaded_csv_files,
    serialize_downloaded_files,
)


class FileDeliveryTests(unittest.IsolatedAsyncioTestCase):
    async def test_generated_uri_is_readable_over_real_stdio(self):
        with tempfile.TemporaryDirectory() as folder:
            csv_dir = Path(folder) / "csv"
            station_dir = csv_dir / "Prueba_123456_M_CO"
            station_dir.mkdir(parents=True)
            path = station_dir / "Prueba-202501.csv"
            path.write_text("Año;Mes;Día\n2025;1;1\n", encoding="utf-8", newline="")
            with patch.object(settings, "CSV_DIR", csv_dir):
                files = serialize_downloaded_files(
                    list_downloaded_csv_files(csv_dir=str(csv_dir))
                )
            self.assertEqual(len(files), 1)
            uri = files[0]["resource_uri"]
            root = Path(__file__).resolve().parents[1]
            transport = PythonStdioTransport(
                root / "src/garua_mcp/__main__.py",
                python_cmd=sys.executable,
                cwd=str(root),
                env={"GARUA_OUTPUT_DIR": folder},
            )
            async with Client(transport, timeout=30) as client:
                contents = await client.read_resource(uri)
            self.assertEqual(contents[0].text, path.read_text(encoding="utf-8"))

    async def test_returned_uri_is_readable_and_small_csv_is_embedded(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(settings, "CSV_DIR", Path(folder)),
            patch.object(settings, "EXPORTS_DIR", Path(folder) / "exports"),
        ):
            path = Path(folder) / "estación prueba.csv"
            text = "Año;Mes;Día\n2025;1;1\n"
            path.write_text(text, encoding="utf-8", newline="")
            files, links = build_files_info([str(path)], "downloaded_file")
            self.assertEqual(str(files[0].uri), path.resolve().as_uri())
            self.assertEqual(files[0].resource_uri, links[0].uri)
            server = FastMCP("file-delivery-test")
            register_resources(server)

            @server.tool()
            def fixture():
                return build_tool_result(
                    content=links,
                    structured_content={
                        "files": [f.model_dump(mode="json") for f in files]
                    },
                )

            for mode in ("legacy", "2026-07-28"):
                async with Client(server, mode=mode) as client:
                    result = await client.call_tool("fixture")
                    resources = await client.read_resource(files[0].resource_uri)
                self.assertEqual(resources[0].text, text)
                embedded = [b for b in result.content if b.type == "resource"]
                self.assertEqual(len(embedded), 1)
                self.assertEqual(embedded[0].resource.text, text)
                self.assertEqual(embedded[0].resource.mime_type, "text/csv")
                self.assertEqual(sum(b.type == "text" for b in result.content), 1)
                self.assertEqual(
                    json.loads(result.content[-1].text), result.structured_content
                )

    async def test_embedding_limits_deduplication_and_disable(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.object(settings, "CSV_DIR", Path(folder)),
            patch.object(settings, "MCP_INLINE_FILE_MAX_BYTES", 4),
            patch.object(settings, "MCP_INLINE_TOTAL_MAX_BYTES", 6),
        ):
            paths = [Path(folder) / f"{i}.csv" for i in range(3)]
            for path, text in zip(paths, ["1234", "123", "12345"]):
                path.write_text(text, encoding="utf-8")
            _, links = build_files_info([str(p) for p in paths], "downloaded_file")
            result = build_tool_result(content=links + links, structured_content={})
            self.assertEqual(sum(b.type == "resource" for b in result.content), 1)
            with patch.object(settings, "MCP_INLINE_FILE_MAX_BYTES", 0):
                result = build_tool_result(content=links, structured_content={})
                self.assertFalse(any(b.type == "resource" for b in result.content))
            server = FastMCP("large-file-read")
            register_resources(server)
            async with Client(server) as client:
                contents = await client.read_resource(links[2].uri)
            self.assertEqual(contents[0].text, "12345")

    async def test_exports_outside_files_and_traversal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "csv"
            exports = Path(folder) / "exports"
            root.mkdir()
            exports.mkdir()
            outside = Path(folder) / "outside.csv"
            outside.write_text("private", encoding="utf-8")
            export = exports / "catálogo.csv"
            export.write_text("Nombre;Código", encoding="utf-8")
            with (
                patch.object(settings, "CSV_DIR", root),
                patch.object(settings, "EXPORTS_DIR", exports),
            ):
                self.assertIsNone(file_resource_uri(outside))
                uri = file_resource_uri(export)
                self.assertEqual(
                    resolve_file_resource(uri.rsplit("/", 1)[1]), export.resolve()
                )
                for identity in (
                    ["csv", "../outside.csv"],
                    ["csv", str(outside)],
                    ["csv", "missing.csv"],
                    ["unknown", "x.csv"],
                ):
                    token = (
                        base64.urlsafe_b64encode(json.dumps(identity).encode())
                        .decode()
                        .rstrip("=")
                    )
                    with self.assertRaises(ValueError):
                        resolve_file_resource(token)
                with self.assertRaises(ValueError):
                    resolve_file_resource("bad-token")


if __name__ == "__main__":
    unittest.main()
