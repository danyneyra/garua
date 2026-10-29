"""Prepare a reviewable catalog with tracking fields; never publish or edit inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from compare_stations import ROOT, compare, load_catalog
from update_station_metadata import merge_station_metadata

sys.path.insert(0, str(ROOT / "src"))
from garua.models.station import Station

LIMA = timezone(timedelta(hours=-5))


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_report(
    path: Path, hashes: dict, codes: set[str], version: int, scope: str
) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("version") != version or report.get("alcance") != scope:
        raise ValueError(f"{path}: versión o alcance incompatible")
    if report.get("fuentes_sha256") != hashes:
        raise ValueError(f"{path}: las fuentes cambiaron; regenerar el informe")
    entries = {}
    for item in report["estaciones"]:
        code = item["cod"].strip().upper()
        if code not in codes or code in entries:
            raise ValueError(f"{path}: código inesperado o duplicado: {code}")
        entries[code] = item
    return entries


def local_query_date(entry: dict | None) -> str | None:
    if entry is None:
        return None
    stamp = datetime.fromisoformat(entry["consultado_en"])
    if stamp.tzinfo is None:
        raise ValueError("La fecha de consulta debe incluir zona horaria")
    return stamp.astimezone(LIMA).date().isoformat()


def annotate(
    record: dict,
    listed: bool,
    catalog_date: str,
    availability: str,
    query_date: str | None,
) -> dict:
    candidate = dict(record)
    candidate.update(
        catalog_status="listed" if listed else "absent",
        catalog_checked_at=catalog_date,
        availability_status=availability,
        availability_checked_at=query_date,
    )
    notes = []
    if record.get("note"):
        notes.append(record["note"])
    if not listed:
        notes.append(
            f"No figura en el listado SENAMHI de {catalog_date}; no confirma una baja oficial."
        )
    if availability == "periods_announced":
        notes.append(
            "La ficha anuncia periodos; no se verificaron observaciones en tablas."
        )
    elif availability == "no_periods_announced":
        notes.append(
            "La ficha no anuncia periodos; no demuestra ausencia total de datos."
        )
    else:
        notes.append("Listado de meses anunciados aún no determinado.")
    candidate["note"] = " ".join(notes)
    # Validate without normalizing or rewriting the published metadata.
    Station(**candidate)
    return candidate


def prepare(
    published: dict, current: dict, absent: dict, added: dict, catalog_date: str
):
    candidates, review = [], []
    absent_status = {
        "ausente_con_periodos_anunciados": "periods_announced",
        "ausente_sin_periodos_anunciados": "no_periods_announced",
        "no_verificable": "periods_unknown",
    }
    added_status = {
        "con_periodos_anunciados": "periods_announced",
        "sin_periodos_anunciados": "no_periods_announced",
        "no_verificable": "periods_unknown",
    }
    for code, original in published.items():
        entry = absent.get(code)
        status = absent_status[entry["resultado"]] if entry else "periods_unknown"
        updated = merge_station_metadata(original, current.get(code))
        candidates.append(
            annotate(
                updated, code in current, catalog_date, status, local_query_date(entry)
            )
        )
    for code in sorted(current.keys() - published.keys()):
        entry = added.get(code)
        if not entry:
            review.append({"cod": code, "revision": "pendiente_enriquecimiento"})
            continue
        record = entry["candidata"]
        if str(record.get("cod", "")).strip().upper() != code:
            raise ValueError(f"Código de candidata no coincide: {code}")
        status = added_status[entry["disponibilidad"]]
        try:
            candidate = annotate(
                record, True, catalog_date, status, local_query_date(entry)
            )
        except ValueError as exc:
            review.append(
                {"cod": code, "revision": "excluida_por_validacion", "error": str(exc)}
            )
            continue
        candidates.append(candidate)
        review.append(
            {
                "cod": code,
                "revision": entry["revision"],
                "ficha": entry["ficha"],
                "availability_status": status,
                "campos_faltantes": entry["campos_faltantes"],
            }
        )
    return candidates, review


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--published", type=Path, default=ROOT / "src/garua/data/estaciones.json"
    )
    parser.add_argument(
        "--current", type=Path, default=ROOT / "src/garua/data/stations.json"
    )
    parser.add_argument(
        "--absent-report",
        type=Path,
        default=ROOT / "reports/absent-stations-audit.json",
    )
    parser.add_argument(
        "--added-report",
        type=Path,
        default=ROOT / "reports/added-stations-enrichment.json",
    )
    parser.add_argument(
        "--catalog-date",
        required=True,
        type=date.fromisoformat,
        help="Fecha del listado SENAMHI, YYYY-MM-DD; no la de ejecución",
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "reports/stations-candidate.json"
    )
    parser.add_argument(
        "--review-output",
        type=Path,
        default=ROOT / "reports/stations-candidate-review.json",
    )
    args = parser.parse_args()
    try:
        inputs = [
            path.resolve()
            for path in (
                args.published,
                args.current,
                args.absent_report,
                args.added_report,
            )
        ]
        outputs = [args.output.resolve(), args.review_output.resolve()]
        destinations = []
        for output in outputs:
            for destination in (output, output.with_name(output.name + ".tmp")):
                for other in inputs + destinations:
                    if destination == other or (
                        destination.exists()
                        and other.exists()
                        and destination.samefile(other)
                    ):
                        raise ValueError(
                            "Los destinos no pueden sobrescribir entradas ni coincidir entre sí"
                        )
                destinations.append(destination)
        before = {str(path): fingerprint(path) for path in inputs}
        _, published = load_catalog(inputs[0])
        _, current = load_catalog(inputs[1])
        hashes = {str(path): before[str(path)] for path in inputs[:2]}
        absent = read_report(
            inputs[2],
            hashes,
            published.keys() - current.keys(),
            2,
            "periodos_anunciados",
        )
        added = read_report(
            inputs[3],
            hashes,
            current.keys() - published.keys(),
            1,
            "enriquecimiento_agregadas_periodos_anunciados",
        )
        candidates, review = prepare(
            published, current, absent, added, args.catalog_date.isoformat()
        )
        manifest = {
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "catalog_date": args.catalog_date.isoformat(),
            "entradas_sha256": before,
            "total_publicadas": len(published),
            "total_candidatas": len(candidates),
            "agregadas_incluidas": len(candidates) - len(published),
            "resumen": {
                field: dict(Counter(item[field] for item in candidates))
                for field in ("catalog_status", "availability_status")
            },
            "revision_agregadas": review,
            "cambios_estaciones_comunes": compare(published, current)["cambios"],
            "ausentes_sin_auditoria": sorted(
                published.keys() - current.keys() - absent.keys()
            ),
            "criterio": "Conserva publicadas y agregadas válidas, incluso pendientes. Actualiza solo los campos compartidos nom/cate/ico/estado/lat/lon presentes en ambas fuentes. No aplicar sin revisión.",
        }
        if before != {str(path): fingerprint(path) for path in inputs}:
            raise ValueError("Las entradas cambiaron durante la preparación")
        for output, payload in zip(outputs, (candidates, manifest)):
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + ".tmp")
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary.replace(output)
        print(json.dumps(manifest["resumen"], ensure_ascii=False))
        print(
            f"Candidatas: {len(candidates)}. Catálogo: {outputs[0]}. Revisión: {outputs[1]}"
        )
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
