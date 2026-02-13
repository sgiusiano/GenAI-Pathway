from sqlalchemy.orm import Session

from licitaciones.application.buscar_por_query_use_case import BuscarPorQueryUseCase
from licitaciones.infrastructure.persistence.repositories.producto_repository_impl import (
    ProductoRepository,
)


class DependencyContainer:
    """Contenedor de dependencias para inyección de dependencias"""

    def __init__(self, session: Session):
        self.session = session

        # Repositorios
        self.producto_repository = ProductoRepository(session)

        # Casos de uso
        self.buscar_por_query = BuscarPorQueryUseCase(self.producto_repository)
