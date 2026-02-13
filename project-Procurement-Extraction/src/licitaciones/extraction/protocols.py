"""Protocols para extractores de productos.

Define las interfaces (contratos) que deben implementar los extractores.
"""

from pathlib import Path
from typing import Protocol

from licitaciones.domain.extraction_models import LicitacionCompleta


class ProductExtractorProtocol(Protocol):
    """Protocol para extractores de productos desde PDFs.

    El ProductExtractor es responsable de:
    1. Recibir un archivo PDF
    2. Extraer el contenido relevante (productos y especificaciones)
    3. Retornar texto no estructurado con la información extraída
    """

    def extract_from_pdf(self, pdf_path: Path) -> str:
        """Extrae información de productos desde un PDF.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            Texto con la información extraída del PDF.
        """
        ...


class PropertiesExtractorProtocol(Protocol):
    """Protocol para estructurar propiedades extraídas.

    El PropertiesExtractor es responsable de:
    1. Recibir texto no estructurado
    2. Convertirlo a modelos Pydantic estructurados
    3. Retornar LicitacionCompleta con todos los items
    """

    def structure_properties(self, raw_text: str) -> LicitacionCompleta:
        """Estructura el texto extraído en modelos Pydantic.

        Args:
            raw_text: Texto no estructurado con información de productos.

        Returns:
            LicitacionCompleta con especificaciones comunes e items.
        """
        ...


class ExtractionPipelineProtocol(Protocol):
    """Protocol para el pipeline completo de extracción.

    Combina ProductExtractor y PropertiesExtractor en un flujo único.
    """

    def process_pdf(self, pdf_path: Path) -> LicitacionCompleta:
        """Procesa un PDF y retorna datos estructurados.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            LicitacionCompleta con todos los datos extraídos.
        """
        ...
