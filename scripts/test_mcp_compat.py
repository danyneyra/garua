"""Prevent unreviewed MCP dependency upgrades and metadata drift."""

import tomllib
import unittest
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

from packaging.requirements import Requirement

from garua.mcp_compat import MCP_REQUIREMENTS, ensure_mcp_compatibility


class MCPCompatibilityTests(unittest.TestCase):
    def test_installed_stack_and_project_metadata_agree(self):
        ensure_mcp_compatibility()
        project = tomllib.loads(
            (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(
                encoding="utf-8"
            )
        )
        requirements = {
            item.name: item.specifier
            for item in map(Requirement, project["project"]["dependencies"])
        }
        for name, expected in MCP_REQUIREMENTS.items():
            self.assertEqual(
                str(requirements[name]), str(Requirement(name + expected).specifier)
            )

    def test_major_minor_prerelease_and_old_versions_are_rejected(self):
        valid = {"fastmcp": "4.1.4", "mcp": "2.3.0", "mcp-types": "2.3.0"}
        for name, bad in (
            ("fastmcp", "3.3.1"),
            ("fastmcp", "4.0.8"),
            ("fastmcp", "4.2.0"),
            ("fastmcp", "5.0.0"),
            ("fastmcp", "4.1.5rc1"),
            ("mcp", "2.4.0"),
            ("mcp-types", "3.0.0"),
        ):
            versions = dict(valid, **{name: bad})
            with patch("garua.mcp_compat.version", side_effect=versions.__getitem__):
                with self.assertRaisesRegex(RuntimeError, "fuera del rango probado"):
                    ensure_mcp_compatibility()

    def test_patch_updates_are_allowed(self):
        versions = {"fastmcp": "4.1.5", "mcp": "2.3.1", "mcp-types": "2.3.1"}
        with patch("garua.mcp_compat.version", side_effect=versions.__getitem__):
            ensure_mcp_compatibility()

    def test_missing_dependency_has_actionable_message(self):
        with patch("garua.mcp_compat.version", side_effect=PackageNotFoundError("mcp")):
            with self.assertRaisesRegex(RuntimeError, "python -m pip install"):
                ensure_mcp_compatibility()


if __name__ == "__main__":
    unittest.main()
