from dataclasses import dataclass


@dataclass
class Garantia:
    """Entity - Garantía del producto"""

    id: int | None = None
    producto_id: int | None = None
    meses: int = 24
    condiciones: str | None = None
