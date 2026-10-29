"""Offline evidence and source-protection checks."""

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from audit_absent_stations import audit, inspect_page, main

RECORD = {"cod": "001", "nom": "PRUEBA", "cate": "CO", "ico": "M", "estado": "REAL", "data_since": "1999-01"}


def page(options):
    return ('<table><tr></tr><tr><font>Estación : PRUEBA</font></tr>'
            '<tr><td><select id="CBOFiltro">' + options + '</select></td></tr></table>')


class AuditTests(unittest.TestCase):
    def test_dates_sorted_unique_and_fresh(self):
        result = inspect_page(page('<option value="202303">Marzo</option><option value="202201">Enero</option><option value="202303">Duplicado</option>'), RECORD)
        self.assertEqual(result["data_available_since"], "2022-01")
        self.assertEqual(result["meses_anunciados"], 2)
        self.assertFalse(result["fecha_inicial_coincide"])
        self.assertEqual(RECORD["data_since"], "1999-01")

    def test_empty_selector_has_no_announced_periods(self):
        result = inspect_page(page(''), RECORD)
        self.assertIsNone(result["data_available_since"])
        self.assertEqual(result["resultado"], "ausente_sin_periodos_anunciados")
        self.assertEqual(result["meses_anunciados"], 0)

    def test_bad_pages_never_mean_no_data(self):
        for html in ("<html>Error</html>", page('<option value="202313">Bad</option>'), page('').replace("PRUEBA", "OTRA"), page('').replace('id="CBOFiltro"', 'id="otro"')):
            with self.assertRaises(ValueError):
                inspect_page(html, RECORD)

    def test_http_failure_is_inconclusive(self):
        session = Mock()
        session.get.side_effect = requests.Timeout("timeout")
        args = argparse.Namespace(delay=0, retries=1, timeout=1)
        result = audit(RECORD.copy(), session, args)
        self.assertEqual(result["resultado"], "no_verificable")
        self.assertEqual(session.get.call_count, 2)
        self.assertNotIn("data_available_since", result)
        self.assertTrue(result["url"].endswith("cod=001&estado=REAL&tipo_esta=M&cate=CO&cod_old="))

    def test_many_months_only_request_station_page(self):
        response = Mock(status_code=200, content=b"station page")
        response.text = page(''.join(
            f'<option value="{year}{month:02d}">{year}/{month}</option>'
            for year in range(2000, 2026) for month in range(1, 13)
        ))
        session = Mock()
        session.get.return_value = response
        args = argparse.Namespace(delay=0, retries=0, timeout=1)
        result = audit(RECORD.copy(), session, args)
        session.get.assert_called_once()
        session.post.assert_not_called()
        self.assertEqual(result["meses_anunciados"], 312)
        self.assertEqual(result["data_available_since"], "2000-01")
        self.assertEqual(result["ultimo_mes_anunciado"], "2025-12")
        self.assertEqual(result["resultado"], "ausente_con_periodos_anunciados")
        self.assertNotIn("verificacion_mensual", result)

    def test_sources_protected_and_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            published, current, output = [Path(folder) / name for name in ("published.json", "current.json", "report.json")]
            published.write_text(json.dumps([RECORD]), encoding="utf-8")
            current.write_text("[]", encoding="utf-8")
            original = published.read_bytes(), current.read_bytes()
            argv = ["audit", "--published", str(published), "--current", str(current), "--output"]
            with patch("sys.argv", argv + [str(published)]):
                self.assertEqual(main(), 1)
            with patch("sys.argv", argv + [str(output)]), patch("audit_absent_stations.audit", return_value={"cod": "001", "resultado": "ausente_con_periodos_anunciados"}) as mocked:
                self.assertEqual(main(), 0)
                self.assertEqual(mocked.call_count, 1)
            with patch("sys.argv", argv + [str(output), "--resume"]), patch("audit_absent_stations.audit") as mocked:
                self.assertEqual(main(), 0)
                mocked.assert_not_called()
            self.assertEqual(original, (published.read_bytes(), current.read_bytes()))


if __name__ == "__main__":
    unittest.main()
