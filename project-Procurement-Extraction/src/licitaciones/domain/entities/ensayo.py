from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from licitaciones.domain.entities.tipo_ensayo import TipoEnsayo


@dataclass
class Ensayo:
    """Entity - Ensayo realizado al producto"""

    id: int | None = None
    producto_id: int | None = None
    tipo_ensayo_id: int | None = None
    realizado: bool = True
    observaciones: str | None = None

    # Relación
    tipo_ensayo: "TipoEnsayo | None" = None
