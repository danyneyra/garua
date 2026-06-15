"""Servicio para listar archivos CSV descargados."""

from dataclasses import dataclass
from pathlib import Path

from garua.settings import CSV_DIR
from garua.utils.helpers import (
    normalize_station_slug,
    parse_csv_period,
    period_covers_request,
    station_folder_matches,
)


@dataclass(frozen=True)
class DownloadedCsvFile:
    """Metadata compacta de un CSV descargado."""

    filename: str
    path: Path
    relative_path: str
    uri: str
    station: str
    station_code: str | None
    station_type: str | None
    station_category: str | None
    size_kb: float
    period: dict
    covers_period: str
    covers_requested_period: bool
    can_extract_requested_month: bool

    def model_dump(self) -> dict:
        return {
            "filename": self.filename,
            "path": str(self.path),
            "relative_path": self.relative_path,
            "uri": self.uri,
            "station": self.station,
            "station_code": self.station_code,
            "station_type": self.station_type,
            "station_category": self.station_category,
            "size_kb": self.size_kb,
            "period": self.period,
            "covers_period": self.covers_period,
            "covers_requested_period": self.covers_requested_period,
            "can_extract_requested_month": self.can_extract_requested_month,
        }


def list_downloaded_csv_files(
    csv_dir: str | None = None,
    station_name: str | None = None,
    station_code: str | None = None,
    station_type: str | None = None,
    station_category: str | None = None,
    year: int | None = None,
    month: int | None = None,
    include_covering_files: bool = True,
) -> list[DownloadedCsvFile]:
    """Lista CSV descargados que coinciden con los filtros dados."""

    base_dir = Path(csv_dir) if csv_dir else CSV_DIR

    if not base_dir.exists():
        return []

    station_slug = normalize_station_slug(station_name) if station_name else None
    code_filter = station_code.strip().upper() if station_code else None
    type_filter = station_type.strip().upper() if station_type else None
    category_filter = station_category.strip().upper() if station_category else None
    files: list[DownloadedCsvFile] = []

    for station_dir in sorted(path for path in base_dir.iterdir() if path.is_dir()):
        station_meta = station_folder_matches(
            station_dir.name,
            station_name=station_name,
            station_code=station_code,
            station_type=station_type,
            station_category=station_category,
        )

        if not station_meta:
            continue

        if station_slug and station_meta["station_slug"] != station_slug:
            continue

        if code_filter and station_meta.get("station_code") != code_filter:
            continue

        if type_filter and station_meta.get("station_type") != type_filter:
            continue

        if category_filter and station_meta.get("station_category") != category_filter:
            continue

        files.extend(
            _list_station_csv_files(
                base_dir=base_dir,
                station_dir=station_dir,
                station_meta=station_meta,
                year=year,
                month=month,
                include_covering_files=include_covering_files,
            )
        )

    return files


def _list_station_csv_files(
    base_dir: Path,
    station_dir: Path,
    station_meta: dict,
    year: int | None,
    month: int | None,
    include_covering_files: bool,
) -> list[DownloadedCsvFile]:
    files: list[DownloadedCsvFile] = []

    for csv_file in sorted(station_dir.glob("*.csv")):
        period = parse_csv_period(csv_file.stem)
        if period is None:
            continue

        coverage = period_covers_request(
            period=period,
            year=year,
            month=month,
            include_covering_files=include_covering_files,
        )

        if not coverage["matches"]:
            continue

        relative_path = str(csv_file.relative_to(base_dir))
        files.append(
            DownloadedCsvFile(
                filename=csv_file.name,
                path=csv_file.resolve(),
                relative_path=relative_path,
                uri=csv_file.resolve().as_uri(),
                station=station_meta["station"],
                station_code=station_meta.get("station_code"),
                station_type=station_meta.get("station_type"),
                station_category=station_meta.get("station_category"),
                size_kb=round(csv_file.stat().st_size / 1024, 1),
                period=period,
                covers_period=coverage["covers_period"],
                covers_requested_period=coverage["covers_requested_period"],
                can_extract_requested_month=coverage["can_extract_requested_month"],
            )
        )

    return files


def serialize_downloaded_files(files: list[DownloadedCsvFile]) -> list[dict]:
    """Convierte archivos descargados a dicts simples para tools y APIs."""
    return [file.model_dump() for file in files]
