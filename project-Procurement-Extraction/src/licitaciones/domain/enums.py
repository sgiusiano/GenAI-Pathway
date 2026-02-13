"""Enumeraciones compartidas para el sistema de licitaciones."""

from enum import Enum


class FaseTipo(str, Enum):
    """Tipo de fase eléctrica."""

    MONOFASICA = "monofásica"
    BIFASICA = "bifásica"
    TRIFASICA = "trifásica"


class ConexionNeutroTierra(str, Enum):
    """Esquema de conexión a tierra."""

    TT = "TT"
    TN = "TN"
    IT = "IT"
    OTRO = "otro"


class ServicioTipo(str, Enum):
    """Tipo de servicio."""

    CONTINUO = "continuo"
    INTERMITENTE = "intermitente"
    OTRO = "otro"


class AlimentacionAlternativaTipo(str, Enum):
    """Tipo de alimentación alternativa."""

    INTERNA = "interna"
    EXTERNA = "externa"


class ReguladorDiodosTipo(str, Enum):
    """Tipo de regulador de diodos."""

    CS = "CS"  # Cadena Simple
    CD = "CD"  # Cadena Doble


# Códigos de alarma predefinidos (mapeo a tipos_alarma)
class CodigoAlarma(str, Enum):
    """Códigos de alarma predefinidos."""

    FALLA_RED = "FALLA_RED"
    ALTA_TENSION_BAT = "ALTA_TENSION_BAT"
    BAJA_TENSION_BAT = "BAJA_TENSION_BAT"
    TENSION_BAT_CRITICA = "TENSION_BAT_CRITICA"
    ALTA_TENSION_CONS = "ALTA_TENSION_CONS"
    BAJA_TENSION_CONS = "BAJA_TENSION_CONS"
    TENSION_CONS_CRITICA = "TENSION_CONS_CRITICA"
    FALLA_RECTIFICADOR = "FALLA_RECTIFICADOR"
    ALTA_CORRIENTE_RECT = "ALTA_CORRIENTE_RECT"
    ALTA_CORRIENTE_BAT = "ALTA_CORRIENTE_BAT"
    ALTA_CORRIENTE_CONS = "ALTA_CORRIENTE_CONS"
    POLO_POS_TIERRA = "POLO_POS_TIERRA"
    POLO_NEG_TIERRA = "POLO_NEG_TIERRA"
    FALLO_VENTILADOR = "FALLO_VENTILADOR"
    OBSTRUCCION_FILTROS = "OBSTRUCCION_FILTROS"
    BATERIA_DESCARGA = "BATERIA_DESCARGA"
    AVERIA_RED_SALIDA = "AVERIA_RED_SALIDA"
    APERTURA_INTERRUPTORES = "APERTURA_INTERRUPTORES"
    FALLO_BATERIA = "FALLO_BATERIA"
    TEMPERATURA = "TEMPERATURA"
    CARGADOR_MODO_FONDO = "CARGADOR_MODO_FONDO"


# Códigos de ensayo predefinidos (mapeo a tipos_ensayo)
class CodigoEnsayo(str, Enum):
    """Códigos de ensayo predefinidos."""

    RESIST_AISLACION = "RESIST_AISLACION"
    DIELECTRICO = "DIELECTRICO"
    RESIST_POST_DIELECTRICO = "RESIST_POST_DIELECTRICO"
    ELEMENTOS_MECANICOS = "ELEMENTOS_MECANICOS"
    TOLERANCIA_TENSION = "TOLERANCIA_TENSION"
    NIVEL_RIZADO = "NIVEL_RIZADO"
    VERIFICACION_ELECTRICA = "VERIFICACION_ELECTRICA"
    VERIFICACION_TENSIONES = "VERIFICACION_TENSIONES"
    VARIACION_TENSION_ALIM = "VARIACION_TENSION_ALIM"
    VARIACION_CARGA = "VARIACION_CARGA"
    CARGA_BATERIA = "CARGA_BATERIA"
    ARMONICOS = "ARMONICOS"
    PLENA_CARGA = "PLENA_CARGA"
    RENDIMIENTO = "RENDIMIENTO"
    REPARTO_INTENSIDADES = "REPARTO_INTENSIDADES"
    SENALIZACION_ALARMA = "SENALIZACION_ALARMA"
    FUNCIONAL_COMPLETO = "FUNCIONAL_COMPLETO"
    CORTOCIRCUITO = "CORTOCIRCUITO"
