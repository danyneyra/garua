import garua.settings as settings
import re
from typing import List, Optional
from bs4 import BeautifulSoup

# Constante para el parser HTML
HTML_PARSER = "html.parser"


def extract_station_info(html_content: str) -> Optional[dict]:
    """
    Extrae información relevante de una página HTML de estación.

    Args:
        html_content (str): El contenido HTML de la página de la estación

    Returns:
        dict: Un diccionario con la información extraída, o None si no se pudo extraer

    Estructura esperada:
        - Segundo <tr>: Nombre de la estación
        - Tercer <tr>: Departamento, Provincia, Distrito y select con fechas disponibles
        - Cuarto <tr>: Latitud, Longitud, Altitud
        - Quinto <tr>: Tipo y Código (frontend_code)
    """
    soup = BeautifulSoup(html_content, HTML_PARSER)

    station_info = {}

    # Buscar la tabla principal
    table = soup.find("table")
    if not table:
        return None

    rows = table.find_all("tr")

    # Extraer el nombre de la estación (segundo tr, índice 1)
    if len(rows) > 1:
        name_row = rows[1]
        font_element = name_row.find("font")
        if font_element:
            name_text = font_element.get_text(strip=True)
            # El texto viene como "Estación : NOMBRE", extraemos solo el nombre
            if ":" in name_text:
                station_info["name"] = name_text.split(":", 1)[1].strip()

    # Extraer Departamento, Provincia, Distrito y año inicial (tercer tr, índice 2)
    if len(rows) > 2:
        info_row = rows[2]
        tds = info_row.find_all("td")

        # Extraer los valores de las celdas que contienen los datos
        # Los tds están en pares: td[i] contiene la etiqueta, td[i+1] contiene el valor
        for i, td in enumerate(tds):
            text = td.get_text(strip=True)

            # Buscar Departamento
            if "Departamento" in text and i + 1 < len(tds):
                station_info["department"] = tds[i + 1].get_text(strip=True)
            # Buscar Provincia
            elif "Provincia" in text and i + 1 < len(tds):
                station_info["province"] = tds[i + 1].get_text(strip=True)
            # Buscar Distrito
            elif "Distrito" in text and i + 1 < len(tds):
                station_info["district"] = tds[i + 1].get_text(strip=True)

        # Extraer el año y mes inicial del select con fechas disponibles
        select_element = info_row.find("select", id="CBOFiltro")
        if select_element:
            options = select_element.find_all("option")
            if options:
                first_option = options[0]
                first_value = first_option.get("value", "")
                # El valor viene como "YYYYMM", lo convertimos a formato ISO "YYYY-MM"
                if first_value and len(first_value) >= 6:
                    try:
                        year = first_value[:4]
                        month = first_value[4:6]
                        station_info["data_available_since"] = f"{year}-{month}"
                    except (ValueError, IndexError):
                        pass

    # Extraer Latitud, Longitud y Altitud (cuarto tr, índice 3)
    if len(rows) > 3:
        coords_row = rows[3]
        tds = coords_row.find_all("td")

        for i, td in enumerate(tds):
            text = td.get_text(strip=True)

            # Buscar Latitud
            if "Altitud" in text and i + 1 < len(tds):
                altitude_text = tds[i + 1].get_text(strip=True)
                # Extraer solo el valor numérico (ej: "3829 msnm." -> 3829)
                altitude_match = re.match(r"(\d+)", altitude_text)
                if altitude_match:
                    try:
                        station_info["altitude"] = int(altitude_match.group(1))
                    except ValueError:
                        pass

    # Extraer Código/frontend_code (quinto tr, índice 4)
    if len(rows) > 4:
        code_row = rows[4]
        tds = code_row.find_all("td")

        for i, td in enumerate(tds):
            text = td.get_text(strip=True)

            # Buscar Código
            if "Codigo" in text and i + 1 < len(tds):
                station_info["frontend_code"] = tds[i + 1].get_text(strip=True)

    return station_info if station_info else None


def extract_select_options(
    html_content: str,
    select_id: Optional[str] = None,
    select_name: Optional[str] = None,
) -> List[dict]:
    """
    Extrae los valores y textos de las opciones de un select.

    Args:
        html_content (str): El contenido HTML que contiene el select
        select_id (str, optional): ID del select a buscar
        select_name (str, optional): Atributo name del select a buscar

    Returns:
        List[dict]: Lista de diccionarios con 'value' y 'text' de cada opción

    Raises:
        ValueError: Si no se encuentra ningún select con los criterios especificados
    """

    soup = BeautifulSoup(html_content, HTML_PARSER)

    # Buscar el select específico
    select_element = None

    if select_id:
        select_element = soup.find("select", id=select_id)
    elif select_name:
        select_element = soup.find("select", attrs={"name": select_name})
    else:
        # Si no se especifica ID ni name, tomar el primer select
        select_element = soup.find("select")

    if not select_element:
        if select_id:
            criteria = f"ID '{select_id}'"
        elif select_name:
            criteria = f"name '{select_name}'"
        else:
            criteria = "algún select"
        raise ValueError(f"No se encontró ningún select con {criteria}")

    # Extraer todas las opciones
    options = select_element.find_all("option")

    result = []

    for i, option in enumerate(options):
        option_data = {
            "value": option.get("value", ""),
            "text": option.get_text(strip=True),
            "selected": option.has_attr("selected"),
            "disabled": option.has_attr("disabled"),
        }

        result.append(option_data)

    return result


def _date_format(date_str: str) -> Optional[tuple]:
    """Verifica si una cadena es una fecha válida en formato YYYY-MM-DD o YYYY/MM/DD y  DD/MM/YYYY o DD-MM-YYYY y extraer año, mes, día"""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str) or re.match(
        r"^\d{4}/\d{2}/\d{2}$", date_str
    ):
        year, month, day = (
            date_str.split("-") if "-" in date_str else date_str.split("/")
        )
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return int(year), int(month), int(day)
    elif re.match(r"^\d{2}/\d{2}/\d{4}$", date_str) or re.match(
        r"^\d{2}-\d{2}-\d{4}$", date_str
    ):
        day, month, year = date_str.split("/" if "/" in date_str else "-")
        if 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
            return int(year), int(month), int(day)
    return None


def _clean_cell_text(text: str) -> str:
    """
    Limpia el texto de una celda, removiendo errores PHP del servidor SENAMHI.

    Args:
        text (str): Texto original de la celda

    Returns:
        str: Texto limpio sin errores PHP
    """
    # Detectar y remover errores PHP comunes del servidor SENAMHI
    # Patrón: Fatal error, Warning, Notice, etc.
    php_error_pattern = r"(Fatal error|Warning|Notice|Parse error):.*?(?:on line\d+|thrown in.*?line\d+)"
    text = re.sub(php_error_pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

    # Limpiar espacios múltiples resultantes
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _process_table_row(row, row_index, separator):
    cells = row.find_all(["td", "th"])
    row_data = []

    for cell_idx, cell in enumerate(cells):
        cell_text = cell.get_text(strip=True)

        # Si la celda contiene errores PHP del servidor, descartar toda la fila
        if (
            "Fatal error" in cell_text
            or "Warning" in cell_text
            or "thrown in" in cell_text
        ):
            print(
                f"⚠️  Advertencia: Fila {row_index + 1} contiene error PHP del servidor, se descarta."
            )
            return None

        cell_text = re.sub(r"\s+", " ", cell_text)
        if separator in cell_text:
            cell_text = f'"{cell_text}"'

        if row_index > 0 and cell_idx == 0:
            date_format = _date_format(cell_text)
            if date_format is None:
                print(
                    f"⚠️  Advertencia: La primera celda de la fila {row_index + 1} no es una fecha válida: '{cell_text}'"
                )
                return None
            year, month, day = date_format
            row_data.extend([f"{year:04d}", f"{month:02d}", f"{day:02d}"])
        else:
            # Normalizar valores especiales: S/D (sin datos) y T (trazas)
            if cell_text.strip() == "S/D" or cell_text.strip() == "":
                cell_text = "S/D"  # Mantener "S/D" para indicar sin datos
            elif cell_text.strip() == "T":
                cell_text = "T"  # Mantener "T" para precipitaciones traza
            row_data.append(cell_text)
    return row_data if row_data and any(cell.strip() for cell in row_data) else None


def html_table_to_csv(
    html_content: str,
    separator: str = settings.CSV_SEPARATOR,
    start_line: Optional[int] = 0,
) -> str:
    """
    Convierte una tabla HTML a formato CSV usando BeautifulSoup y retorna directamente el contenido CSV como string.

    Args:
        html_content (str): El contenido HTML que contiene la tabla
        separator (str): Separador a usar (por defecto ';')
        start_line (int, optional): Línea desde la cual empezar a procesar

    Returns:
        str: Contenido CSV como string
    """
    soup = BeautifulSoup(html_content, HTML_PARSER)
    table = soup.find("table")
    if not table:
        return ""

    csv_lines = []
    seen_rows = set()  # Para detectar filas completamente duplicadas
    rows = table.find_all("tr")

    for row_index, row in enumerate(rows):
        if start_line and row_index < start_line:
            continue
        row_data = _process_table_row(row, row_index, separator)
        if row_data:
            row_content = separator.join(row_data)

            # Para filas de datos (no headers), verificar duplicados exactos
            if row_index > 0:
                if row_content in seen_rows:
                    print(
                        f"⚠️  Advertencia: Fila duplicada detectada en línea {row_index + 1}, se omite."
                    )
                    continue
                seen_rows.add(row_content)

            csv_lines.append(row_content)

    return "\n".join(csv_lines)
