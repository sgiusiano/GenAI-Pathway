from dataclasses import dataclass


@dataclass
class Salida:
    """Entity - Especificaciones de salida"""

    id: int | None = None
    producto_id: int | None = None
    tension_nominal: int | None = None
    corriente_nominal: int | None = None
    maxima_corriente_consumos: int | None = None
    tipo_interruptor_consumo: str | None = None
    tipo_interruptor_baterias: str | None = None
    sistema_rectificacion: str | None = None
