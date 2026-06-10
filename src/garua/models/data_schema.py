"""
Esquemas de datos CSV para diferentes tipos de estaciones.
Separado del modelo Station para mantener la separación de responsabilidades.
"""

from typing import List
from .station import StationType, StationStatus


# Headers para estaciones meteorológicas convencionales
METEOROLOGICAL_CONVENTIONAL_HEADERS = [
    "Año",
    "Mes", 
    "Día",
    "Temp. Máx (°C)",
    "Temp. Mín (°C)",
    "Humedad (%)",
    "Precipitación (mm)",
]

# Headers para estaciones meteorológicas automáticas
METEOROLOGICAL_AUTOMATIC_HEADERS = [
    "Año",
    "Mes",
    "Día", 
    "Hora",
    "Temperatura (°C)",
    "Precipitación (mm)",
    "Humedad (%)",
    "Dir. Viento (°)",
    "Vel. Viento (m/s)",
]

# Headers para estaciones hidrológicas convencionales
HYDROLOGICAL_CONVENTIONAL_HEADERS = [
    "Año",
    "Mes",
    "Día",
    "Nivel del río (m) 06",
    "Nivel del río (m) 10", 
    "Nivel del río (m) 14",
    "Nivel del río (m) 18",
]

# Headers para estaciones hidrológicas automáticas
HYDROLOGICAL_AUTOMATIC_HEADERS = [
    "Año",
    "Mes",
    "Día",
    "Hora",
    "Nivel del río (m)",
    "Precipitación (mm/hora)",
]


def get_headers_for_station_type(station_type: StationType, status: StationStatus) -> List[str]:
    """
    Retorna los headers CSV apropiados según el tipo y estado de la estación.
    
    Args:
        station_type: Tipo de estación (M o H)
        status: Estado de la estación (REAL, DIFERIDO, AUTOMATICA)
    
    Returns:
        Lista de headers apropiados para el CSV
    
    Raises:
        ValueError: Si la combinación de tipo y estado no es válida
    """
    
    if station_type == StationType.METEOROLOGICAL:
        if status == StationStatus.AUTOMATIC:
            return METEOROLOGICAL_AUTOMATIC_HEADERS.copy()
        else:
            return METEOROLOGICAL_CONVENTIONAL_HEADERS.copy()
            
    elif station_type == StationType.HYDROLOGICAL:
        if status == StationStatus.AUTOMATIC:
            return HYDROLOGICAL_AUTOMATIC_HEADERS.copy()
        else:
            return HYDROLOGICAL_CONVENTIONAL_HEADERS.copy()
            
    else:
        raise ValueError(f"Tipo de estación desconocido: {station_type}")


def get_expected_columns_count(station_type: StationType, status: StationStatus) -> int:
    """
    Retorna el número esperado de columnas para validación.
    
    Args:
        station_type: Tipo de estación
        status: Estado de la estación
        
    Returns:
        Número de columnas esperadas
    """
    headers = get_headers_for_station_type(station_type, status)
    return len(headers)


def validate_csv_row(row: List[str], station_type: StationType, status: StationStatus) -> bool:
    """
    Valida que una fila CSV tenga el número correcto de columnas.
    
    Args:
        row: Fila de datos CSV
        station_type: Tipo de estación
        status: Estado de la estación
        
    Returns:
        True si la fila es válida, False en caso contrario
    """
    expected_count = get_expected_columns_count(station_type, status)
    return len(row) == expected_count