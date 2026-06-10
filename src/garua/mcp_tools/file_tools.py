"""Tools para gestión de archivos CSV descargados."""

from pathlib import Path
from typing import Annotated

from pydantic import Field

import garua.settings as settings
from garua.utils.helpers import parse_csv_period
from garua.schemas.mcp import build_mcp_error_response, build_mcp_success_response
from garua.schemas.file_tools import (
    build_csv_preview_success_response,
    build_extracted_data_success_response,
)
from garua.services.downloaded_files import (
    list_downloaded_csv_files,
    serialize_downloaded_files,
)
from garua.services.file_preview import (
    MAX_CSV_PREVIEW_COLUMNS,
    MAX_CSV_PREVIEW_ROWS,
    build_csv_preview,
    resolve_preview_csv_path,
)


def register_file_tools(mcp):
    """Registra las tools de gestión de archivos en el servidor MCP."""

    def _error_response(
        message: str,
        error_code: str,
        station_name: str,
        station_code: str,
        error_details: str | None = None,
        mcp_response: bool = True,
    ) -> dict:
        if not mcp_response:
            raise ValueError(
                f"Error: {message} (Código: {error_code}, Estación: {station_name} [{station_code}]) Detalles: {error_details}"
            )

        return build_mcp_error_response(
            error_message=message,
            error_code=error_code,
            station_name=station_name,
            station_code=station_code,
            error_details=error_details,
        )

    def _resolve_extract_source_path(
        csv_dir: Path,
        source_file: str | None,
        station_name: str | None,
        station_code: str | None,
        station_type: str | None,
        station_category: str | None,
        year: int,
        month: int,
    ) -> Path:
        if source_file:
            raw_path = Path(source_file)

            if raw_path.is_absolute():
                source_path = raw_path.resolve()
                try:
                    source_path.relative_to(csv_dir.resolve())
                except ValueError:
                    raise ValueError(
                        "source_file está fuera de la carpeta CSV configurada."
                    )
                return source_path

            source_path = (csv_dir / source_file).resolve()
            try:
                source_path.relative_to(csv_dir.resolve())
            except ValueError:
                raise ValueError(
                    "source_file está fuera de la carpeta CSV configurada."
                )
            return source_path

        matches = list_downloaded_files(
            station_name=station_name,
            station_code=station_code,
            station_type=station_type,
            station_category=station_category,
            year=year,
            month=month,
            include_covering_files=True,
            mcp_response=False,
        )

        candidates = [
            item
            for item in matches
            if item.get("can_extract_requested_month") is True
            and (item.get("period") or {}).get("kind") in {"year", "period"}
        ]

        if not candidates:
            raise ValueError(
                "No se encontró archivo consolidado que cubra el mes solicitado. "
                "Usa list_downloaded_files para revisar archivos disponibles."
            )

        candidates = sorted(
            candidates,
            key=lambda item: (
                0 if (item.get("period") or {}).get("kind") == "year" else 1
            ),
        )

        if len(candidates) > 1:
            options = [
                item.get("relative_path") or item.get("path") or item.get("filename")
                for item in candidates[:10]
            ]
            raise ValueError(
                "Se encontraron múltiples archivos consolidados compatibles. "
                f"Especifica source_file. Opciones: {options}"
            )

        selected = candidates[0].get("path") or candidates[0].get("relative_path")
        if not selected:
            raise ValueError("El archivo encontrado no incluye path.")

        selected_path = Path(selected)
        if selected_path.is_absolute():
            return selected_path

        return (csv_dir / selected).resolve()

    @mcp.tool()
    def list_downloaded_files(
        station_name: Annotated[
            str | None,
            Field(
                description="Nombre de la estación para filtrar (ej: 'Cabana', 'Cachicadan'). Si se omite, lista todas."
            ),
        ] = None,
        station_code: Annotated[
            str | None,
            Field(
                description=(
                    "Código interno de la estación SENAMHI (ej: '107008', '100090') para filtrar. "
                    "Obténlo primero con search_stations. Requiere station_name si se especifica."
                )
            ),
        ] = None,
        station_type: Annotated[
            str | None,
            Field(
                description=(
                    "Tipo de estación para filtrar (M para meteorológica, H para hidrológica). "
                    "Requiere station_name si se especifica."
                )
            ),
        ] = None,
        station_category: Annotated[
            str | None,
            Field(
                description=(
                    "Categoría de estación para filtrar (ej: EMA, CO). "
                    "Requiere station_name si se especifica."
                )
            ),
        ] = None,
        year: Annotated[
            int | None,
            Field(
                description="Año para filtrar archivos que contengan datos de ese año (ej: 2025)."
            ),
        ] = None,
        month: Annotated[
            int | None,
            Field(
                description="Mes para filtrar archivos individuales (1-12). Requiere year si se especifica."
            ),
        ] = None,
        csv_dir: Annotated[
            str | None,
            Field(
                description=(
                    "Ruta del directorio CSV para listar archivos (opcional). Por defecto busca en la carpeta de salida configurada."
                )
            ),
        ] = None,
        include_covering_files: Annotated[
            bool,
            Field(
                description=(
                    "Si es True, incluye archivos consolidados que cubren rangos de años, incluso si no son específicos del año/mes filtrado. Por defecto False."
                )
            ),
        ] = True,
        mcp_response: Annotated[
            bool,
            Field(
                description="Si True, devuelve una respuesta MCP completa. Por defecto False."
            ),
        ] = True,
    ) -> dict | list[dict]:
        """
        Lista archivos CSV ya descargados en la carpeta CSV configurada.

        Usa esta tool cuando el usuario pregunte qué datos existen localmente
        o cuando necesites verificar si un periodo ya está descargado.

        Soporta carpetas nuevas:
        - Cajabamba_107008_M_CO/

        Y carpetas legacy:
        - Cajabamba_M_CO/
        - Cajabamba/

        Si se solicita year + month, también puede devolver archivos consolidados
        que cubren ese mes, por ejemplo:
        - Cajabamba-2025.csv
        - Cajabamba-2022-2025.csv
        """

        if month is not None and year is None:
            return _error_response(
                "month requiere year para filtrar correctamente.",
                error_code="MONTH_WITHOUT_YEAR",
                station_name=station_name or "",
                station_code=station_code or "",
            )

        if month is not None and not 1 <= month <= 12:
            return _error_response(
                "month debe estar entre 1 y 12.",
                error_code="INVALID_MONTH",
                station_name=station_name or "",
                station_code=station_code or "",
            )

        if (station_type or station_category) and not (station_name or station_code):
            return _error_response(
                "station_type/station_category requieren station_name o station_code.",
                error_code="MISSING_STATION_INFO",
                station_name=station_name or "",
                station_code=station_code or "",
            )

        files = serialize_downloaded_files(
            list_downloaded_csv_files(
                csv_dir=csv_dir,
                station_name=station_name,
                station_code=station_code,
                station_type=station_type,
                station_category=station_category,
                year=year,
                month=month,
                include_covering_files=include_covering_files,
            )
        )

        if mcp_response:
            message = f"Se encontraron {len(files)} archivos descargados que coinciden con los filtros."
            structured_data: dict = {
                "total_files": len(files),
                "files": files,
            }
            return build_mcp_success_response(
                message=message, structured_data=structured_data
            )

        return files

    @mcp.tool()
    def read_csv_preview(
        file_path: Annotated[
            str | None,
            Field(
                description=(
                    "Ruta completa o relativa del CSV dentro de la carpeta CSV de Garua. "
                    "Recomendado usar el campo path devuelto por list_downloaded_files."
                )
            ),
        ] = None,
        relative_path: Annotated[
            str | None,
            Field(
                description=(
                    "Ruta relativa legacy del CSV dentro de la carpeta CSV de Garua "
                    "(ej: 'Cajabamba_107008_M_CO/Cajabamba-2025.csv'). "
                    "Se mantiene por compatibilidad; prefiere file_path."
                )
            ),
        ] = None,
        station_name: Annotated[
            str | None,
            Field(
                description="Nombre de la estación para búsqueda automática del CSV."
            ),
        ] = None,
        station_code: Annotated[
            str | None,
            Field(
                description="Código de estación para búsqueda precisa del CSV. Recomendado si hay estaciones con el mismo nombre."
            ),
        ] = None,
        station_type: Annotated[
            str | None,
            Field(
                description="Tipo de estación: M para meteorológica, H para hidrológica."
            ),
        ] = None,
        station_category: Annotated[
            str | None,
            Field(description="Categoría de estación, por ejemplo CO, EMA, HLM, EHA."),
        ] = None,
        year: Annotated[
            int | None,
            Field(description="Año a mostrar/filtrar dentro del CSV."),
        ] = None,
        month: Annotated[
            int | None,
            Field(description="Mes a filtrar dentro del CSV (1-12). Requiere year."),
        ] = None,
        max_rows: Annotated[
            int,
            Field(
                description=(
                    "Número máximo de filas a mostrar. Por defecto 20. "
                    f"Tope de seguridad: {MAX_CSV_PREVIEW_ROWS}."
                )
            ),
        ] = 20,
        max_columns: Annotated[
            int,
            Field(
                description=(
                    "Número máximo de columnas a mostrar. Por defecto 20. "
                    f"Tope de seguridad: {MAX_CSV_PREVIEW_COLUMNS}."
                )
            ),
        ] = 20,
    ) -> dict:
        """
        Muestra una vista previa de un CSV descargado.

        Usa esta tool cuando el usuario pida ver el contenido, datos o vista previa
        de un archivo CSV ya descargado.

        Formas de uso:
        1. Ruta directa recomendada:
        read_csv_preview(file_path='C:/Users/.../Garua/csv/Cajabamba_107008_M_CO/Cajabamba-2025.csv')

        2. Ruta relativa legacy:
        read_csv_preview(relative_path='Cajabamba_107008_M_CO/Cajabamba-2025.csv')

        3. Búsqueda inteligente:
        read_csv_preview(station_code='107008', year=2025, month=12)

        4. Búsqueda por estación:
        read_csv_preview(
            station_name='Cajabamba',
            station_type='M',
            station_category='CO',
            year=2025,
            month=12
        )

        Si el archivo encontrado es consolidado, filtra internamente el periodo pedido.

        No uses esta tool para descargar datos. Para descargar usa scrape_station_data.
        No la uses automáticamente tras scrape_station_data, porque esa tool ya devuelve rutas.
        """
        if month is not None and year is None:
            return build_mcp_error_response(
                "El parámetro month requiere year.",
                error_code="MONTH_WITHOUT_YEAR",
                station_name=station_name,
                station_code=station_code,
            )

        if month is not None and not 1 <= month <= 12:
            return build_mcp_error_response(
                "month debe estar entre 1 y 12.",
                error_code="INVALID_MONTH",
                station_name=station_name,
                station_code=station_code,
            )

        if max_rows < 1:
            return build_mcp_error_response(
                "max_rows debe ser mayor o igual a 1.",
                error_code="INVALID_MAX_ROWS",
                station_name=station_name,
                station_code=station_code,
            )

        if max_columns < 1:
            return build_mcp_error_response(
                "max_columns debe ser mayor o igual a 1.",
                error_code="INVALID_MAX_COLUMNS",
                station_name=station_name,
                station_code=station_code,
            )

        csv_dir = settings.CSV_DIR

        try:
            path = resolve_preview_csv_path(
                csv_dir=csv_dir,
                file_path=file_path,
                relative_path=relative_path,
                station_name=station_name,
                station_code=station_code,
                station_type=station_type,
                station_category=station_category,
                year=year,
                month=month,
            )
            preview = build_csv_preview(
                path=path,
                year=year,
                month=month,
                max_rows=max_rows,
                max_columns=max_columns,
            )

            return build_csv_preview_success_response(
                message=preview.message,
                columns=preview.columns,
                rows=preview.rows,
                total_rows=preview.total_rows,
                total_columns=preview.total_columns,
                truncated=preview.truncated,
                truncated_reason=preview.truncated_reason,
                source_file=str(preview.source_file),
            )

        except FileNotFoundError as e:
            return build_mcp_error_response(
                str(e),
                error_code="FILE_NOT_FOUND",
                station_name=station_name,
                station_code=station_code,
            )
        except ValueError as e:
            return build_mcp_error_response(
                str(e),
                error_code="VALUE_ERROR",
                station_name=station_name,
                station_code=station_code,
            )
        except Exception as e:
            return build_mcp_error_response(
                f"Error al leer el archivo: {e}",
                error_code="CSV_READ_ERROR",
                station_name=station_name,
                station_code=station_code,
            )

    @mcp.tool()
    async def extract_month_from_csv(
        year: Annotated[
            int,
            Field(description="Año a extraer."),
        ],
        month: Annotated[
            int,
            Field(description="Mes a extraer (1-12)."),
        ],
        station_name: Annotated[
            str | None,
            Field(description="Nombre de la estación, por ejemplo 'Cajabamba'."),
        ] = None,
        station_code: Annotated[
            str | None,
            Field(
                description="Código de estación. Recomendado para evitar ambigüedad."
            ),
        ] = None,
        station_type: Annotated[
            str | None,
            Field(
                description="Tipo de estación: M para meteorológica, H para hidrológica."
            ),
        ] = None,
        station_category: Annotated[
            str | None,
            Field(description="Categoría de estación, por ejemplo CO, EMA, HLM, EHA."),
        ] = None,
        source_file: Annotated[
            str | None,
            Field(
                description=(
                    "Archivo origen opcional. Puede ser filename dentro de la carpeta de estación "
                    "o relative_path devuelto por list_downloaded_files."
                )
            ),
        ] = None,
        overwrite: Annotated[
            bool,
            Field(description="Si True, sobrescribe el CSV mensual si ya existe."),
        ] = False,
    ) -> dict:
        """
        Extrae un mes específico desde un CSV consolidado y lo guarda como archivo mensual.

        Usa esta tool cuando ya existe un archivo anual o multianual y el usuario quiere
        generar un CSV mensual independiente.

        Formas de uso:
        1. Con source_file:
        extract_month_from_csv(
            source_file='Cajabamba_107008_M_CO/Cajabamba-2025.csv',
            year=2025,
            month=5
        )

        2. Búsqueda automática:
        extract_month_from_csv(
            station_code='107008',
            year=2025,
            month=5
        )

        No uses esta tool para descargar desde SENAMHI. Para descargar usa scrape_station_data.
        """
        csv_dir = settings.CSV_DIR

        if month < 1 or month > 12:
            return build_mcp_error_response(
                "month debe estar entre 1 y 12.",
                error_code="INVALID_MONTH",
                station_name=station_name,
                station_code=station_code,
                error_details=f"Año: {year}, Mes: {month}",
            )

        if not csv_dir.exists():
            return build_mcp_error_response(
                "No existe la carpeta CSV configurada.",
                error_code="CSV_DIR_NOT_FOUND",
                station_name=station_name,
                station_code=station_code,
            )

        try:
            source_path = _resolve_extract_source_path(
                csv_dir=csv_dir,
                source_file=source_file,
                station_name=station_name,
                station_code=station_code,
                station_type=station_type,
                station_category=station_category,
                year=year,
                month=month,
            )
        except ValueError as e:
            return build_mcp_error_response(
                str(e),
                error_code="VALUE_ERROR",
                station_name=station_name,
                station_code=station_code,
            )

        if not source_path.exists():
            return build_mcp_error_response(
                f"Archivo no encontrado: {source_path}",
                error_code="FILE_NOT_FOUND",
                station_name=station_name,
                station_code=station_code,
            )

        period = parse_csv_period(source_path.stem)
        if not period:
            return build_mcp_error_response(
                f"No se pudo detectar el periodo del archivo: {source_path.name}",
                error_code="PERIOD_NOT_DETECTED",
                station_name=station_name,
                station_code=station_code,
            )

        if period["kind"] == "month":
            return build_mcp_error_response(
                "El archivo origen ya es mensual. No hay nada que extraer.",
                error_code="ALREADY_MONTHLY",
                station_name=station_name,
                station_code=station_code,
            )

        if period["kind"] == "year" and period["year"] != year:
            return build_mcp_error_response(
                f"El archivo {source_path.name} no cubre el año {year}.",
                error_code="YEAR_NOT_COVERED",
                station_name=station_name,
                station_code=station_code,
            )

        if period["kind"] == "period" and not (
            period["start_year"] <= year <= period["end_year"]
        ):
            return build_mcp_error_response(
                f"El archivo {source_path.name} no cubre el año {year}.",
                error_code="YEAR_NOT_COVERED",
                station_name=station_name,
                station_code=station_code,
            )

        with open(source_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if not lines:
            return build_mcp_error_response(
                "El archivo de origen está vacío.",
                error_code="EMPTY_FILE",
                station_name=station_name,
                station_code=station_code,
            )

        header = lines[0].strip()
        extracted_rows = []

        for line in lines[1:]:
            parts = line.strip().split(";")
            if len(parts) < 3:
                continue

            try:
                row_year = int(parts[0])
                row_month = int(parts[1])
            except ValueError:
                continue

            if row_year == year and row_month == month:
                extracted_rows.append(line.strip())

        if not extracted_rows:
            return build_mcp_error_response(
                f"No se encontraron datos para {month:02d}/{year} en {source_path.name}.",
                error_code="NO_DATA_FOUND",
                station_name=station_name,
                station_code=station_code,
                error_details=f"Año: {year}, Mes: {month}, Archivo origen: {source_path.name}",
            )

        station_folder = source_path.parent
        station_part = period.get("station_part") or source_path.stem.split("-")[0]
        output_filename = f"{station_part}-{year:04d}{month:02d}.csv"
        output_path = station_folder / output_filename

        if output_path.exists() and not overwrite:
            return build_mcp_error_response(
                f"El archivo mensual ya existe: {output_filename}. Usa overwrite=True para sobrescribirlo.",
                error_code="FILE_ALREADY_EXISTS",
                station_name=station_name,
                station_code=station_code,
                error_details=f"Archivo destino: {output_filename}",
            )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(header + "\n")
            for row in extracted_rows:
                f.write(row + "\n")

        return build_extracted_data_success_response(
            message=f"Archivo mensual extraído exitosamente: {output_filename}",
            station_name=station_name or "",
            station_code=station_code or "",
            mode="extract_month",
            period=f"{year:04d}-{month:02d}",
            rows_extracted=len(extracted_rows),
            source_files=[str(source_path.resolve())],
            output_files=[str(output_path.resolve())],
            overwrite=overwrite,
        )
