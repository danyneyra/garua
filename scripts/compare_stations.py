"""Compare the published catalog against a local SENAMHI snapshot, read-only.

Run from any directory: python scripts/compare_stations.py
Exit codes: 0 = valid comparison (including differences), 1 = invalid input/output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("nom", "cate", "ico", "estado", "lat", "lon")


def load_catalog(path: Path) -> tuple[list[dict], dict[str, dict]]:
    """Reject ambiguous identities instead of silently overwriting duplicates."""
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: se esperaba una lista JSON")
    indexed = {}
    errors = []
    for position, record in enumerate(data, start=1):
        if not isinstance(record, dict):
            errors.append(f"fila {position}: se esperaba un objeto")
            continue
        code = record.get("cod")
        if not isinstance(code, str) or not code.strip():
            errors.append(f"fila {position}: cod debe ser texto no vacío")
            continue
        code = code.strip().upper()
        if code in indexed:
            errors.append(f"fila {position}: código duplicado {code}")
        else:
            indexed[code] = record
        for field in ("nom", "cate", "ico"):
            value = record.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"fila {position} ({code}): {field} debe ser texto no vacío")
    if errors:
        raise ValueError(f"{path}:\n" + "\n".join(errors))
    return data, indexed


def normalized(value: object) -> object:
    if isinstance(value, str):
        return " ".join(value.split()).casefold()
    return value


def compare(published: dict[str, dict], current: dict[str, dict]) -> dict:
    shared = published.keys() & current.keys()
    changed = []
    for code in sorted(shared):
        before, after = published[code], current[code]
        changes = {
            field: {"publicado": before[field], "actual": after[field]}
            for field in FIELDS
            if field in before
            and field in after
            and normalized(before[field]) != normalized(after[field])
        }
        if changes:
            changed.append({"cod": code, "nom": after["nom"], "campos": changes})
    added = [current[code] for code in sorted(current.keys() - published.keys())]
    absent = [published[code] for code in sorted(published.keys() - current.keys())]
    return {
        "resumen": {
            "publicadas": len(published),
            "actuales": len(current),
            "comunes": len(shared),
            "agregadas": len(added),
            "ausentes": len(absent),
            "con_cambios": len(changed),
            "sin_cambios_en_campos_comparados": len(shared) - len(changed),
        },
        "agregadas": added,
        "ausentes": absent,
        "cambios": changed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--published", type=Path, default=ROOT / "src/garua/data/estaciones.json")
    parser.add_argument("--current", type=Path, default=ROOT / "src/garua/data/stations.json")
    parser.add_argument("--output", type=Path, help="Guardar informe JSON; nunca una fuente")
    args = parser.parse_args()
    try:
        sources = (args.published.resolve(), args.current.resolve())
        if sources[0] == sources[1] or sources[0].samefile(sources[1]):
            raise ValueError("Las fuentes deben ser archivos diferentes")
        if args.output:
            output = args.output.resolve()
            if output in sources or (
                output.exists() and any(output.samefile(source) for source in sources)
            ):
                raise ValueError("El informe no puede sobrescribir una fuente")
        _, published = load_catalog(args.published)
        _, current = load_catalog(args.current)
        report = compare(published, current)
        report["fuentes"] = {"publicada": str(sources[0]), "actual": str(sources[1])}
        for key, value in report["resumen"].items():
            print(f"{key}: {value}")
        for key, title in (("agregadas", "Agregadas"), ("ausentes", "Ausentes del listado actual")):
            print(f"\n{title}:")
            for record in report[key]:
                print(f"  {record['cod']} | {record['nom']} | {record['cate']} | {record['ico']}")
        print("\nCambios en estaciones comunes:")
        for record in report["cambios"]:
            print(f"  {record['cod']} | {record['nom']}")
            for field, values in record["campos"].items():
                print(f"    {field}: {values['publicado']!r} -> {values['actual']!r}")
        print("\nAusente no implica descontinuada: requiere verificación posterior.")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
