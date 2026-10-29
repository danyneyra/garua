"""Check release gates and concise notes without publishing anything."""

import tempfile
import unittest
import tomllib
from pathlib import Path

from prepare_release import ROOT, prepare_release


VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]


class ReleaseTests(unittest.TestCase):
    def test_current_release_notes_are_concise(self):
        notes = prepare_release(ROOT, f"v{VERSION}")
        self.assertIn(f"# Garúa {VERSION}", notes)
        self.assertIn("Fecha:", notes)
        self.assertNotIn("???", notes)
        self.assertNotIn("| Código |", notes)
        self.assertNotIn("!!!", notes)
        self.assertIn(f"blob/v{VERSION}/docs/changelog.md", notes)

    def test_wrong_tag_rejected(self):
        with self.assertRaises(ValueError):
            prepare_release(ROOT, "wrong-tag")

    def test_inconsistent_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = (
                "pyproject.toml",
                "uv.lock",
                "CITATION.cff",
                "src/garua/settings.py",
                "docs/changelog.md",
            )
            for name in files:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
            for name in files[1:]:
                target = root / name
                original = target.read_text(encoding="utf-8")
                changed = original.replace(VERSION, "99.99.99")
                self.assertNotEqual(original, changed)
                target.write_text(changed, encoding="utf-8")
                with self.subTest(file=name), self.assertRaises(ValueError):
                    prepare_release(root, f"v{VERSION}")
                target.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
