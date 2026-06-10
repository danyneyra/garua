"""
Modelos de datos para el SENAMHI Scraper.
"""

from .station import (
    Station,
    StationCategory,
    StationType,
    StationStatus,
    StationSummary,
)

from .scraping import ScrapingErrorResponse, ScrapingSuccessResponse

from .data_schema import (
    get_headers_for_station_type,
    get_expected_columns_count,
    validate_csv_row,
    METEOROLOGICAL_CONVENTIONAL_HEADERS,
    METEOROLOGICAL_AUTOMATIC_HEADERS,
    HYDROLOGICAL_CONVENTIONAL_HEADERS,
    HYDROLOGICAL_AUTOMATIC_HEADERS,
)

from .recommendation import (
    RecommendationCriteria,
    StationRecommendation,
    RecommendationResponse,
)

from .comparison import (
    ComparisonPeriod,
    ComparisonWarning,
    PeriodSummary,
    PeriodDifference,
    SchemaInfo,
    ComparePeriodsResponse,
)

from .anomaly import (
    AnomalyIssue,
    DataQualitySummary,
    DetectAnomaliesResponse,
)

from .summary import (
    SummaryPeriod,
    SummaryQuality,
    SummaryResponse,
    SummaryWarning,
)

from .query import QueryMode, OutputFormat, DateRange, QueryRequest, ScrapingResult

from .responses import (
    SuccessResponse,
    ErrorResponse,
)

__all__ = [
    # Station models
    "Station",
    "StationCategory",
    "StationType",
    "StationStatus",
    "StationSummary",
    # Recommendation models
    "RecommendationCriteria",
    "StationRecommendation",
    "RecommendationResponse",
    # Comparison models
    "ComparisonPeriod",
    "ComparisonWarning",
    "PeriodSummary",
    "PeriodDifference",
    "SchemaInfo",
    "ComparePeriodsResponse",
    # Anomaly models
    "AnomalyIssue",
    "DataQualitySummary",
    "DetectAnomaliesResponse",
    # Summary models
    "SummaryPeriod",
    "SummaryQuality",
    "SummaryResponse",
    "SummaryWarning",
    # Query models
    "QueryMode",
    "OutputFormat",
    "DateRange",
    "QueryRequest",
    "ScrapingResult",
    # Response models
    "SuccessResponse",
    "ErrorResponse",
    # Scraping response models
    "ScrapingErrorResponse",
    "ScrapingSuccessResponse",
    # Data schema functions
    "get_headers_for_station_type",
    "get_expected_columns_count",
    "validate_csv_row",
    # Headers constants
    "METEOROLOGICAL_CONVENTIONAL_HEADERS",
    "METEOROLOGICAL_AUTOMATIC_HEADERS",
    "HYDROLOGICAL_CONVENTIONAL_HEADERS",
    "HYDROLOGICAL_AUTOMATIC_HEADERS",
]
