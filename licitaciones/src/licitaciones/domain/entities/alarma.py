from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from licitaciones.domain.entities.tipo_alarma import TipoAlarma


@dataclass
class Alarma:
    """Entity - Alarma del producto"""

    id: int | None = None
    producto_id: int | None = None
    tipo_alarma_id: int | None = None
    tipo_senal: str | None = None
    activa: bool = True

    # Relación
    tipo_alarma: "TipoAlarma | None" = None
