from dataclasses import dataclass


@dataclass
class TipoEnsayo:
    """Entity - Catálogo de tipos de ensayo"""

    id: int | None = None
    codigo: str = ""
    descripcion: str = ""
    orden: int | None = None
