"""PDF extraction and processing module."""

from licitaciones.extraction.extraction_pipeline import ExtractionPipeline
from licitaciones.extraction.product_extractor import GeminiProductExtractor
from licitaciones.extraction.properties_extractor import (
    GeminiPropertiesExtractor,
    OpenAIPropertiesExtractor,
)
from licitaciones.extraction.protocols import (
    ProductExtractorProtocol,
    PropertiesExtractorProtocol,
)

__all__ = [
    "ExtractionPipeline",
    "GeminiProductExtractor",
    "GeminiPropertiesExtractor",
    "OpenAIPropertiesExtractor",
    "ProductExtractorProtocol",
    "PropertiesExtractorProtocol",
]
