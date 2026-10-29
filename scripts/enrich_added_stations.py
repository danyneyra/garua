"""Enrich added stations from their page and announced months, read-only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import requests

from audit_absent_stations import (
    TIMEOUT_SECONDS,
    build_scraping_url_for_station,
    inspect_identity,
    inspect_periods,
    now,
)
from compare_stations import ROOT, load_catalog

BASE_FIELDS = ("nom", "cate", "lat", "lon", "ico", "cod", "estado", "cod_old")
PAGE_FIELDS = {
    "cod_ui": "frontend_code",
    "dep": "department",
    "prov": "province",
    "dist": "district",
    "alt": "altitude",
}


def missing_fields(candidate: dict) -> list[str]:
    missing = []
    # cod_old is optional; data_since is assessed separately as availability.
    for field in (*BASE_FIELDS[:-1], *PAGE_FIELDS):
        value = candidate.get(field)
        if field in ("lat", "lon", "alt"):
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                missing.append(field)
            elif (field == "lat" and not -90 <= value <= 90) or (field == "lon" and not -180 <= value <= 180) or (field == "alt" and value < -500):
                missing.append(field)
        elif not isinstance(value, str) or not value.strip():
            missing.append(field)
    return missing


def enrich(record: dict, session, args) -> dict:
    candidate = {key: record.get(key) for key in BASE_FIELDS}
    candidate["cod"] = record["cod"].strip().upper()
    candidate.update(dict.fromkeys(PAGE_FIELDS))
    candidate["data_since"] = None
    result = {
        "cod": candidate["cod"], "nom": record["nom"],
        "consultado_en": now(), "ficha": "no_verificable",
        "disponibilidad": "no_verificable", "revision": "pendiente_revision",
        "meses_anunciados": None, "primer_mes": None, "ultimo_mes": None,
        "periodos": None, "candidata": candidate, "errores": [],
    }
    try:
        for key in ("estado", "cate", "ico"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                raise ValueError(f"Campo requerido para consulta: {key}")
        station = SimpleNamespace(
            code=candidate["cod"], status=record["estado"], category=record["cate"],
            station_type=record["ico"], legacy_code=record.get("cod_old") or "",
        )
        result["url"] = build_scraping_url_for_station(station)
        for attempt in range(args.retries + 1):
            try:
                time.sleep(args.delay)
                response = session.get(result["url"], timeout=args.timeout)
                result["http_status"] = response.status_code
                response.raise_for_status()
                break
            except requests.RequestException:
                if attempt == args.retries:
                    raise
        result["html_sha256"] = hashlib.sha256(response.content).hexdigest()
        info = inspect_identity(response.text, record)
        result["identidad_observada"] = info
        for field, source in PAGE_FIELDS.items():
            value = info.get(source)
            candidate[field] = value.strip() or None if isinstance(value, str) else value
        result["ficha"] = "incompleta" if missing_fields(candidate) else "completa"
        # A missing selector must not discard a successfully extracted station page.
        try:
            periods = inspect_periods(response.text)
            result.update(
                periodos=periods, meses_anunciados=len(periods),
                primer_mes=periods[0] if periods else None,
                ultimo_mes=periods[-1] if periods else None,
                disponibilidad="con_periodos_anunciados" if periods else "sin_periodos_anunciados",
            )
            candidate["data_since"] = result["primer_mes"]
        except ValueError as exc:
            result["errores"].append(str(exc))
    except Exception as exc:
        result["errores"].append(str(exc))
    result["campos_faltantes"] = missing_fields(candidate)
    if result["ficha"] == "completa":
        if result["disponibilidad"] == "con_periodos_anunciados":
            result["revision"] = "candidata_incorporacion"
        elif result["disponibilidad"] == "sin_periodos_anunciados":
            result["revision"] = "pendiente_disponibilidad"
    return result


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", type=Path, default=ROOT / "src/garua/data/estaciones.json")
    parser.add_argument("--current", type=Path, default=ROOT / "src/garua/data/stations.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/added-stations-enrichment.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=TIMEOUT_SECONDS)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()
    try:
        if not math.isfinite(args.delay) or not math.isfinite(args.timeout) or args.delay < 0 or args.timeout <= 0 or args.retries < 0 or (args.limit is not None and args.limit < 1):
            raise ValueError("Límites, timeout o pausas inválidos")
        sources = [args.published.resolve(), args.current.resolve()]
        if sources[0] == sources[1] or sources[0].samefile(sources[1]):
            raise ValueError("Las fuentes deben ser diferentes")
        output = args.output.resolve()
        temporary = output.with_name(output.name + ".tmp")
        for destination in (output, temporary):
            if destination in sources or (destination.exists() and any(destination.samefile(source) for source in sources)):
                raise ValueError("El informe o su temporal no pueden sobrescribir una fuente")
        _, published = load_catalog(sources[0])
        _, current = load_catalog(sources[1])
        added = sorted(current.keys() - published.keys())
        fingerprint = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
        report = {
            "version": 1, "alcance": "enriquecimiento_agregadas_periodos_anunciados",
            "fuentes_sha256": fingerprint, "iniciado_en": now(),
            "total_agregadas": len(added), "estaciones": [],
        }
        if args.resume and output.exists():
            previous = json.loads(output.read_text(encoding="utf-8"))
            if any(previous.get(key) != report[key] for key in ("version", "alcance", "fuentes_sha256")):
                raise ValueError("No se puede reanudar: fuentes, alcance o versión diferentes")
            report = previous
        results = {item["cod"]: item for item in report["estaciones"]}
        output.parent.mkdir(parents=True, exist_ok=True)

        def save():
            report.update(
                actualizado_en=now(), estaciones=list(results.values()),
                pendientes=len(added) - len(results),
                resumen={field: dict(Counter(item[field] for item in results.values()))
                         for field in ("ficha", "disponibilidad", "revision")},
            )
            temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(output)

        count = 0
        with requests.Session() as session:
            for code in added:
                existing = results.get(code)
                if existing and existing["ficha"] != "no_verificable" and existing["disponibilidad"] != "no_verificable":
                    continue
                results[code] = enrich(current[code], session, args)
                save()
                print(f"{code}: {results[code]['ficha']} | {results[code]['disponibilidad']}", flush=True)
                count += 1
                if args.limit and count >= args.limit:
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
