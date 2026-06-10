"""Servicio de descarga y extracción de datos SENAMHI."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import garua.settings as settings
from garua.models.scraping import (
    ScrapingServiceErrorResponse,
    ScrapingServiceSuccessResponse,
    Stats,
)
from garua.models.station import Station
from garua.models.scraping import ScrapingPeriod, ScrapingQueryParams
from garua.services.station import find_station_by_code
from garua.settings import YEAR_MAX, YEAR_MIN
from garua.utils.helpers import (
    build_station_folder_name,
    normalize_station_slug,
    parse_csv_period,
)


def _error_response(
    message: str,
    error_code: str,
    station_code: str | None = None,
    station_name: str | None = None,
    details: str | None = None,
) -> ScrapingServiceErrorResponse:
    return ScrapingServiceErrorResponse(
        message=message,
        station_code=station_code,
        station_name=station_name,
        error_code=error_code,
        details=details,
    )


def _success_response(
    message: str,
    station_name: str,
    station_code: str,
    mode: str,
    period: str,
    stats: dict,
    files: list[str] | None = None,
    extracted_from: str | None = None,
) -> ScrapingServiceSuccessResponse:
    return ScrapingServiceSuccessResponse(
        message=message,
        station_name=station_name,
        station_code=station_code,
        mode=mode,
        period=period,
        stats=Stats(**stats),
        files=files or [],
        extracted_from=extracted_from,
    )


def _try_extract_from_existing(
    station: Station, year: int, month: int
) -> ScrapingServiceSuccessResponse | None:
    """
    Intenta extraer un mes específico de archivos consolidados existentes.
    Retorna resultado si encuentra datos, None si no hay archivo o no tiene datos.
    """

    csv_dir = Path(settings.CSV_DIR).resolve()
    station_name_slug = normalize_station_slug(station.name)
    station_folder_name = build_station_folder_name(station)
    station_dir = csv_dir / station_folder_name

    if not station_dir.exists():
        return None

    candidates = []
    for f in station_dir.glob("*.csv"):
        period = parse_csv_period(f.stem)
        if not period:
            continue

        if period["kind"] == "year" and period["year"] == year:
            candidates.append(f)

        if period["kind"] == "period" and (
            period["start_year"] <= year <= period["end_year"]
        ):
            candidates.append(f)

    if not candidates:
        return None

    candidates = sorted(
        candidates,
        key=lambda path: (
            0 if (parse_csv_period(path.stem) or {}).get("kind") == "year" else 1
        ),
    )
    source_path = candidates[0]

    try:
        with open(source_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return None

        header = lines[0].strip()
        extracted_rows = []

        for line in lines[1:]:
            parts = line.strip().split(";")
            if len(parts) < 3:
                continue

            try:
                row_year = int(parts[0])
                row_month = int(parts[1])

                if row_year == year and row_month == month:
                    extracted_rows.append(line.strip())
            except (ValueError, IndexError):
                continue

        if not extracted_rows:
            return None

        output_filename = f"{station_name_slug}-{year:04d}{month:02d}.csv"
        output_path = station_dir / output_filename

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n")
            for i, row in enumerate(extracted_rows):
                if i == len(extracted_rows) - 1:
                    f.write(row)
                else:
                    f.write(row + "\n")

        file_uri_output = output_path.resolve().as_uri()

        message = f"Para el periodo {month:02d}/{year}, encontré un archivo consolidado existente ({source_path.name}) y extraje los datos correspondientes. Guardé el archivo extraído como [{output_filename}]({file_uri_output})."

        return _success_response(
            message=message,
            station_name=station.name,
            station_code=station.code,
            mode="month",
            period=f"{month:02d}/{year}",
            files=[str(output_path)],
            stats={
                "successful": 1,
                "total": 1,
                "failed": 0,
            },
            extracted_from=source_path.name,
        )

    except Exception:
        return None


def _format_success_message(
    station_name: str,
    station_code: str,
    mode: str,
    period: str,
    successful: int,
    total: int,
) -> str:
    """Genera un mensaje formateado."""
    mode_messages = {
        "month": f"Listo, descargué los datos de {station_name} ({station_code}) para {period}.",
        "year": f"Terminé de descargar todos los datos de {station_name} ({station_code}) para el año {period}.",
        "period": f"Completé la descarga de {station_name} ({station_code}) para el periodo {period}.",
    }

    main_message = mode_messages.get(
        mode, f"Descarga completada para {station_name} ({station_code})."
    )

    if successful < total:
        main_message += f"Se descargaron {successful} de {total} opciones disponibles. Revisa los detalles para más información."

    return main_message


def _validate_periods(
    periods: list[ScrapingPeriod],
) -> list[ScrapingPeriod] | ScrapingServiceErrorResponse:
    if not periods or len(periods) == 0:
        return _error_response(
            error_code="invalid_periods_parameter",
            message="El parámetro 'periods' debe ser una lista no vacía",
            details="Se esperaba una lista con al menos un periodo.",
        )

    if len(periods) > 12:
        return _error_response(
            error_code="too_many_periods",
            message=f"Máximo 12 periodos por llamada. Recibido: {len(periods)}. Para más periodos, usa mode='year' o mode='period'.",
            details="Se excedió el número máximo de periodos permitidos.",
        )

    for i, period in enumerate(periods):
        p_year = period.year
        p_month = period.month

        if not (YEAR_MIN <= p_year <= YEAR_MAX):
            return _error_response(
                error_code="invalid_year",
                message=f"Año inválido en periodo {i + 1}: {p_year}. Debe estar entre {YEAR_MIN} y {YEAR_MAX}.",
                details="El año proporcionado no está dentro del rango permitido.",
            )

        if not (1 <= p_month <= 12):
            return _error_response(
                error_code="invalid_month",
                message=f"Mes inválido en periodo {i + 1}: {p_month}. Debe estar entre 1 y 12.",
                details="El mes proporcionado no está dentro del rango permitido.",
            )

    return periods


async def _run_scraper(station: Station, query_params: ScrapingQueryParams) -> dict:
    from garua.scraping.scraper import scraping_main

    stdout_capture = StringIO()
    with redirect_stdout(stdout_capture):
        result = await scraping_main(station, query_params)
    return result


async def _scrape_multiple_periods(
    station: Station,
    periods: list[ScrapingPeriod],
    force_download: bool,
) -> ScrapingServiceSuccessResponse | ScrapingServiceErrorResponse:
    validated_periods = _validate_periods(periods)
    if isinstance(validated_periods, ScrapingServiceErrorResponse):
        return validated_periods

    extracted_results = []
    pending_downloads = []
    message_parts = []

    if not force_download:
        for period in validated_periods:
            extraction = _try_extract_from_existing(station, period.year, period.month)
            if extraction:
                extracted_results.append(extraction)
                message_parts.append(extraction.message)
            else:
                pending_downloads.append(period)

        if not pending_downloads:
            all_files = []
            for result in extracted_results:
                all_files.extend(result.files)

            periods_str = ", ".join(
                f"{period.month:02d}/{period.year}" for period in validated_periods
            )

            return _success_response(
                message=(
                    f"Listo, encontré los datos de {station.name} para {periods_str} en archivos existentes.\n\n"
                    f"{' '.join(message_parts)}"
                ),
                station_name=station.name,
                station_code=station.code,
                mode="periods",
                period=periods_str,
                stats={
                    "successful": len(all_files),
                    "total": len(validated_periods),
                    "failed": 0,
                },
                files=all_files,
                extracted_from="local_files",
            )
    else:
        pending_downloads = validated_periods

    min_year = min(period.year for period in pending_downloads)
    max_year = max(period.year for period in pending_downloads)

    query_params = ScrapingQueryParams(
        mode="period",
        start_year=min_year,
        end_year=max_year,
        individual=True,
        mcp_filter_periods=pending_downloads,
    )

    try:
        result = await _run_scraper(station, query_params)

        if not result or not result.get("success"):
            error_msg = (
                result.get("error", "Descarga fallida")
                if result
                else "Descarga fallida"
            )
            return _error_response(
                error_code="download_failed",
                message=error_msg,
                details="El scraper no pudo descargar los periodos pendientes.",
            )

        downloaded_files = result.get("saved_files", [])

        all_files = []
        for extraction_result in extracted_results:
            all_files.extend(extraction_result.files)
        all_files.extend(downloaded_files)

        periods_str = ", ".join(
            f"{period.month:02d}/{period.year}" for period in validated_periods
        )

        message_parts = message_parts or []
        if extracted_results:
            message_parts.append(
                f"{len(extracted_results)} periodo(s) extraído(s) de archivos existentes"
            )
        if downloaded_files:
            message_parts.append(
                f"{len(downloaded_files)} periodo(s) descargado(s) del SENAMHI"
            )

        message = (
            f"Listo, procesé {len(validated_periods)} periodo(s) de {station.name}\n\n"
            + "\n".join(message_parts)
        )

        extraction_type = (
            "mixed"
            if extracted_results and downloaded_files
            else "local_files"
            if extracted_results
            else "downloaded_files"
        )

        return _success_response(
            message=message,
            station_name=station.name,
            station_code=station.code,
            mode="period",
            period=periods_str,
            stats={
                "successful": len(all_files),
                "total": len(validated_periods),
                "failed": len(validated_periods) - len(all_files),
            },
            files=all_files,
            extracted_from=extraction_type,
        )
    except Exception as e:
        error_msg = f"Error durante la descarga de periodos: {str(e)}"
        return _error_response(
            error_code="download_failed",
            message=error_msg,
            details="Ocurrió un error inesperado durante la descarga de periodos.",
        )


async def scrape_station_data_service(
    station_code: str,
    mode: str | None = None,
    year: int | None = None,
    month: int | None = None,
    start_year: int | None = None,
    end_year: int | None = None,
    individual: bool = False,
    periods: list[ScrapingPeriod] | None = None,
    force_download: bool = False,
) -> ScrapingServiceSuccessResponse | ScrapingServiceErrorResponse:
    """Descarga datos históricos SENAMHI o extrae periodos existentes."""
    station = find_station_by_code(station_code)
    if not station:
        error_msg = f"Estación '{station_code}' no encontrada. Usa search_stations para obtener el código correcto."
        return _error_response(
            error_code="station_not_found",
            message=error_msg,
            station_code=station_code,
            details=f"No existe una estación con código '{station_code}' en la base de datos.",
        )

    if periods:
        return await _scrape_multiple_periods(
            station=station,
            periods=periods,
            force_download=force_download,
        )

    if not mode:
        return _error_response(
            error_code="missing_mode",
            message="El parámetro 'mode' es requerido cuando no se usa 'periods'.",
            station_code=station_code,
            station_name=station.name,
            details="Especifica 'mode' como 'month', 'year' o 'period' para indicar el tipo de descarga.",
        )

    if not force_download and mode == "month" and year and month:
        extraction_result = _try_extract_from_existing(station, year, month)
        if extraction_result:
            return extraction_result

    query_params = ScrapingQueryParams(
        mode=mode,
        year=year,
        month=month,
        start_year=start_year,
        end_year=end_year,
        individual=individual,
    )

    try:
        result = await _run_scraper(station, query_params)

        if not result or not result.get("success"):
            error_msg = (
                result.get("error", "Descarga fallida")
                if result
                else "Descarga fallida"
            )
            return _error_response(
                error_code="download_failed",
                message=error_msg,
                station_code=station_code,
                station_name=station.name,
                details="Ocurrió un error inesperado durante la descarga.",
            )

        station_name = result["station_name"]
        mode_value = result["mode"]
        saved_files = result.get("saved_files", [])
        successful_count = result.get("successful_count", 0)
        total_options = result.get("total_options", 0)

        period = ""
        if mode_value == "month" and year and month:
            period = f"{month:02d}/{year}"
        elif mode_value == "year" and year:
            period = str(year)
        elif mode_value == "period" and start_year and end_year:
            period = f"{start_year}-{end_year}"

        message = _format_success_message(
            station_name,
            station.code,
            mode_value,
            period,
            successful_count,
            total_options,
        )

        return _success_response(
            message=message,
            station_name=station_name,
            station_code=station_code,
            mode=mode_value,
            period=period,
            files=saved_files,
            stats={
                "successful": successful_count,
                "total": total_options,
                "failed": total_options - successful_count,
            },
        )

    except Exception as e:
        error_msg = f"Error durante la descarga: {str(e)}"
        return _error_response(
            error_code="download_failed",
            message=error_msg,
            station_code=station_code,
            station_name=station.name,
            details="Ocurrió un error inesperado durante la descarga.",
        )
