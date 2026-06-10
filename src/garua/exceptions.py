"""
Excepciones específicas para el scraping de SENAMHI
"""

class ScrapingError(Exception):
    """Excepción base para errores de scraping"""
    pass

class IframeNotFoundError(ScrapingError):
    """Error cuando no se encuentra el iframe contenedor"""
    pass

class TableNotFoundError(ScrapingError):
    """Error cuando no se encuentra la tabla de datos"""
    pass

class SelectNotFoundError(ScrapingError):
    """Error cuando no se encuentra el elemento select"""
    pass

class OptionProcessingError(ScrapingError):
    """Error al procesar una opción específica"""
    pass