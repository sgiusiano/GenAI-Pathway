from dataclasses import dataclass


@dataclass
class Especificaciones:
    """Entity - Especificaciones técnicas del producto"""

    id: int | None = None
    producto_id: int | None = None
    normas_fabricacion: str | None = None
    apto_pb_ac: bool = True
    apto_ni_cd: bool = True
    temperatura_maxima: float | None = None
    temperatura_minima: float | None = None
    altura_snm: int | None = None
    humedad_relativa_max: float | None = None
    tipo_instalacion: str | None = None
    tipo_servicio: str | None = None
    ventilacion: str | None = None
    tipo_rectificador: str | None = None
    nivel_ruido: str | None = None
    rendimiento_minimo: float | None = None
    proteccion_sobretension: str | None = None
    proteccion_cortocircuito: str | None = None
    proteccion_sobrecarga: str | None = None
    ripple_con_baterias: str | None = None
    ripple_sin_baterias: str | None = None
    tension_flote_min: float | None = None
    tension_flote_max: float | None = None
    tension_fondo_min: float | None = None
    tension_fondo_max: float | None = None
    modo_manual_automatico: bool | None = None
    modo_carga_excepcional: bool | None = None
    regulador_diodos_carga: str | None = None
    rango_salida_nicd: str | None = None
    rango_salida_pbca: str | None = None
    deteccion_polo_tierra: bool | None = None
