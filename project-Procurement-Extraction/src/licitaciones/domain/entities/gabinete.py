from dataclasses import dataclass

from licitaciones.domain.valueObjects.value_objects import Dimensiones


@dataclass
class Gabinete:
    """Entity - Especificaciones del gabinete"""

    id: int | None = None
    producto_id: int | None = None
    material: str | None = None
    acceso: str | None = None
    grado_proteccion: str | None = None
    espesor_chapa: float | None = None
    tipo_pintura: str | None = None
    color: str | None = None
    espesor_pintura: float | None = None
    dimensiones: Dimensiones | None = None
    peso: int | None = None

    def __post_init__(self):
        # Convertir dimensiones individuales en Value Object si existen
        if hasattr(self, "ancho") and hasattr(self, "alto") and hasattr(self, "profundidad"):
            if self.ancho or self.alto or self.profundidad:
                self.dimensiones = Dimensiones(
                    ancho=self.ancho, alto=self.alto, profundidad=self.profundidad
                )
