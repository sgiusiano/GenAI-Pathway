"""Modelos Pydantic que mapean 1:1 con las tablas de la base de datos.

Estos modelos representan la estructura de datos normalizada en PostgreSQL.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from licitaciones.domain.enums import ReguladorDiodosTipo

# ============================================
# MODELOS BASE
# ============================================


class DBModelBase(BaseModel):
    """Modelo base para todos los modelos de BD."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class DBModelWithId(DBModelBase):
    """Modelo base con ID."""

    id: int | None = None


# ============================================
# TABLA: productos
# ============================================


class ProductoCreate(DBModelBase):
    """Modelo para crear un producto (sin ID)."""

    codigo: str = Field(..., max_length=50)
    marca: str = Field(..., max_length=100)
    modelo: str = Field(..., max_length=50)
    tension_nominal: int
    corriente_nominal: int
    regulador_diodos: ReguladorDiodosTipo | None = None
    origen: str | None = Field(default="Argentina", max_length=100)
    tipo: str | None = Field(default="Autorregulado", max_length=100)


class Producto(ProductoCreate, DBModelWithId):
    """Modelo completo de producto (con ID y timestamps)."""

    created_at: datetime | None = None
    updated_at: datetime | None = None


# ============================================
# TABLA: especificaciones
# ============================================


class EspecificacionesCreate(DBModelBase):
    """Modelo para crear especificaciones."""

    producto_id: int

    # Generales
    normas_fabricacion: str | None = None
    apto_pb_ac: bool | None = True
    apto_ni_cd: bool | None = True

    # Condiciones ambientales
    temperatura_maxima: Decimal | None = None
    temperatura_minima: Decimal | None = None
    altura_snm: int | None = None
    humedad_relativa_max: Decimal | None = None
    tipo_instalacion: str | None = Field(default=None, max_length=50)
    tipo_servicio: str | None = Field(default=None, max_length=50)

    # Características técnicas
    ventilacion: str | None = Field(default=None, max_length=50)
    tipo_rectificador: str | None = None
    nivel_ruido: str | None = Field(default=None, max_length=10)
    rendimiento_minimo: Decimal | None = None

    # Protecciones
    proteccion_sobretension: str | None = None
    proteccion_cortocircuito: str | None = None
    proteccion_sobrecarga: str | None = None

    # Ripple
    ripple_con_baterias: str | None = Field(default=None, max_length=10)
    ripple_sin_baterias: str | None = Field(default=None, max_length=10)

    # Tensiones de carga
    tension_flote_min: Decimal | None = None
    tension_flote_max: Decimal | None = None
    tension_fondo_min: Decimal | None = None
    tension_fondo_max: Decimal | None = None

    # Modos de operación
    modo_manual_automatico: bool | None = None
    modo_carga_excepcional: bool | None = None
    regulador_diodos_carga: str | None = Field(default=None, max_length=50)
    rango_salida_nicd: str | None = Field(default=None, max_length=50)
    rango_salida_pbca: str | None = Field(default=None, max_length=50)
    deteccion_polo_tierra: bool | None = None


class Especificaciones(EspecificacionesCreate, DBModelWithId):
    """Modelo completo de especificaciones."""

    pass


# ============================================
# TABLA: alimentacion
# ============================================


class AlimentacionCreate(DBModelBase):
    """Modelo para crear alimentación."""

    producto_id: int

    tipo: str | None = Field(default=None, max_length=50)  # 'Trifásico', 'Monofásico'
    tension: str | None = Field(default=None, max_length=50)
    rango_tension: str | None = Field(default=None, max_length=50)
    frecuencia: int | None = None
    rango_frecuencia: str | None = Field(default=None, max_length=50)
    conexion_neutro: str | None = Field(default=None, max_length=50)
    conductor_pe_independiente: bool | None = None
    corriente_cortocircuito: str | None = Field(default=None, max_length=100)
    tipo_interruptor_acometida: str | None = None
    potencia_transformador: str | None = Field(default=None, max_length=50)
    corriente_conexion_transformador: str | None = Field(default=None, max_length=50)


class Alimentacion(AlimentacionCreate, DBModelWithId):
    """Modelo completo de alimentación."""

    pass


# ============================================
# TABLA: salida
# ============================================


class SalidaCreate(DBModelBase):
    """Modelo para crear salida."""

    producto_id: int

    tension_nominal: int | None = None
    corriente_nominal: int | None = None
    maxima_corriente_consumos: int | None = None
    tipo_interruptor_consumo: str | None = None
    tipo_interruptor_baterias: str | None = None
    sistema_rectificacion: str | None = None


class Salida(SalidaCreate, DBModelWithId):
    """Modelo completo de salida."""

    pass


# ============================================
# TABLA: gabinete
# ============================================


class GabineteCreate(DBModelBase):
    """Modelo para crear gabinete."""

    producto_id: int

    material: str | None = Field(default=None, max_length=100)
    acceso: str | None = Field(default=None, max_length=100)
    grado_proteccion: str | None = Field(default=None, max_length=10)  # IP21, IP54, etc.
    espesor_chapa: Decimal | None = None
    tipo_pintura: str | None = Field(default=None, max_length=100)
    color: str | None = Field(default=None, max_length=20)  # RAL 7032, etc.
    espesor_pintura: Decimal | None = None
    ancho: int | None = None  # mm
    alto: int | None = None  # mm
    profundidad: int | None = None  # mm
    peso: int | None = None  # kg


class Gabinete(GabineteCreate, DBModelWithId):
    """Modelo completo de gabinete."""

    pass


# ============================================
# TABLA: aparatos_medida
# ============================================


class AparatosMedidaCreate(DBModelBase):
    """Modelo para crear aparatos de medida."""

    producto_id: int

    unidad_digital_centralizada: bool | None = None
    protocolo_comunicacion: str | None = Field(default=None, max_length=50)  # 'Modbus RTU'
    puerto_comunicacion: str | None = Field(default=None, max_length=100)  # 'RS485', 'TCP-IP'
    medicion: dict[str, Any] | None = None  # JSONB


class AparatosMedida(AparatosMedidaCreate, DBModelWithId):
    """Modelo completo de aparatos de medida."""

    pass


# ============================================
# TABLA: accesorios
# ============================================


class AccesoriosCreate(DBModelBase):
    """Modelo para crear accesorios."""

    producto_id: int

    panel_control: str | None = None
    resistencias_calefactoras: bool | None = None
    tension_resistencias: int | None = None
    potencia_resistencias: str | None = Field(default=None, max_length=100)
    cables_incluidos: bool | None = None
    tension_aislacion_cables: str | None = Field(default=None, max_length=20)
    material_cables: str | None = Field(default=None, max_length=50)
    baja_emision_halogenos: bool | None = None
    bornes_reserva: bool | None = None
    placas_identificacion: bool | None = None
    chapa_caracteristicas: bool | None = None


class Accesorios(AccesoriosCreate, DBModelWithId):
    """Modelo completo de accesorios."""

    pass


# ============================================
# TABLA: tipos_alarma (catálogo)
# ============================================


class TipoAlarma(DBModelWithId):
    """Modelo de tipo de alarma (catálogo)."""

    codigo: str = Field(..., max_length=50)
    descripcion: str


# ============================================
# TABLA: alarmas
# ============================================


class AlarmaCreate(DBModelBase):
    """Modelo para crear alarma."""

    producto_id: int
    tipo_alarma_id: int
    tipo_senal: str | None = Field(default=None, max_length=100)  # 'LCD + contacto seco'
    activa: bool = True


class Alarma(AlarmaCreate, DBModelWithId):
    """Modelo completo de alarma."""

    pass


# ============================================
# TABLA: senalizaciones
# ============================================


class SenalizacionCreate(DBModelBase):
    """Modelo para crear señalización."""

    producto_id: int
    tipo: str = Field(..., max_length=100)  # 'Red Ok', 'LED FLOTE'
    descripcion: str | None = None
    tipo_display: str | None = Field(default=None, max_length=50)  # 'LED frontal', 'Display LCD'


class Senalizacion(SenalizacionCreate, DBModelWithId):
    """Modelo completo de señalización."""

    pass


# ============================================
# TABLA: tipos_ensayo (catálogo)
# ============================================


class TipoEnsayo(DBModelWithId):
    """Modelo de tipo de ensayo (catálogo)."""

    codigo: str = Field(..., max_length=50)
    descripcion: str
    orden: int | None = None


# ============================================
# TABLA: ensayos
# ============================================


class EnsayoCreate(DBModelBase):
    """Modelo para crear ensayo."""

    producto_id: int
    tipo_ensayo_id: int
    realizado: bool = True
    observaciones: str | None = None


class Ensayo(EnsayoCreate, DBModelWithId):
    """Modelo completo de ensayo."""

    pass


# ============================================
# TABLA: garantia
# ============================================


class GarantiaCreate(DBModelBase):
    """Modelo para crear garantía."""

    producto_id: int
    meses: int = 24
    condiciones: str | None = None


class Garantia(GarantiaCreate, DBModelWithId):
    """Modelo completo de garantía."""

    pass


# ============================================
# MODELO AGREGADO: ProductoCompleto
# ============================================


class ProductoCompleto(DBModelBase):
    """Producto con todas sus relaciones."""

    producto: Producto
    especificaciones: Especificaciones | None = None
    alimentacion: Alimentacion | None = None
    salida: Salida | None = None
    gabinete: Gabinete | None = None
    aparatos_medida: AparatosMedida | None = None
    accesorios: Accesorios | None = None
    alarmas: list[Alarma] = Field(default_factory=list)
    senalizaciones: list[Senalizacion] = Field(default_factory=list)
    ensayos: list[Ensayo] = Field(default_factory=list)
    garantia: Garantia | None = None
