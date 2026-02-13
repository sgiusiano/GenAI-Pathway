from licitaciones.domain.entities.producto import Producto
from licitaciones.domain.repositories.producto_repository import IProductoRepository


class BuscarPorQueryUseCase:
    """
    Caso de uso para buscar productos con SQL raw generado por LLM
    """

    def __init__(self, producto_repository: IProductoRepository):
        self.producto_repository = producto_repository

    def execute(
        self,
        sql_query: str,
        validar: bool = True,
        seguridad: bool = True,
        umbral_minimo: float = 0.5,
    ) -> list[Producto]:
        """
        Ejecuta una búsqueda con SQL raw del LLM

        Args:
            sql_query: Query SQL generada por el LLM (como string)
            validar: Si valida el SQL antes de ejecutar
            seguridad: Si aplica validaciones de seguridad
            umbral_minimo: Score mínimo para filtrar resultados

        Returns:
            Lista de productos que cumplen los criterios

        Raises:
            ValueError: Si el SQL es inválido o inseguro

        Ejemplo:
            sql = '''
            SELECT * FROM (
                SELECT DISTINCT p.*,
                    similarity(p.tipo, 'Rectificador') AS match_score_total
                FROM productos p
            ) q
            WHERE q.match_score_total > 0.5
            LIMIT 10
            '''

            use_case = BuscarPorQueryUseCase(producto_repo)
            productos = use_case.execute(sql)
        """
        return self.producto_repository.buscar_por_query(
            sql_query=sql_query, validar=validar, seguridad=seguridad, umbral_minimo=umbral_minimo
        )
