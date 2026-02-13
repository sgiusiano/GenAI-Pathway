from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from licitaciones.domain.entities.producto import Producto
from licitaciones.domain.repositories.producto_repository import IProductoRepository
from licitaciones.domain.services.sql_validator_service import SQLValidatorService
from licitaciones.infrastructure.persistence.mappers.producto_mapper import ProductoMapper
from licitaciones.infrastructure.persistence.models.producto_model import ProductoModel


class ProductoRepository(IProductoRepository):
    """Implementación del repositorio de productos"""

    def __init__(self, session: Session):
        self.session = session
        self.mapper = ProductoMapper()
        self.validator = SQLValidatorService()

    def buscar_por_query(
        self,
        sql_query: str,
        validar: bool = True,
        seguridad: bool = True,
        umbral_minimo: float = 0.5,
    ) -> list[Producto]:
        """
        Busca productos ejecutando SQL raw del LLM

        Args:
            sql_query: Query SQL generada por el LLM
            validar: Si valida el SQL antes de ejecutar
            seguridad: Si aplica validaciones de seguridad
            umbral_minimo: Score mínimo para filtrar resultados

        Returns:
            Lista de productos encontrados
        """
        # 1. Validar SQL si está habilitado
        if validar and seguridad:
            validacion = self.validator.validar(sql_query)
            if not validacion.es_valido:
                errores = "\n".join(validacion.errores)
                raise ValueError(f"SQL inválido o inseguro:\n{errores}")

        # 2. Ejecutar la query raw
        result = self.session.execute(text(sql_query))
        columnas = result.keys()

        # 3. Procesar resultados
        productos = []
        for row in result:
            row_dict = dict(zip(columnas, row))

            # Filtrar por umbral si hay score
            if "match_score_total" in row_dict:
                score = float(row_dict["match_score_total"])
                if score < umbral_minimo:
                    continue

            # Obtener ID y cargar producto completo
            producto_id = row_dict.get("id")
            if producto_id:
                producto = self._cargar_producto_completo(producto_id)
                if producto:
                    productos.append(producto)

        return productos

    def _cargar_producto_completo(self, producto_id: int) -> Producto:
        """Carga un producto con todas sus relaciones"""
        model = (
            self.session.query(ProductoModel)
            .options(
                joinedload(ProductoModel.accesorios),
                joinedload(ProductoModel.alarmas).joinedload("tipo_alarma"),
                joinedload(ProductoModel.alimentacion),
                joinedload(ProductoModel.aparatos_medida),
                joinedload(ProductoModel.ensayos).joinedload("tipo_ensayo"),
                joinedload(ProductoModel.especificaciones),
                joinedload(ProductoModel.gabinete),
                joinedload(ProductoModel.garantia),
                joinedload(ProductoModel.salida),
                joinedload(ProductoModel.senalizaciones),
            )
            .filter(ProductoModel.id == producto_id)
            .first()
        )

        return self.mapper.to_entity(model) if model else None
