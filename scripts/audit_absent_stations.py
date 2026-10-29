"""Audit absent stations without changing either source catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from bs4 import BeautifulSoup
import requests

from compare_stations import ROOT, load_catalog, normalized

sys.path.insert(0, str(ROOT / "src"))
from garua.utils.station_url import build_scraping_url_for_station
from garua.settings import TIMEOUT_SECONDS
from garua.utils.html_utils import extract_station_info


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def inspect_identity(html: str, record: dict) -> dict:
    """Use fresh response only; never inherit a published availability date."""
    soup = BeautifulSoup(html, "html.parser")
    if re.search(r"(?:Fatal error|Warning|Parse error):", soup.get_text()):
        raise ValueError("La página contiene errores del servidor")
    info = extract_station_info(html) or {}
    known_codes = {str(record.get(key, "")).strip().upper() for key in ("cod", "cod_old", "cod_ui")}
    known_codes.discard("")
    identity_ok = (
        normalized(info.get("name", "")) == normalized(record["nom"])
        or str(info.get("frontend_code", "")).strip().upper() in known_codes
    )
    if not identity_ok:
        raise ValueError("No se pudo confirmar la identidad de la estación")
    info.pop("data_available_since", None)
    return info


def inspect_periods(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    select = soup.find("select", id="CBOFiltro")
    if select is None:
        raise ValueError("No se encontró CBOFiltro; no demuestra ausencia de datos")
    periods, invalid = set(), []
    for option in select.find_all("option"):
        value = str(option.get("value", "")).strip()
        if not value or value in ("0", "-1"):
            continue
        if not re.fullmatch(r"\d{6}", value):
            invalid.append(value)
            continue
        try:
            period = date(int(value[:4]), int(value[4:]), 1)
        except ValueError:
            invalid.append(value)
            continue
        if period > date.today().replace(day=1):
            invalid.append(value)
        else:
            periods.add(period.strftime("%Y-%m"))
    if invalid:
        raise ValueError(f"Opciones de fecha inválidas: {invalid}")
    return sorted(periods)


def inspect_page(html: str, record: dict) -> dict:
    info = inspect_identity(html, record)
    periods = inspect_periods(html)
    since = periods[0] if periods else None
    return {
        "identidad_observada": info,
        "periodos": periods,
        "meses_anunciados": len(periods),
        "data_available_since": since,
        "ultimo_mes_anunciado": periods[-1] if periods else None,
        "data_since_publicado": record.get("data_since"),
        "fecha_inicial_coincide": record.get("data_since") == since,
        "resultado": "ausente_con_periodos_anunciados" if periods else "ausente_sin_periodos_anunciados",
        "motivo": None if periods else "Selector sin meses: no confirma ausencia de observaciones",
    }


def audit(record: dict, session, args) -> dict:
    result = {"cod": record["cod"].strip().upper(), "nom": record["nom"], "consultado_en": now(),
              "resultado": "no_verificable", "data_since_publicado": record.get("data_since")}
    try:
        for field in ("estado", "cate", "ico"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"Campo requerido para consulta: {field}")
        station = SimpleNamespace(code=record["cod"].strip().upper(), status=record["estado"],
                                  category=record["cate"], station_type=record["ico"],
                                  legacy_code=record.get("cod_old") or "")
        url = build_scraping_url_for_station(station)
        result["url"] = url
        for attempt in range(args.retries + 1):
            try:
                time.sleep(args.delay)
                response = session.get(url, timeout=args.timeout)
                result["http_status"] = response.status_code
                response.raise_for_status()
                break
            except requests.RequestException:
                if attempt == args.retries:
                    raise
        result["html_sha256"] = hashlib.sha256(response.content).hexdigest()
        result.update(inspect_page(response.text, record))
    except Exception as exc:
        result.update(resultado="no_verificable", motivo=str(exc))
    return result


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", type=Path, default=ROOT / "src/garua/data/estaciones.json")
    parser.add_argument("--current", type=Path, default=ROOT / "src/garua/data/stations.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/absent-stations-audit.json")
    parser.add_argument("--resume", action="store_true", help="Reutilizar éxitos del mismo par de fuentes")
    parser.add_argument("--limit", type=int, help="Máximo de estaciones nuevas por ejecución")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    try:
        if args.delay < 0 or args.timeout <= 0 or args.retries < 0 or (args.limit is not None and args.limit < 1):
            raise ValueError("Límites, timeout y pausas inválidos")
        sources = [args.published.resolve(), args.current.resolve()]
        output = args.output.resolve()
        temporary = output.with_name(output.name + ".tmp")
        for destination in (output, temporary):
            if destination in sources or (destination.exists() and any(destination.samefile(source) for source in sources)):
                raise ValueError("El informe o su temporal no pueden sobrescribir una fuente")
        _, published = load_catalog(sources[0])
        _, current = load_catalog(sources[1])
        absent = sorted(published.keys() - current.keys())
        fingerprint = {str(source): hashlib.sha256(source.read_bytes()).hexdigest() for source in sources}
        report = {"version": 2, "fuentes_sha256": fingerprint, "alcance": "periodos_anunciados",
                  "iniciado_en": now(), "total_ausentes": len(absent), "estaciones": []}
        if args.resume and output.exists():
            report = json.loads(output.read_text(encoding="utf-8"))
            if report.get("fuentes_sha256") != fingerprint or report.get("alcance") != "periodos_anunciados" or report.get("version") != 2:
                raise ValueError("No se puede reanudar: fuentes, modo o versión diferentes")
        results = {item["cod"].strip().upper(): item for item in report["estaciones"]}
        done = 0
        output.parent.mkdir(parents=True, exist_ok=True)

        def save():
            report.update(actualizado_en=now(), estaciones=list(results.values()),
                          pendientes=len(absent) - len(results),
                          resumen=dict(Counter(item["resultado"] for item in results.values())))
            temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(output)

        with requests.Session() as session:
            for code in absent:
                if code in results and results[code]["resultado"] != "no_verificable":
                    continue
                result = audit(published[code], session, args)
                results[code] = result
                save()
                print(f"{code}: {result['resultado']}", flush=True)
                done += 1
                if args.limit and done >= args.limit:
                    break
        save()
        print(json.dumps(report["resumen"], ensure_ascii=False))
        print(f"Pendientes: {report['pendientes']}. Informe: {output}")
        return 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
