"""Extractor de propiedades estructuradas.

Utiliza modelos LLM para convertir texto extraído en modelos Pydantic estructurados.
"""

import json

from google import genai
from google.genai import types
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from licitaciones.config import Settings, get_settings
from licitaciones.domain.extraction_models import LicitacionCompleta
from licitaciones.extraction.prompts import MULTI_ITEM_EXTRACTION_PROMPT


class OpenAIPropertiesExtractor:
    """Estructura propiedades extraídas usando OpenAI.

    Responsabilidades:
    - Recibir texto no estructurado
    - Usar structured output de OpenAI/LangChain
    - Retornar LicitacionCompleta con todos los items
    """

    def __init__(
        self,
        settings: Settings | None = None,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0,
    ) -> None:
        """Inicializa el extractor.

        Args:
            settings: Configuración de la aplicación.
            model_name: Nombre del modelo OpenAI a usar.
            temperature: Temperatura del modelo (0 = más determinístico).
        """
        self._settings = settings or get_settings()
        self._model_name = model_name
        self._temperature = temperature
        self._configure_chain()

    def _configure_chain(self) -> None:
        """Configura la cadena de LangChain."""
        self._llm = ChatOpenAI(
            model=self._model_name,
            temperature=self._temperature,
            api_key=self._settings.openai_api_key,
        )

        self._prompt = ChatPromptTemplate.from_template(
            MULTI_ITEM_EXTRACTION_PROMPT + "\n\n**Text to process:**\n{text_chunk}"
        )

        self._chain = self._prompt | self._llm.with_structured_output(LicitacionCompleta)

    def structure_properties(self, raw_text: str) -> LicitacionCompleta:
        """Estructura el texto extraído en modelos Pydantic.

        Args:
            raw_text: Texto no estructurado con información de productos.

        Returns:
            LicitacionCompleta con especificaciones comunes e items.
        """
        return self._chain.invoke({"text_chunk": raw_text})


class GeminiPropertiesExtractor:
    """Estructura propiedades extraídas usando Gemini.

    Usa google-genai SDK directamente en lugar de langchain_google_genai
    porque este último tiene problemas al convertir modelos Pydantic complejos
    con tipos anidados y Decimal al formato de function declaration de Gemini.

    Responsabilidades:
    - Recibir texto no estructurado
    - Usar structured output de google-genai SDK
    - Retornar LicitacionCompleta con todos los items
    """

    def __init__(
        self,
        settings: Settings | None = None,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0,
    ) -> None:
        """Inicializa el extractor.

        Args:
            settings: Configuración de la aplicación.
            model_name: Nombre del modelo Gemini a usar.
            temperature: Temperatura del modelo (0 = más determinístico).
        """
        self._settings = settings or get_settings()
        self._model_name = model_name
        self._temperature = temperature
        self._client = genai.Client(api_key=self._settings.google_api_key)

    def structure_properties(self, raw_text: str) -> LicitacionCompleta:
        """Estructura el texto extraído en modelos Pydantic.

        Args:
            raw_text: Texto no estructurado con información de productos.

        Returns:
            LicitacionCompleta con especificaciones comunes e items.

        Note:
            No usamos response_json_schema porque el schema de LicitacionCompleta
            es demasiado complejo (muchos campos anidados) y Gemini rechaza schemas
            que generan demasiados "states". En su lugar, incluimos el schema en
            el prompt y validamos con Pydantic después.
        """
        schema_json = json.dumps(LicitacionCompleta.model_json_schema(), indent=2)
        full_prompt = (
            f"{MULTI_ITEM_EXTRACTION_PROMPT}\n\n"
            f"**JSON Schema to follow:**\n```json\n{schema_json}\n```\n\n"
            f"**Text to process:**\n{raw_text}"
        )

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=self._temperature,
                response_mime_type="application/json",
            ),
        )

        return LicitacionCompleta.model_validate_json(response.text)
