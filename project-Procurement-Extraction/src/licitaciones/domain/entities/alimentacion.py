from dataclasses import dataclass

from licitaciones.domain.valueObjects.value_objects import RangoTension


@dataclass
class Alimentacion:
    """Entity - Especificaciones de alimentación"""

    id: int | None = None
    producto_id: int | None = None
    tipo: str | None = None
    tension: str | None = None
    rango_tension: RangoTension | None = None
    frecuencia: int | None = None
    rango_frecuencia: str | None = None
    conexion_neutro: str | None = None
    conductor_pe_independiente: bool | None = None
    corriente_cortocircuito: str | None = None
    tipo_interruptor_acometida: str | None = None
    potencia_transformador: str | None = None
    corriente_conexion_transformador: str | None = None

    def __post_init__(self):
        if self.rango_tension and isinstance(self.rango_tension, str):
            self.rango_tension = RangoTension.from_string(self.rango_tension)
