"""Application Context - Factory de dependencias.

Responsable de crear e inyectar todas las dependencias de la aplicación.
"""

from licitaciones.config import LLMProvider, Settings, get_settings
from licitaciones.db.connection import DatabaseConnection
from licitaciones.extraction.extraction_pipeline import ExtractionPipeline
from licitaciones.extraction.pdf_processor import PDFProcessor
from licitaciones.extraction.product_extractor import GeminiProductExtractor
from licitaciones.extraction.properties_extractor import (
    GeminiPropertiesExtractor,
    OpenAIPropertiesExtractor,
)
from licitaciones.extraction.protocols import PropertiesExtractorProtocol


class ApplicationContext:
    """Factory que crea e inyecta todas las dependencias.

    Esta clase es responsable de:
    1. Cargar configuración
    2. Crear todas las instancias de servicios
    3. Conectar todo con inyección de dependencias
    """

    def __init__(self) -> None:
        """Inicializa el contexto de la aplicación."""
        # 1. Cargar configuración
        self._settings = get_settings()

        # 2. Crear conexión a BD
        self._db_connection = DatabaseConnection(settings=self._settings)

        # 3. Crear extractores
        self._pdf_processor = PDFProcessor(settings=self._settings)
        self._product_extractor = GeminiProductExtractor(settings=self._settings)

        # 4. Crear extractor de propiedades según configuración
        self._properties_extractor = self._create_properties_extractor()

        # 5. Crear pipeline con dependencias inyectadas
        self._extraction_pipeline = ExtractionPipeline(
            pdf_preprocessor=self._pdf_processor,
            product_extractor=self._product_extractor,
            properties_extractor=self._properties_extractor,
        )

    @property
    def settings(self) -> Settings:
        """Configuración de la aplicación."""
        return self._settings

    @property
    def db_connection(self) -> DatabaseConnection:
        """Conexión a la base de datos."""
        return self._db_connection

    @property
    def extraction_pipeline(self) -> ExtractionPipeline:
        """Pipeline de extracción de PDFs."""
        return self._extraction_pipeline

    def close(self) -> None:
        """Cierra la conexión a la base de datos."""
        self._db_connection.close()

    def _create_properties_extractor(self) -> PropertiesExtractorProtocol:
        """Crea el extractor de propiedades según configuración."""
        if self._settings.structured_output_provider == LLMProvider.GEMINI.value:
            return GeminiPropertiesExtractor(
                settings=self._settings,
                model_name=self._settings.structured_output_model_gemini,
                temperature=self._settings.structured_output_temperature,
            )
        return OpenAIPropertiesExtractor(
            settings=self._settings,
            model_name=self._settings.structured_output_model_openai,
            temperature=self._settings.structured_output_temperature,
        )
