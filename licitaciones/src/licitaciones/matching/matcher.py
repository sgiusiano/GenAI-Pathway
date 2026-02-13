"""Matching de productos extraídos contra el catálogo.

Este módulo es un placeholder para la lógica de matching futura.
"""

from dataclasses import dataclass

from licitaciones.domain.db_models import Producto
from licitaciones.domain.extraction_models import ItemLicitado


@dataclass
class MatchResult:
    """Resultado de matching entre un item licitado y productos del catálogo."""

    item_licitado: ItemLicitado
    productos_coincidentes: list[Producto]
    score: float  # 0.0 - 1.0
    notas: str | None = None


class ProductMatcher:
    """Placeholder para lógica de matching de productos.

    Esta clase será implementada en una futura iteración.

    La lógica de matching deberá considerar:
    - Tensión nominal (exacta o dentro de rango)
    - Corriente nominal (igual o mayor a la requerida)
    - Características técnicas compatibles
    - Certificaciones y normas requeridas
    """

    def match(
        self,
        extracted_items: list[ItemLicitado],
        catalog: list[Producto],
    ) -> list[MatchResult]:
        """Encuentra productos del catálogo que coinciden con items licitados.

        Args:
            extracted_items: Lista de items extraídos de la licitación.
            catalog: Lista de productos del catálogo.

        Returns:
            Lista de resultados de matching.

        Raises:
            NotImplementedError: Esta funcionalidad aún no está implementada.
        """
        raise NotImplementedError(
            "Matching logic pending implementation. This will be developed in a future iteration."
        )

    def match_single(
        self,
        item: ItemLicitado,
        catalog: list[Producto],
    ) -> MatchResult:
        """Encuentra productos que coinciden con un solo item.

        Args:
            item: Item a matchear.
            catalog: Lista de productos del catálogo.

        Returns:
            Resultado de matching para el item.

        Raises:
            NotImplementedError: Esta funcionalidad aún no está implementada.
        """
        raise NotImplementedError(
            "Matching logic pending implementation. This will be developed in a future iteration."
        )

    def calculate_compatibility_score(
        self,
        item: ItemLicitado,
        producto: Producto,
    ) -> float:
        """Calcula un score de compatibilidad entre item y producto.

        Args:
            item: Item de la licitación.
            producto: Producto del catálogo.

        Returns:
            Score de 0.0 a 1.0 indicando compatibilidad.

        Raises:
            NotImplementedError: Esta funcionalidad aún no está implementada.
        """
        raise NotImplementedError(
            "Matching logic pending implementation. This will be developed in a future iteration."
        )
