"""Extractor de productos desde PDFs.

Utiliza Gemini para hacer file upload y extraer información de productos.
"""

import time
from pathlib import Path

from google import genai

from licitaciones.config import Settings, get_settings
from licitaciones.extraction.prompts import PRODUCT_EXTRACTION_PROMPT


class GeminiProductExtractor:
    """Extrae información de productos desde PDFs usando Gemini.

    Responsabilidades:
    - Subir el PDF a Gemini
    - Usar file search para extraer productos
    - Retornar texto no estructurado con la información
    """

    def __init__(
        self,
        settings: Settings | None = None,
        model_name: str = "gemini-2.5-flash",
    ) -> None:
        """Inicializa el extractor.

        Args:
            settings: Configuración de la aplicación.
            model_name: Nombre del modelo Gemini a usar.
        """
        self._settings = settings or get_settings()
        self._model_name = model_name
        self._client = genai.Client(api_key=self._settings.google_api_key)

    def extract_from_pdf(self, pdf_path: Path) -> str:
        """Extrae información de productos desde un PDF.

        Args:
            pdf_path: Ruta al archivo PDF.

        Returns:
            Texto con la información extraída.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si hay un error al procesar el PDF.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")

        # Subir archivo a Gemini
        uploaded_file = self._upload_file(pdf_path)

        try:
            # Generar contenido
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=[PRODUCT_EXTRACTION_PROMPT, uploaded_file],
            )
            return response.text
        finally:
            # Limpiar archivo subido
            try:
                self._client.files.delete(name=uploaded_file.name)
            except Exception:
                pass  # Ignorar errores de limpieza

    def _upload_file(self, pdf_path: Path):
        """Sube un archivo a Gemini y espera a que esté procesado.

        Args:
            pdf_path: Ruta al archivo.

        Returns:
            Archivo subido a Gemini.

        Raises:
            ValueError: Si hay un error al procesar el archivo.
        """
        uploaded_file = self._client.files.upload(file=str(pdf_path))

        # Esperar a que el archivo esté procesado
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = self._client.files.get(name=uploaded_file.name)

        if uploaded_file.state.name == "FAILED":
            raise ValueError(f"Error al procesar el archivo: {uploaded_file.state}")

        return uploaded_file

    def extract_from_pdf_with_custom_prompt(
        self,
        pdf_path: Path,
        prompt: str,
    ) -> str:
        """Extrae información usando un prompt personalizado.

        Args:
            pdf_path: Ruta al archivo PDF.
            prompt: Prompt personalizado para la extracción.

        Returns:
            Texto con la información extraída.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")

        uploaded_file = self._upload_file(pdf_path)

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=[prompt, uploaded_file],
            )
            return response.text
        finally:
            try:
                self._client.files.delete(name=uploaded_file.name)
            except Exception:
                pass
