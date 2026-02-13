# domain/repositories/producto_repository.py
from abc import ABC, abstractmethod

from licitaciones.domain.entities.producto import Producto


class IProductoRepository(ABC):
    """Interface del repositorio de productos"""

    @abstractmethod
    def buscar_por_query(
        self,
        sql_query: str,
        validar: bool = True,
        seguridad: bool = True,
        umbral_minimo: float = 0.5,
    ) -> list[Producto]:
        """Busca productos por una cadena de búsqueda"""
