from dataclasses import dataclass

from licitaciones.domain.entities.producto import Producto


@dataclass
class ProductoConScore:
    """
    Entidad que representa un Producto con su score de coincidencia
    Útil para búsquedas con ranking/scoring
    """

    producto: Producto
    origen_consulta: int
    score_tipo_producto: float
    score_tipo_alimentacion: float
    score_tension: float
    score_frecuencia: float
    score_tension_nominal: float
    score_corriente_nominal: float
    match_score_total: float

    def __str__(self):
        return (
            f"ProductoConScore(codigo={self.producto.codigo}, "
            f"score={self.match_score_total:.2f}, "
            f"origen={self.origen_consulta})"
        )

    def es_relevante(self, umbral: float = 0.5) -> bool:
        """Verifica si el producto supera el umbral de relevancia"""
        return self.match_score_total >= umbral
