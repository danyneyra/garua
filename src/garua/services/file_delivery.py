"""Portable MCP references to CSV files in Garúa's output directories."""

import base64
import binascii
import json
from pathlib import Path

from garua import settings

RESOURCE_PREFIX = "garua://files/"


def _roots() -> dict[str, Path]:
    return {
        "csv": settings.CSV_DIR.resolve(),
        "exports": settings.EXPORTS_DIR.resolve(),
    }


def file_resource_uri(path: Path) -> str | None:
    """Return a readable resource only for existing CSVs inside managed roots."""
    resolved = path.resolve()
    if resolved.suffix.lower() != ".csv" or not resolved.is_file():
        return None
    for area, root in _roots().items():
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            continue
        identity = json.dumps([area, relative.as_posix()], ensure_ascii=False)
        file_id = (
            base64.urlsafe_b64encode(identity.encode("utf-8")).decode().rstrip("=")
        )
        return RESOURCE_PREFIX + file_id
    return None


def resolve_file_resource(file_id: str) -> Path:
    """Validate identifiers again on every read, including resolved symlinks."""
    try:
        if not file_id or len(file_id) > 8192:
            raise ValueError("Identificador inválido")
        raw = base64.b64decode(
            file_id + "=" * (-len(file_id) % 4), altchars=b"-_", validate=True
        )
        area, relative = json.loads(raw.decode("utf-8"))
        if not isinstance(area, str) or not isinstance(relative, str):
            raise ValueError("Identificador inválido")
        root = _roots()[area]
        path = (root / relative).resolve()
        path.relative_to(root)
        if path.suffix.lower() != ".csv" or not path.is_file():
            raise ValueError("CSV no disponible")
        return path
    except (ValueError, TypeError, KeyError, UnicodeError, binascii.Error) as exc:
        raise ValueError(
            "Recurso CSV inválido o fuera de los directorios de Garúa."
        ) from exc


def read_file_resource(file_id: str) -> str:
    return resolve_file_resource(file_id).read_bytes().decode(settings.CSV_ENCODING)


def read_inline_resource(uri: str, limit: int) -> str | None:
    """Read at most limit+1 bytes; oversized files are never truncated inline."""
    if limit <= 0 or not uri.startswith(RESOURCE_PREFIX):
        return None
    try:
        path = resolve_file_resource(uri[len(RESOURCE_PREFIX) :])
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            return None
        return data.decode(settings.CSV_ENCODING)
    except (OSError, ValueError, UnicodeError):
        # A missing/unreadable optional attachment must not invalidate a result.
        return None
