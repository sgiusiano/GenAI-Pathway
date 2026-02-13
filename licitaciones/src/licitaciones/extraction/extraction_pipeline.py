"""Pipeline de extracción de productos desde PDFs de licitaciones.

Orquesta los extractores siguiendo el principio de inversión de dependencias.
"""

import os
from pathlib import Path

from licitaciones.config import get_settings
from licitaciones.domain.extraction_models import LicitacionCompleta
from licitaciones.extraction.pdf_processor import PDFProcessor
from licitaciones.extraction.protocols import (
    ProductExtractorProtocol,
    PropertiesExtractorProtocol,
)
from licitaciones.logger import get_logger

logger = get_logger(__name__)


class ExtractionPipeline:
    """Pipeline completo de extracción.

    Orquesta ProductExtractor y PropertiesExtractor para procesar PDFs.
    Recibe protocolos (abstracciones) en lugar de implementaciones concretas.
    """

    def __init__(
        self,
        pdf_preprocessor: PDFProcessor,
        product_extractor: ProductExtractorProtocol,
        properties_extractor: PropertiesExtractorProtocol,
    ) -> None:
        """Inicializa el pipeline.

        Args:
            pdf_preprocessor: Procesador de PDF para validaciones y análisis de calidad.
            product_extractor: Extractor de productos (cumple ProductExtractorProtocol).
            properties_extractor: Estructurador de propiedades (cumple PropertiesExtractorProtocol).
        """
        self.settings = get_settings()
        self._pdf_preprocessor = pdf_preprocessor
        self._product_extractor = product_extractor
        self._properties_extractor = properties_extractor

    def process_pdf(
        self,
        pdf_path: Path,
        page_ranges: list[tuple[int, int]] | None = None,
    ) -> LicitacionCompleta:
        """Procesa un PDF y retorna datos estructurados.

        Args:
            pdf_path: Ruta al archivo PDF.
            page_ranges: Lista opcional de rangos de páginas a procesar.
                Formato: [(start, end), ...], 1-indexed, inclusive.
                Ej: [(1, 10), (15, 25)] procesa páginas 1-10 y 15-25.

        Returns:
            LicitacionCompleta con todos los datos extraídos.
        """
        temp_pdf_path: str | None = None
        pdf_to_process = str(pdf_path)

        try:
            # Paso 0: Extraer páginas si se especificaron rangos
            if page_ranges:
                temp_pdf_path = self._pdf_preprocessor.extract_pages(str(pdf_path), page_ranges)
                pdf_to_process = temp_pdf_path

            # Paso 1: Preprocesar PDF (calidad, validaciones)
            pdf_quality = self._pdf_preprocessor.check_quality(pdf_to_process)
            logger.info(
                "PDF quality analysis: score=%d, digital=%s, pages=%d, "
                "text_ratio=%.3f, image_coverage=%.2f, ocr_ratio=%.2f, "
                "low_res_images=%d, rotated_text=%.2f",
                pdf_quality.quality_score,
                pdf_quality.is_digital,
                pdf_quality.pages_analyzed,
                pdf_quality.text_to_size_ratio,
                pdf_quality.image_coverage_ratio,
                pdf_quality.ocr_text_ratio,
                pdf_quality.low_res_image_count,
                pdf_quality.rotated_text_ratio,
            )
            if pdf_quality.quality_score < self.settings.pdf_min_acceptable_quality_score:
                raise ValueError(
                    f"PDF quality score ({pdf_quality.quality_score}) is below minimum "
                    f"threshold ({self.settings.pdf_min_acceptable_quality_score}). "
                    f"Digital: {pdf_quality.is_digital}, "
                    f"OCR ratio: {pdf_quality.ocr_text_ratio:.2f}, "
                    f"Image coverage: {pdf_quality.image_coverage_ratio:.2f}"
                )

            # Paso 2: Extraer texto del PDF
            raw_text = self._product_extractor.extract_from_pdf(Path(pdf_to_process))

            # Paso 3: Estructurar con modelo de lenguaje
            structured_data = self._properties_extractor.structure_properties(raw_text)

            return structured_data
        finally:
            # Cleanup: eliminar PDF temporal si se creó
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
