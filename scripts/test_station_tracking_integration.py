"""Check catalog context survives recommendation and export boundaries."""

import json
import unittest

from garua.models.station import Station
from garua.services.recommendation import recommend_station_for_point
from garua.mcp_tools.station_tools import _STATIONS_CSV_HEADERS
from garua.schemas.station import station_response_serializer


class TrackingIntegrationTests(unittest.TestCase):
    def test_recommendation_keeps_historical_station_and_context(self):
        record = {"cod": "001", "nom": "PRUEBA", "cate": "CO", "ico": "M",
                  "estado": "REAL", "lat": -12.0, "lon": -75.0, "data_since": "2000-01"}
        plain = Station(**record)
        tagged = Station(**dict(record, catalog_status="absent", availability_status="periods_announced",
                                catalog_checked_at="2026-10-27", note="No figura en el listado consultado."))
        def recommend(station):
            return recommend_station_for_point([station], lambda *args: 0, lat=-12.0, lon=-75.0)
        result = recommend(tagged)
        self.assertIsNotNone(result.recommended)
        self.assertEqual(result.recommended.code, "001")
        self.assertEqual(result.recommended.catalog_status, "absent")
        self.assertEqual(result.recommended.score, recommend(plain).recommended.score)
        payload = result.model_dump(mode="json")
        self.assertEqual(payload["recommended"]["catalog_checked_at"], "2026-10-27")
        json.dumps(payload)
        serialized = station_response_serializer(tagged)
        for key in ("catalog_status", "availability_status", "catalog_checked_at", "availability_checked_at", "note"):
            self.assertIn(key, _STATIONS_CSV_HEADERS)
            self.assertIn(key, serialized)


if __name__ == "__main__":
    unittest.main()
