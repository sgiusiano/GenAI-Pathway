from dataclasses import dataclass


@dataclass
class Senalizacion:
    """Entity - Señalizaciones del producto"""

    id: int | None = None
    producto_id: int | None = None
    tipo: str = ""
    descripcion: str | None = None
    tipo_display: str | None = None
