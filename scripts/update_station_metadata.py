"""Prepare or apply shared-field updates, preserving Garúa's enriched data."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from compare_stations import FIELDS, ROOT, compare, load_catalog, normalized

sys.path.insert(0, str(ROOT / "src"))
from garua.models.station import Station


def merge_station_metadata(original: dict, current: dict | None) -> dict:
    merged = dict(original)
    if current:
        if str(current["cod"]).strip().upper() != str(original["cod"]).strip().upper():
            raise ValueError("No se pueden combinar estaciones con códigos diferentes")
        for field in FIELDS:
            if (
                field in original
                and field in current
                and normalized(original[field]) != normalized(current[field])
            ):
                merged[field] = current[field]
    Station(**merged)
    return merged


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
        "--output", type=Path, default=ROOT / "reports/stations-metadata-candidate.json"
    )
    parser.add_argument(
        "--review-output",
        type=Path,
        default=ROOT / "reports/stations-metadata-review.json",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplicar al catálogo publicado tras validación y respaldo",
    )
    args = parser.parse_args()
    try:
        published_path, current_path = args.published.resolve(), args.current.resolve()
        if published_path == current_path or published_path.samefile(current_path):
            raise ValueError("Las fuentes deben ser diferentes")
        original_bytes, current_bytes = (
            published_path.read_bytes(),
            current_path.read_bytes(),
        )
        _, published = load_catalog(published_path)
        _, current = load_catalog(current_path)
        comparison = compare(published, current)
        candidate = [
            merge_station_metadata(record, current.get(code))
            for code, record in published.items()
        ]
        outputs = [args.output.resolve(), args.review_output.resolve()]
        backup = (
            outputs[1].parent
            / f"{published_path.stem}-before-metadata-{digest(original_bytes)[:12]}.json"
        )
        destinations = []
        for output in outputs + [backup]:
            for destination in (output, output.with_name(output.name + ".tmp")):
                for other in [published_path, current_path] + destinations:
                    if destination == other or (
                        destination.exists()
                        and other.exists()
                        and destination.samefile(other)
                    ):
                        raise ValueError(
                            "Los destinos no pueden sobrescribir fuentes ni coincidir entre sí"
                        )
                destinations.append(destination)
        serialized = (
            json.dumps(candidate, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8")
        review = {
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "fuentes_sha256": {
                str(published_path): digest(original_bytes),
                str(current_path): digest(current_bytes),
            },
            "total_estaciones": len(candidate),
            "estaciones_actualizadas": len(comparison["cambios"]),
            "campos_actualizados": sum(
                len(item["campos"]) for item in comparison["cambios"]
            ),
            "cambios": comparison["cambios"],
            "campos_permitidos": list(FIELDS),
            "aplicado": False,
            "respaldo": None,
        }
        if (
            original_bytes != published_path.read_bytes()
            or current_bytes != current_path.read_bytes()
        ):
            raise ValueError("Las fuentes cambiaron durante la preparación")
        if args.apply and comparison["cambios"]:
            if backup.exists() and backup.read_bytes() != original_bytes:
                raise ValueError("Ya existe un respaldo con otro contenido")
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(original_bytes)
            # Validate all records before the only authorized source write.
            published_path.write_bytes(serialized)
            review.update(aplicado=True, respaldo=str(backup))
        for output, payload in zip(outputs, (candidate, review)):
            output.parent.mkdir(parents=True, exist_ok=True)
            temporary = output.with_name(output.name + ".tmp")
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary.replace(output)
        print(
            f"Estaciones: {len(candidate)}; modificadas: {review['estaciones_actualizadas']}; campos: {review['campos_actualizados']}; aplicado: {review['aplicado']}"
        )
        print(f"Informe: {outputs[1]}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
