"""Servicio para generar vistas previas de archivos CSV descargados."""

import csv
from dataclasses import dataclass
from pathlib import Path

from garua import settings
from garua.services.downloaded_files import list_downloaded_csv_files, DownloadedCsvFile

MAX_CSV_PREVIEW_ROWS = 100
MAX_CSV_PREVIEW_COLUMNS = 50


@dataclass(frozen=True)
class CsvPreview:
    """Datos calculados para una vista previa de CSV."""

    source_file: Path
    columns: list[str]
    rows: list[dict]
    total_rows: int
    total_columns: int
    truncated: bool
    truncated_reason: str | None

    @property
    def message(self) -> str:
        return (
            f"Preview del CSV generado: {len(self.rows)} filas y "
            f"{len(self.columns)} columnas."
        )


def preview_file_priority(
    item: DownloadedCsvFile,
    year: int | None = None,
    month: int | None = None,
) -> tuple[int, str]:
    """Prioriza archivos mensuales, anuales o multianuales para una vista previa."""
    period = item.period or {}
    filename = item.filename

    if year is not None and month is not None:
        if period.get("kind") == "month":
            return (0, filename)
        if period.get("kind") == "year":
            return (1, filename)
        if period.get("kind") == "period":
            return (2, filename)

    if year is not None:
        if period.get("kind") == "year":
            return (0, filename)
        if period.get("kind") == "period":
            return (1, filename)
        if period.get("kind") == "month":
            return (2, filename)

    return (3, filename)


def resolve_preview_csv_path(
    csv_dir: Path,
    file_path: str | None,
    relative_path: str | None,
    station_name: str | None,
    station_code: str | None,
    station_type: str | None,
    station_category: str | None,
    year: int | None,
    month: int | None,
) -> Path:
    """Resuelve el CSV que se usará para la vista previa."""
    direct_path = file_path or relative_path
    if direct_path:
        return resolve_csv_path_in_dir(csv_dir=csv_dir, file_path=direct_path)

    if not (station_name or station_code):
        raise ValueError(
            "Debes especificar file_path, relative_path, station_code o station_name."
        )

    matches = list_downloaded_csv_files(
        station_name=station_name,
        station_code=station_code,
        station_type=station_type,
        station_category=station_category,
        year=year,
        month=month,
    )

    if not matches:
        target = station_code or station_name or "la estación indicada"
        raise FileNotFoundError(
            f"No se encontró archivo descargado para {target} "
            "en el periodo solicitado. Usa list_downloaded_files para ver qué hay disponible."
        )

    matches = sorted(
        matches,
        key=lambda item: preview_file_priority(item, year=year, month=month),
    )
    best = matches[0]
    best_priority = preview_file_priority(best, year=year, month=month)

    ambiguous = [
        item
        for item in matches
        if preview_file_priority(item, year=year, month=month) == best_priority
    ]

    if len(ambiguous) > 1:
        options = [
            item.path or item.relative_path or item.filename for item in ambiguous[:10]
        ]
        raise ValueError(
            "Se encontraron múltiples archivos compatibles. "
            f"Usa file_path para elegir uno: {options}"
        )

    selected_path = best.path or best.relative_path
    if not selected_path:
        raise ValueError(
            "El archivo encontrado no incluye path. Revisa list_downloaded_files."
        )

    path = Path(selected_path)
    if not path.is_absolute():
        path = (csv_dir / selected_path).resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Archivo encontrado en índice, pero no existe en disco: {selected_path}"
        )

    return path


def resolve_csv_path_in_dir(csv_dir: Path, file_path: str) -> Path:
    """Resuelve una ruta absoluta o relativa y valida que pertenezca a csv_dir."""
    raw_path = Path(file_path)
    if raw_path.is_absolute():
        path = raw_path.resolve()
    else:
        path = (csv_dir / raw_path).resolve()

    try:
        path.relative_to(csv_dir.resolve())
    except ValueError:
        raise ValueError("La ruta indicada está fuera de la carpeta CSV configurada.")

    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

    return path


def build_csv_preview(
    path: Path,
    year: int | None = None,
    month: int | None = None,
    max_rows: int = 20,
    max_columns: int = 20,
) -> CsvPreview:
    """Lee, filtra y limita un CSV para devolver una vista previa segura."""
    columns, all_rows = read_csv_rows(path)
    filtered_rows = filter_rows_by_period(all_rows, year=year, month=month)
    preview_columns, preview_rows, truncated, truncated_reason = limit_csv_preview(
        columns=columns,
        rows=filtered_rows,
        max_rows=max_rows,
        max_columns=max_columns,
    )

    return CsvPreview(
        source_file=path.resolve(),
        columns=preview_columns,
        rows=preview_rows,
        total_rows=len(filtered_rows),
        total_columns=len(columns),
        truncated=truncated,
        truncated_reason=truncated_reason,
    )


def read_csv_rows(path: Path) -> tuple[list[str], list[dict]]:
    """Lee un CSV SENAMHI usando la configuración de separador del proyecto."""
    with open(path, "r", encoding=settings.CSV_ENCODING, newline="") as f:
        reader = csv.DictReader(f, delimiter=settings.CSV_SEPARATOR)
        columns = list(reader.fieldnames or [])
        rows = list(reader)

    return columns, rows


def filter_rows_by_period(
    rows: list[dict],
    year: int | None = None,
    month: int | None = None,
) -> list[dict]:
    """Filtra filas por año y mes cuando se solicitan."""
    if year is None and month is None:
        return rows

    filtered = []
    for row in rows:
        try:
            row_year = int(row.get("Año", 0))
            row_month = int(row.get("Mes", 0))
        except (TypeError, ValueError):
            continue

        if year is not None and row_year != year:
            continue

        if month is not None and row_month != month:
            continue

        filtered.append(row)

    return filtered


def limit_csv_preview(
    columns: list[str],
    rows: list[dict],
    max_rows: int,
    max_columns: int,
) -> tuple[list[str], list[dict], bool, str | None]:
    """Limita filas y columnas devueltas por la vista previa."""
    effective_rows = min(max_rows, MAX_CSV_PREVIEW_ROWS)
    effective_columns = min(max_columns, MAX_CSV_PREVIEW_COLUMNS)

    preview_columns = columns[:effective_columns]
    preview_rows = [
        {column: row.get(column) for column in preview_columns}
        for row in rows[:effective_rows]
    ]

    reasons = []
    if len(rows) > len(preview_rows):
        reasons.append("filas")
    if len(columns) > len(preview_columns):
        reasons.append("columnas")

    truncated = len(reasons) > 0
    truncated_reason = None
    if truncated:
        truncated_items = " y ".join(reasons)
        truncated_reason = f"Se limitaron {truncated_items} para vista previa."

    return preview_columns, preview_rows, truncated, truncated_reason
