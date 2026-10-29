"""Tracking defaults, MCP serialization and candidate preparation checks."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from prepare_station_catalog import annotate, main, prepare, read_report
from garua.models.station import Station
from garua.schemas.station import station_response_serializer
from garua.services.station import station_data_availability

RECORD = {
    "cod": "001",
    "nom": "PRUEBA",
    "cate": "CO",
    "ico": "M",
    "estado": "REAL",
    "lat": -12.0,
    "lon": -75.0,
    "data_since": "1999-01",
}


class CatalogPreparationTests(unittest.TestCase):
    def test_legacy_catalog_loads_with_unknown_defaults(self):
        station = Station(**RECORD)
        result = station_response_serializer(station)
        self.assertEqual(result["catalog_status"], "unknown")
        self.assertEqual(result["availability_status"], "periods_unknown")
        self.assertIsNone(result["catalog_checked_at"])

    def test_tracking_is_validated_and_exposed_to_mcp(self):
        candidate = annotate(
            RECORD, False, "2026-10-27", "periods_announced", "2026-10-27"
        )
        station = Station(**candidate)
        result = station_response_serializer(station)
        self.assertEqual(result["catalog_status"], "absent")
        self.assertEqual(result["catalog_checked_at"], "2026-10-27")
        self.assertEqual(
            station_data_availability(station).availability_status, "periods_announced"
        )
        availability = station_data_availability(station).model_dump(mode="json")
        self.assertEqual(availability["availability_checked_at"], "2026-10-27")
        json.dumps(availability)
        with self.assertRaises(ValueError):
            Station(**dict(candidate, catalog_status="discontinued"))
        with self.assertRaises(ValueError):
            Station(**dict(candidate, catalog_checked_at="2026-99-99"))

    def test_preserves_published_and_includes_pending_added_station(self):
        published = {"001": RECORD}
        current = {"002": dict(RECORD, cod="002")}
        absent = {
            "001": {
                "resultado": "ausente_con_periodos_anunciados",
                "consultado_en": "2026-10-28T00:01:00+00:00",
                "data_available_since": "2020-01",
            }
        }
        added = {
            "002": {
                "candidata": current["002"],
                "disponibilidad": "no_verificable",
                "consultado_en": "2026-10-28T00:02:00+00:00",
                "revision": "pendiente_revision",
                "ficha": "incompleta",
                "campos_faltantes": ["dep"],
            }
        }
        candidate, review = prepare(published, current, absent, added, "2026-10-27")
        self.assertEqual(len(candidate), 2)
        self.assertEqual(candidate[0]["data_since"], "1999-01")
        self.assertEqual(candidate[0]["nom"], "PRUEBA")
        self.assertEqual(candidate[0]["availability_checked_at"], "2026-10-27")
        self.assertEqual(candidate[1]["catalog_status"], "listed")
        self.assertEqual(candidate[1]["availability_status"], "periods_unknown")
        self.assertEqual(review[0]["revision"], "pendiente_revision")
        self.assertNotIn("catalog_status", RECORD)

    def test_missing_evidence_does_not_infer_data_from_old_date(self):
        candidates, review = prepare(
            {"001": RECORD}, {"002": dict(RECORD, cod="002")}, {}, {}, "2026-10-27"
        )
        self.assertEqual(candidates[0]["availability_status"], "periods_unknown")
        self.assertIsNone(candidates[0]["availability_checked_at"])
        self.assertEqual(review[0]["revision"], "pendiente_enriquecimiento")

    def test_common_metadata_is_merged_in_future_candidates(self):
        candidates, _ = prepare(
            {"001": RECORD},
            {"001": dict(RECORD, nom="NUEVO", lat=-13.0, data_since="2020-01")},
            {},
            {},
            "2026-10-27",
        )
        self.assertEqual(candidates[0]["nom"], "NUEVO")
        self.assertEqual(candidates[0]["lat"], -13.0)
        self.assertEqual(candidates[0]["data_since"], "1999-01")
        self.assertEqual(RECORD["nom"], "PRUEBA")

    def test_report_fingerprint_and_source_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 2,
                        "alcance": "periodos_anunciados",
                        "fuentes_sha256": {},
                    }
                )
            )
            with self.assertRaises(ValueError):
                read_report(path, {"changed": "hash"}, set(), 2, "periodos_anunciados")
            original = path.read_bytes()
            argv = [
                "prepare",
                "--catalog-date",
                "2026-10-27",
                "--published",
                str(path),
                "--output",
                str(path),
            ]
            with patch("sys.argv", argv):
                self.assertEqual(main(), 1)
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
