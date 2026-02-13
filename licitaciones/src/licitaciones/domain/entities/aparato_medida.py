from dataclasses import dataclass


@dataclass
class AparatosMedida:
    """Entity - Aparatos de medida"""

    id: int | None = None
    producto_id: int | None = None
    unidad_digital_centralizada: bool | None = None
    protocolo_comunicacion: str | None = None
    puerto_comunicacion: str | None = None
    medicion: dict | None = None
