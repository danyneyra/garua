"""Validate a stable release and extract concise notes from the changelog."""

from __future__ import annotations

import argparse
import ast
from datetime import date
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def prepare_release(root: Path, tag: str) -> str:
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version = project["project"]["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version) or tag != f"v{version}":
        raise ValueError(
            f"La etiqueta {tag!r} no coincide con la versión estable v{version}"
        )
    settings = ast.parse((root / "src/garua/settings.py").read_text(encoding="utf-8"))
    versions = [
        ast.literal_eval(node.value)
        for node in settings.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "VERSION"
            for target in node.targets
        )
    ]
    if versions != [version]:
        raise ValueError("settings.VERSION no coincide con pyproject.toml")
    lock = tomllib.loads((root / "uv.lock").read_text(encoding="utf-8"))
    locked = [
        package["version"]
        for package in lock["package"]
        if package["name"] == project["project"]["name"]
    ]
    if locked != [version]:
        raise ValueError("uv.lock no coincide con pyproject.toml")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")
    citation_version = re.search(r'^version:\s*["\']?([^"\'\s]+)', citation, re.M)
    released = re.search(r'^date-released:\s*["\']?(\d{4}-\d{2}-\d{2})', citation, re.M)
    if not citation_version or citation_version.group(1) != version or not released:
        raise ValueError("CITATION.cff no coincide o no tiene fecha de publicación")
    release_date = date.fromisoformat(released.group(1)).isoformat()
    changelog = (root / "docs/changelog.md").read_text(encoding="utf-8")
    section = re.search(
        rf"^## {re.escape(tag)} - {release_date}\s*\n(.*?)(?=^## |\Z)",
        changelog,
        re.M | re.S,
    )
    if not section:
        raise ValueError(
            "Falta una entrada del changelog con la versión y fecha de CITATION.cff"
        )
    notes = []
    skipping = False
    admonition = False
    for line in section.group(1).splitlines():
        if line.startswith("??? "):
            skipping = True
            continue
        if skipping:
            if not line.strip() or line.startswith((" ", "\t")):
                continue
            skipping = False
        if line.startswith("!!! "):
            title = re.search(r'"([^"]+)"', line)
            notes.extend(["", f"**{title.group(1) if title else 'Nota'}**", ""])
            admonition = True
            continue
        if admonition and line.startswith("    "):
            line = line[4:]
        elif line.strip():
            admonition = False
        notes.append(line)
    body = "\n".join(notes).strip()
    if not body:
        raise ValueError("Las notas del release están vacías")
    repository = project["project"]["urls"]["Repository"].rstrip("/")
    return f"# Garúa {version}\n\nFecha: {release_date}\n\n{body}\n\n[Changelog detallado]({repository}/blob/{tag}/docs/changelog.md)\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tag", required=True)
    parser.add_argument(
        "--notes-output", type=Path, default=ROOT / "reports/release-notes.md"
    )
    args = parser.parse_args()
    try:
        notes = prepare_release(args.root, args.tag)
        output = args.notes_output.resolve()
        inputs = [
            args.root / name
            for name in (
                "pyproject.toml",
                "uv.lock",
                "CITATION.cff",
                "src/garua/settings.py",
                "docs/changelog.md",
            )
        ]
        if any(
            output == path.resolve() or (output.exists() and output.samefile(path))
            for path in inputs
        ):
            raise ValueError("El destino de notas no puede sobrescribir una entrada")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(notes, encoding="utf-8")
        print(f"Release validado: {args.tag}. Notas: {output}")
        return 0
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
