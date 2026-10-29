"""Shared-field updates must preserve enrichment, tracking and source files."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from update_station_metadata import main, merge_station_metadata

RECORD = {
    "cod": "001",
    "nom": "ANTERIOR",
    "cate": "PLU",
    "ico": "M",
    "estado": "REAL",
    "lat": -12.0,
    "lon": -75.0,
    "cod_ui": "000001",
    "dep": "LIMA",
    "alt": 123,
    "data_since": "1999-01",
    "catalog_status": "listed",
    "catalog_checked_at": "2026-10-27",
    "availability_status": "periods_unknown",
    "note": "Nota existente",
}


class MetadataUpdateTests(unittest.TestCase):
    def test_updates_only_shared_fields_without_mutating_inputs(self):
        current = dict(
            RECORD,
            nom="NUEVO",
            cate="EMA",
            lat=-13.0,
            data_since="2020-01",
            dep="OTRO",
            cod_ui="999",
        )
        merged = merge_station_metadata(RECORD, current)
        self.assertEqual(merged, dict(RECORD, nom="NUEVO", cate="EMA", lat=-13.0))
        self.assertEqual(RECORD["nom"], "ANTERIOR")
        self.assertEqual(merge_station_metadata(RECORD, None), RECORD)

    def test_normalized_text_is_not_rewritten(self):
        self.assertEqual(
            merge_station_metadata(RECORD, dict(RECORD, nom=" anterior ")), RECORD
        )

    def test_invalid_metadata_or_wrong_identity_is_rejected(self):
        for changed in (
            dict(RECORD, lat=100),
            dict(RECORD, cate="INVALID"),
            dict(RECORD, cod="002"),
        ):
            with self.assertRaises(ValueError):
                merge_station_metadata(RECORD, changed)

    def test_preview_apply_backup_and_idempotence(self):
        with tempfile.TemporaryDirectory() as folder:
            published, current, output, review = [
                Path(folder) / name
                for name in ("old.json", "new.json", "candidate.json", "review.json")
            ]
            published.write_text(json.dumps([RECORD]), encoding="utf-8")
            current.write_text(
                json.dumps([dict(RECORD, nom="NUEVO")]), encoding="utf-8"
            )
            original, snapshot = published.read_bytes(), current.read_bytes()
            argv = [
                "update",
                "--published",
                str(published),
                "--current",
                str(current),
                "--output",
                str(output),
                "--review-output",
                str(review),
            ]
            with patch("sys.argv", argv):
                self.assertEqual(main(), 0)
            self.assertEqual(published.read_bytes(), original)
            with patch("sys.argv", argv + ["--apply"]):
                self.assertEqual(main(), 0)
            result = json.loads(review.read_text(encoding="utf-8"))
            self.assertEqual(Path(result["respaldo"]).read_bytes(), original)
            self.assertTrue(result["aplicado"])
            once = published.read_bytes()
            with patch("sys.argv", argv + ["--apply"]):
                self.assertEqual(main(), 0)
            self.assertEqual(published.read_bytes(), once)
            self.assertEqual(current.read_bytes(), snapshot)
            with patch("sys.argv", argv + ["--output", str(current)]):
                self.assertEqual(main(), 1)
            self.assertEqual(current.read_bytes(), snapshot)


if __name__ == "__main__":
    unittest.main()
