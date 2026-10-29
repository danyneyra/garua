"""Offline checks for candidate enrichment and read-only catalog handling."""

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from enrich_added_stations import enrich, main

RECORD = {
    "cod": "001", "nom": "PRUEBA", "cate": "CO", "ico": "M",
    "estado": "REAL", "lat": -12.0, "lon": -75.0,
}


def page(options="", selector=True, department="LIMA"):
    select = f'<select id="CBOFiltro">{options}</select>' if selector else ""
    return (
        '<table><tr></tr><tr><font>Estación : PRUEBA</font></tr>'
        f'<tr><td>Departamento</td><td>{department}</td>'
        '<td>Provincia</td><td>LIMA</td><td>Distrito</td><td>LIMA</td>'
        f'<td>{select}</td></tr><tr><td>Altitud</td><td>0 msnm.</td></tr>'
        '<tr><td>Codigo</td><td>000123</td></tr></table>'
    )


def run_enrichment(html):
    response = Mock(status_code=200, content=html.encode(), text=html)
    session = Mock()
    session.get.return_value = response
    args = argparse.Namespace(delay=0, timeout=1, retries=0)
    return enrich(RECORD.copy(), session, args), session


class EnrichmentTests(unittest.TestCase):
    def test_complete_candidate_dates_and_codes(self):
        result, session = run_enrichment(page(
            '<option value="202303">Marzo</option><option value="202201">Enero</option>'
            '<option value="202303">Duplicado</option>'
        ))
        self.assertEqual(result["ficha"], "completa")
        self.assertEqual(result["revision"], "candidata_incorporacion")
        self.assertEqual(result["meses_anunciados"], 2)
        self.assertEqual(result["candidata"]["data_since"], "2022-01")
        self.assertEqual(result["ultimo_mes"], "2023-03")
        self.assertEqual(result["candidata"]["cod_ui"], "000123")
        self.assertIsNone(result["candidata"]["cod_old"])
        self.assertEqual(result["candidata"]["alt"], 0)
        session.get.assert_called_once()
        session.post.assert_not_called()
        self.assertNotIn("cod_ui", RECORD)

    def test_empty_periods_and_incomplete_page_are_independent(self):
        result, _ = run_enrichment(page())
        self.assertEqual(result["ficha"], "completa")
        self.assertEqual(result["disponibilidad"], "sin_periodos_anunciados")
        self.assertEqual(result["revision"], "pendiente_disponibilidad")
        self.assertEqual(result["meses_anunciados"], 0)
        self.assertIsNone(result["candidata"]["data_since"])
        result, _ = run_enrichment(page('<option value="202201">Enero</option>', department=""))
        self.assertEqual(result["ficha"], "incompleta")
        self.assertEqual(result["disponibilidad"], "con_periodos_anunciados")
        self.assertIn("dep", result["campos_faltantes"])
        self.assertEqual(result["revision"], "pendiente_revision")

    def test_missing_or_invalid_selector_preserves_page(self):
        for html in (page(selector=False), page('<option value="202313">Bad</option>')):
            result, _ = run_enrichment(html)
            self.assertEqual(result["ficha"], "completa")
            self.assertEqual(result["disponibilidad"], "no_verificable")
            self.assertIsNone(result["meses_anunciados"])
            self.assertEqual(result["candidata"]["dep"], "LIMA")

    def test_failed_request_or_wrong_identity(self):
        result, _ = run_enrichment(page().replace("PRUEBA", "OTRA"))
        self.assertEqual(result["ficha"], "no_verificable")
        self.assertIsNone(result["candidata"]["cod_ui"])
        session = Mock()
        session.get.side_effect = requests.Timeout("timeout")
        result = enrich(RECORD, session, argparse.Namespace(delay=0, timeout=1, retries=1))
        self.assertEqual(result["disponibilidad"], "no_verificable")
        self.assertEqual(session.get.call_count, 2)

    def test_added_only_resume_and_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            published, current, output = [Path(folder) / name for name in ("old.json", "new.json", "report.json")]
            published.write_text(json.dumps([dict(RECORD, cod="002")]), encoding="utf-8")
            current.write_text(json.dumps([RECORD, dict(RECORD, cod="002")]), encoding="utf-8")
            before = published.read_bytes(), current.read_bytes()
            argv = ["enrich", "--published", str(published), "--current", str(current), "--output"]
            for destination in (published, current):
                with patch("sys.argv", argv + [str(destination)]):
                    self.assertEqual(main(), 1)
            fixture, _ = run_enrichment(page())
            with patch("sys.argv", argv + [str(output)]), patch("enrich_added_stations.enrich", return_value=fixture) as mocked:
                self.assertEqual(main(), 0)
                self.assertEqual(mocked.call_args.args[0]["cod"], "001")
                self.assertEqual(mocked.call_count, 1)
            with patch("sys.argv", argv + [str(output), "--resume"]), patch("enrich_added_stations.enrich") as mocked:
                self.assertEqual(main(), 0)
                mocked.assert_not_called()
            self.assertEqual(before, (published.read_bytes(), current.read_bytes()))


if __name__ == "__main__":
    unittest.main()
