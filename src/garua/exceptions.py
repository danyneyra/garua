"""Excepciones de dominio para Garúa."""


class GaruaError(Exception):
    """Excepción base para errores controlados de Garúa."""


class ScrapingError(GaruaError):
    """Error base durante la navegación, captura o procesamiento de datos SENAMHI."""


class BrowserNotFoundError(ScrapingError):
    """No se encontró un navegador Chromium compatible para ejecutar zendriver."""


class ScrapingPageError(ScrapingError):
    """Error al preparar o navegar la página de SENAMHI."""


class SelectNotFoundError(ScrapingPageError):
    """No se encontró el selector de periodos en la página de SENAMHI."""


class IframeNotFoundError(ScrapingPageError):
    """No se encontró el iframe esperado en la página de SENAMHI."""


class ScrapingDataError(ScrapingError):
    """Error al interpretar la respuesta de datos de SENAMHI."""


class TableNotFoundError(ScrapingDataError):
    """No se encontró la tabla de datos esperada en la respuesta de SENAMHI."""


class OptionProcessingError(ScrapingError):
    """Falló el procesamiento de una opción o periodo del selector."""


__all__ = [
    "GaruaError",
    "ScrapingError",
    "BrowserNotFoundError",
    "ScrapingPageError",
    "SelectNotFoundError",
    "IframeNotFoundError",
    "ScrapingDataError",
    "TableNotFoundError",
    "OptionProcessingError",
]
