"""Modelos Pydantic para extracción de datos desde PDFs de licitaciones.

Estos modelos son jerárquicos y flexibles, diseñados para capturar
la información extraída de documentos de licitación.
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from licitaciones.domain.enums import (
    AlimentacionAlternativaTipo,
    ConexionNeutroTierra,
    FaseTipo,
    ServicioTipo,
)

# ============================================
# TIPOS REUTILIZABLES
# ============================================


class NumericRange(BaseModel):
    """Rango numérico genérico con unidad opcional."""

    model_config = ConfigDict(extra="forbid")

    min: Decimal = Field(..., description="Valor mínimo")
    max: Decimal = Field(..., description="Valor máximo")
    unidad: str | None = Field(default=None, description="Unidad (V, A, Hz, °C, kVA, etc.)")

    @field_validator("max")
    @classmethod
    def _min_le_max(cls, v: Decimal, info: object) -> Decimal:
        min_val = info.data.get("min") if hasattr(info, "data") else None
        if min_val is not None and v < min_val:
            raise ValueError("max debe ser >= min")
        return v


class Dimensiones(BaseModel):
    """Dimensiones físicas."""

    model_config = ConfigDict(extra="forbid")

    ancho_mm: Decimal | None = Field(default=None, description="Ancho en mm")
    alto_mm: Decimal | None = Field(default=None, description="Alto en mm")
    profundidad_mm: Decimal | None = Field(default=None, description="Profundidad en mm")


class InterruptorSpec(BaseModel):
    """Especificación de interruptor."""

    model_config = ConfigDict(extra="forbid")

    tipo: str | None = Field(default=None, description="Tipo de interruptor")
    calibre_a: Decimal | None = Field(default=None, description="Calibre en amperes (A)")


# ============================================
# SECCIONES DEL SISTEMA
# ============================================


class Generales(BaseModel):
    """Información general del producto."""

    model_config = ConfigDict(extra="forbid")

    codigo_producto: str | None = None
    marca: str | None = None
    modelo: str | None = None
    normas_fabricacion: str | None = Field(default=None, description="Normas / estándares")
    origen: str | None = Field(default=None, description="País o región de fabricación")
    tipo: str | None = Field(default=None, description="Familia / categoría del equipo")
    apto_baterias_pb_y_nicd: bool | None = Field(
        default=None, description="Apto para Pb-Ca/Pb-Ac y Ni-Cd"
    )


class CondicionesAmbientales(BaseModel):
    """Condiciones ambientales de operación."""

    model_config = ConfigDict(extra="forbid")

    temperatura_max_c: Decimal | None = Field(
        default=None, description="Temperatura máxima de operación (°C)"
    )
    temperatura_min_c: Decimal | None = Field(
        default=None, description="Temperatura mínima de operación (°C)"
    )
    altura_snm_m: Decimal | None = Field(
        default=None, description="Altura sobre el nivel del mar (m)"
    )
    humedad_relativa_max_pct: Decimal | None = Field(
        default=None, description="Humedad relativa máx. sin condensación (%)"
    )
    instalacion: str | None = Field(default=None, description="Interior/Exterior/Armario/etc.")
    tipo_servicio: ServicioTipo | None = None


class AlimentacionExtraccion(BaseModel):
    """Especificaciones de alimentación eléctrica (extracción)."""

    model_config = ConfigDict(extra="forbid")

    tipo: FaseTipo | None = Field(default=None, description="Tipo de fase")
    tension_v: Decimal | None = Field(default=None, description="Tensión nominal (V)")
    rango_tension_entrada: NumericRange | None = Field(
        default=None, description="Rango de tensión admisible (V)"
    )
    frecuencia_hz: Decimal | None = Field(default=None, description="Frecuencia nominal (Hz)")
    rango_frecuencia_entrada: NumericRange | None = Field(
        default=None, description="Rango de frecuencia admisible (Hz)"
    )
    conexion_neutro_tierra: ConexionNeutroTierra | None = Field(
        default=None, description="Esquema de conexión a tierra"
    )
    conductor_pe_independiente: bool | None = Field(
        default=None, description="PE independiente del neutro"
    )
    isc_punto_conexion: Decimal | None = Field(
        default=None, description="Corriente de cortocircuito en punto de conexión (A o kA)"
    )
    interruptor_acometida: InterruptorSpec | None = Field(
        default=None, description="Interruptor de acometida"
    )
    potencia_transformador_entrada_kva: Decimal | None = Field(
        default=None, description="Potencia del transformador de entrada (kVA)"
    )
    corriente_conexion_transformador_a: Decimal | None = Field(
        default=None, description="Corriente de conexión del transformador (A)"
    )


class SalidaExtraccion(BaseModel):
    """Especificaciones de salida eléctrica (extracción)."""

    model_config = ConfigDict(extra="forbid")

    tension_nominal_v: Decimal | None = Field(
        default=None, description="Tensión nominal de salida fija (V)"
    )
    corriente_nominal_a: Decimal | None = Field(
        default=None, description="Corriente nominal de salida fija (A)"
    )
    maxima_corriente_consumos_a: Decimal | None = Field(
        default=None, description="Máxima corriente a consumos (A)"
    )

    # Campos para salidas ajustables
    tension_ajustable: NumericRange | None = Field(
        default=None, description="Rango de tensión ajustable (V)"
    )
    corriente_ajustable: NumericRange | None = Field(
        default=None, description="Rango de corriente ajustable (A)"
    )


class ModosCarga(BaseModel):
    """Modos de carga disponibles."""

    model_config = ConfigDict(extra="forbid")

    manual_automatico: str | None = Field(
        default=None, description="Modo de operación: manual/automático"
    )
    carga_excepcional: bool | None = Field(
        default=None, description="Disponibilidad de carga excepcional"
    )


class RangoTensionPorQuimica(BaseModel):
    """Rangos de tensión por química de batería."""

    model_config = ConfigDict(extra="forbid")

    nicd: NumericRange | None = Field(default=None, description="Rango de tensión para Ni-Cd (V)")
    pb_ca: NumericRange | None = Field(default=None, description="Rango de tensión para Pb-Ca (V)")


class CargaBaterias(BaseModel):
    """Especificaciones de carga de baterías."""

    model_config = ConfigDict(extra="forbid")

    tension_flote: NumericRange | None = Field(
        default=None, description="Tensión de flote (rango de ajuste, V)"
    )
    estabilizacion_tension_flote: str | None = Field(
        default=None, description="Estabilización de tensión de flote (ej., ±1%)"
    )
    tension_fondo: NumericRange | None = Field(
        default=None, description="Tensión de fondo (rango de ajuste, V)"
    )
    modos_carga: ModosCarga | None = None
    regulador_diodos: bool | None = Field(
        default=None, description="Regulación mediante cadena de diodos"
    )
    rango_tension_salida_consumo: RangoTensionPorQuimica | None = Field(
        default=None, description="Rango de tensión de salida a consumo por química"
    )
    deteccion_polo_tierra: bool | None = Field(
        default=None, description="Detección de polo a tierra"
    )
    interruptor_salida_consumo: InterruptorSpec | None = Field(
        default=None, description="Interruptor de salida a consumo"
    )
    interruptor_salida_baterias: InterruptorSpec | None = Field(
        default=None, description="Interruptor de salida a baterías"
    )
    sistema_rectificacion: str | None = Field(
        default=None, description="Tecnología del rectificador"
    )
    ripple_con_baterias: str | None = Field(
        default=None, description="Nivel de rizado con baterías (mVpp o %)"
    )
    ripple_sin_baterias: str | None = Field(
        default=None, description="Nivel de rizado sin baterías (mVpp o %)"
    )


class GabineteExtraccion(BaseModel):
    """Especificaciones del gabinete (extracción)."""

    model_config = ConfigDict(extra="forbid")

    material: str | None = None
    acceso: str | None = Field(default=None, description="Acceso: frontal/lateral/trasero")
    grado_proteccion: str | None = Field(default=None, description="IP/NEMA")
    espesor_chapa_estructura_mm: Decimal | None = Field(
        default=None, description="Espesor de chapa (mm)"
    )
    tipo_pintura: str | None = None
    color: str | None = Field(default=None, description="Código RAL u otro")
    espesor_pintura_micras: Decimal | None = Field(
        default=None, description="Espesor de pintura (μm)"
    )
    dimensiones: Dimensiones | None = Field(default=None, description="Dimensiones (mm)")


class Otros(BaseModel):
    """Otras características."""

    model_config = ConfigDict(extra="forbid")

    ventilacion: str | None = Field(default=None, description="Natural/forzada")
    rectificador: str | None = Field(
        default=None, description="Topología o modelo del rectificador"
    )


class Protecciones(BaseModel):
    """Protecciones eléctricas."""

    model_config = ConfigDict(extra="forbid")

    sobretensiones_cc: bool | None = Field(
        default=None, description="Protección contra sobretensiones en CC"
    )
    sobretensiones_ca: bool | None = Field(
        default=None, description="Protección contra sobretensiones en CA"
    )
    cortocircuito: bool | None = Field(default=None, description="Protección contra cortocircuito")
    sobrecarga: bool | None = Field(default=None, description="Protección contra sobrecarga")
    lvd: bool | None = Field(default=None, description="Desconexión por baja tensión (LVD)")


class Alarmas(BaseModel):
    """Alarmas del sistema."""

    model_config = ConfigDict(extra="forbid")

    falla_red: bool | None = None
    alta_tension_baterias: bool | None = None
    baja_tension_baterias: bool | None = None
    tension_baterias_critica: bool | None = Field(default=None, description="Batería descargada")
    alta_tension_consumos: bool | None = None
    baja_tension_consumos: bool | None = None
    tension_consumo_critica: bool | None = None
    falla_rectificador: bool | None = None
    alta_corriente_rectificador: bool | None = None
    alta_corriente_baterias: bool | None = None
    alta_corriente_consumos: bool | None = None
    polo_positivo_tierra: bool | None = None
    polo_negativo_tierra: bool | None = None
    fallo_ventilador: bool | None = Field(default=None, description="Si corresponde")
    obstruccion_filtros: bool | None = Field(default=None, description="Si corresponde")
    bateria_en_descarga: bool | None = None
    averia_red_salida: bool | None = Field(default=None, description="Falla de aislación")
    apertura_interruptores: bool | None = None
    fallo_bateria_supervision: bool | None = Field(
        default=None, description="Si hay sistema de supervisión"
    )
    temperatura_termostato: bool | None = None
    cargador_modo_fondo: bool | None = None


class Senalizaciones(BaseModel):
    """Señalizaciones del sistema."""

    model_config = ConfigDict(extra="forbid")

    red_ok: bool | None = Field(default=None, description="Presencia de tensión alterna en redes")
    bateria_carga_flotacion: bool | None = None
    bateria_carga_rapida: bool | None = None
    bateria_carga_excepcional: bool | None = None
    ventiladores_funcionando: bool | None = Field(default=None, description="Si aplica")
    carga_por_red_alternativa: bool | None = None
    falla: bool | None = None
    tension_bateria: bool | None = None
    tension_consumos: bool | None = None
    corriente_baterias: bool | None = None
    corriente_consumos: bool | None = None
    alarmas_discriminadas: bool | None = None


class AparatosDeMedidaExtraccion(BaseModel):
    """Aparatos de medida (extracción)."""

    model_config = ConfigDict(extra="forbid")

    unidad_digital_centralizada: bool | None = None
    protocolo_comunicacion: str | None = None
    puerto_comunicacion: str | None = None
    mide_corrientes_entrada: bool | None = None
    mide_tensiones_entrada: bool | None = None
    mide_corriente_salida_rectificador: bool | None = None
    mide_corriente_carga_baterias: bool | None = None
    mide_tension_salida_rectificador: bool | None = None
    mide_tension_baterias: bool | None = None
    mide_tension_consumos: bool | None = None
    mide_corriente_descarga_baterias: bool | None = None


class ResistenciasCalefactoras(BaseModel):
    """Resistencias calefactoras."""

    model_config = ConfigDict(extra="forbid")

    tension_alimentacion_v: Decimal | None = Field(default=None, description="V")
    potencia_w: Decimal | None = Field(default=None, description="W")
    llave_termomagnetica_independiente: bool | None = Field(
        default=None, description="Llave dedicada"
    )
    alimentacion: AlimentacionAlternativaTipo | None = Field(
        default=None, description="Interna o externa"
    )


class CablesPotenciaAuxiliares(BaseModel):
    """Cables de potencia auxiliares."""

    model_config = ConfigDict(extra="forbid")

    tension_aislacion_v: Decimal | None = Field(
        default=None, description="Tensión de aislación (V)"
    )
    material: str | None = None
    baja_emision_halogenos: bool | None = None


class CaracteristicasAccesoriosAuxiliares(BaseModel):
    """Características de accesorios auxiliares."""

    model_config = ConfigDict(extra="forbid")

    panel_control: str | None = Field(default=None, description="Ajuste y configuración")
    resistencias_calefactoras: ResistenciasCalefactoras | None = None
    cables_potencia_auxiliares: CablesPotenciaAuxiliares | None = None
    bornes_reserva: int | None = Field(default=None, description="Cantidad de bornes de reserva")
    nivel_ruido_db_a: Decimal | None = Field(
        default=None, description="Nivel de ruido a 1 m y 100% carga (dB(A))"
    )
    placas_identificacion: bool | None = None
    chapa_caracteristicas: bool | None = None


class InspeccionesEnsayos(BaseModel):
    """Inspecciones y ensayos."""

    model_config = ConfigDict(extra="forbid")

    resistencia_aislacion: bool | None = Field(
        default=None, description="Medición de resistencia de aislación"
    )
    ensayo_dieletrico: bool | None = Field(
        default=None, description="Ensayo dieléctrico de potencia/control"
    )
    resistencia_aislacion_post: bool | None = Field(
        default=None, description="Medición posterior al ensayo dieléctrico"
    )
    elementos_mecanicos_enclavamientos: bool | None = Field(
        default=None, description="Funcionamiento y enclavamientos"
    )
    tolerancia_tension_salida: bool | None = None
    nivel_rizado: bool | None = None
    verificacion_valores_salida_control: bool | None = Field(
        default=None, description="Verificación eléctrica en condiciones de carga"
    )
    verificacion_tensiones_carga: bool | None = Field(
        default=None, description="Verifica flote/rápida/excepcional"
    )
    variacion_tension_alimentacion: bool | None = Field(
        default=None, description="No varía en límites de alimentación"
    )
    variacion_carga_0_a_100: bool | None = Field(
        default=None, description="No varía del 0% al 100% de carga"
    )
    verificacion_carga_bateria: bool | None = None
    contenido_armonicos_alimentacion: bool | None = None
    ensayo_plena_carga_48h: bool | None = Field(
        default=None, description="Ensayo a plena carga hasta régimen estable"
    )
    ensayo_rendimiento: bool | None = None
    reparto_intensidades_paralelo: bool | None = Field(
        default=None, description="Para cargadores en paralelo"
    )
    prueba_senalizacion_alarma: bool | None = None
    prueba_funcional_total: bool | None = Field(
        default=None, description="Todas las condiciones de operación"
    )
    capacidad_corriente_cortocircuito: bool | None = Field(
        default=None, description="Capacidad para abrir el mayor interruptor de salida"
    )


class GarantiaExtraccion(BaseModel):
    """Garantía (extracción)."""

    model_config = ConfigDict(extra="forbid")

    descripcion: str | None = Field(default=None, description="Términos de garantía")
    meses: int | None = Field(default=None, description="Duración en meses")


# ============================================
# MODELO PRINCIPAL DE EXTRACCIÓN
# ============================================


class SistemaCargadorRectificador(BaseModel):
    """Esquema completo del sistema cargador/rectificador + baterías."""

    model_config = ConfigDict(extra="forbid")

    generales: Generales | None = None
    condiciones_ambientales: CondicionesAmbientales | None = None
    alimentacion: AlimentacionExtraccion | None = None
    salida: SalidaExtraccion | None = None
    carga_baterias: CargaBaterias | None = None
    gabinete: GabineteExtraccion | None = None
    otros: Otros | None = None
    protecciones: Protecciones | None = None
    alarmas: Alarmas | None = None
    senalizaciones: Senalizaciones | None = None
    aparatos_medida: AparatosDeMedidaExtraccion | None = None
    caracteristicas_accesorios: CaracteristicasAccesoriosAuxiliares | None = None
    inspecciones_ensayos: InspeccionesEnsayos | None = None
    garantia: GarantiaExtraccion | None = None


# ============================================
# MODELOS PARA LICITACIÓN CON MÚLTIPLES ITEMS
# ============================================


class ItemLicitado(BaseModel):
    """Representa un item individual dentro de la licitación."""

    model_config = ConfigDict(extra="forbid")

    numero_item: int | None = Field(
        default=None, description="Número de ítem en la licitación (1, 2, 3, 4, etc.)"
    )
    cantidad: int | None = Field(default=None, description="Cantidad requerida de unidades")
    descripcion: str | None = Field(default=None, description="Descripción del item")

    # Especificaciones específicas que varían por item
    alimentacion: AlimentacionExtraccion | None = Field(
        default=None, description="Alimentación específica de este item"
    )
    salida: SalidaExtraccion | None = Field(
        default=None, description="Salida específica de este item"
    )
    sistema_control: str | None = Field(default=None, description="Sistema de control específico")

    # Marca y modelo si se especifican por item
    marca: str | None = None
    modelo: str | None = None


class LicitacionCompleta(BaseModel):
    """Esquema para licitaciones con múltiples items y especificaciones comunes."""

    model_config = ConfigDict(extra="forbid")

    # Especificaciones comunes a todos los items
    especificaciones_comunes: SistemaCargadorRectificador | None = Field(
        default=None,
        description="Especificaciones técnicas que aplican a todos los items de la licitación",
    )

    # Lista de items individuales
    items: list[ItemLicitado] = Field(
        default_factory=list,
        description="Lista de items individuales licitados con sus especificaciones particulares",
    )
