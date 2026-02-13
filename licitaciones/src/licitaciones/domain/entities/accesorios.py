from dataclasses import dataclass


@dataclass
class Accesorios:
    """Entity - Accesorios del producto"""

    id: int | None = None
    producto_id: int | None = None
    panel_control: str | None = None
    resistencias_calefactoras: str | None = None
    tension_resistencias: int | None = None
    potencia_resistencias: str | None = None
    cables_incluidos: str | None = None
    tension_aislacion_cables: str | None = None
    material_cables: str | None = None
    baja_emision_halogenos: bool | None = None
    bornes_reserva: bool | None = None
    placas_identificacion: bool | None = None
    chapa_caracteristicas: bool | None = None
