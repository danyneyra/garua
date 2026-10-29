"""Run with python -m unittest discover -s scripts -p test_compare_stations.py."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from compare_stations import compare, load_catalog, main


class ComparisonTests(unittest.TestCase):
    def test_additions_absences_and_partial_fields(self):
        old = {"01": {"nom": "Uno", "cate": "CO", "alt": 100}, "02": {"nom": "Dos"}}
        new = {"01": {"nom": " UNO ", "cate": "EMA"}, "03": {"nom": "Tres"}}
        result = compare(old, new)
        self.assertEqual(result["resumen"]["agregadas"], 1)
        self.assertEqual(result["resumen"]["ausentes"], 1)
        self.assertEqual(result["cambios"][0]["campos"], {"cate": {"publicado": "CO", "actual": "EMA"}})

    def test_invalid_identities(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "source.json"
            for codes in (("01", " 01 "), ("",), (1,)):
                source.write_text(json.dumps([{"cod": code, "nom": "Uno", "cate": "CO", "ico": "M"} for code in codes]))
                with self.assertRaises(ValueError):
                    load_catalog(source)

    def test_never_overwrites_source(self):
        with tempfile.TemporaryDirectory() as folder:
            before, after = Path(folder) / "before.json", Path(folder) / "after.json"
            for source in (before, after):
                source.write_text("[]")
            with patch("sys.argv", ["compare", "--published", str(before), "--current", str(after), "--output", str(before)]):
                self.assertEqual(main(), 1)
            self.assertEqual(before.read_text(), "[]")
            self.assertEqual(after.read_text(), "[]")


if __name__ == "__main__":
    unittest.main()
