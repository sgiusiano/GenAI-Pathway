"""Carga el catálogo de productos desde archivos CSV."""

import json
import re
from pathlib import Path

import pandas as pd

from licitaciones.db.connection import DatabaseConnection
from licitaciones.logger import get_logger

logger = get_logger(__name__)

# Directorio default para CSVs del catálogo
DEFAULT_CATALOG_DIR = Path(__file__).parent.parent.parent.parent / "data" / "catalog"


def limpiar_valor(valor: object) -> object:
    """Limpia y convierte valores del CSV."""
    if pd.isna(valor) or valor == "" or valor == "N/A":
        return None
    if isinstance(valor, str):
        valor_lower = valor.strip().lower()
        # Detectar booleanos por prefijo (ej: "Sí (texto adicional)")
        if valor_lower.startswith(("sí", "si", "yes")):
            return True
        if valor_lower.startswith("no"):
            return False
    return valor


def extraer_numero(texto: object) -> float | None:
    """Extrae el primer número de un texto."""
    if pd.isna(texto):
        return None
    match = re.search(r"(\d+\.?\d*)", str(texto))
    return float(match.group(1)) if match else None


def extraer_rango(texto: object) -> tuple[float | None, float | None]:
    """Extrae valores min y max de un rango como '55.0-143.0'."""
    if pd.isna(texto):
        return None, None
    match = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", str(texto))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None


def extraer_dimensiones(texto: object) -> tuple[int | None, int | None, int | None]:
    """Extrae dimensiones del formato 'ancho x alto x profundidad'."""
    if pd.isna(texto):
        return None, None, None
    match = re.search(r"(\d+)\s*x\s*(\d+)\s*x\s*(\d+)", str(texto))
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return None, None, None


def procesar_csv(archivo_csv: Path, db: DatabaseConnection) -> int:
    """Procesa un archivo CSV de productos.

    Args:
        archivo_csv: Ruta al archivo CSV.
        db: Conexión a la base de datos.

    Returns:
        Número de productos cargados.
    """
    logger.info("Procesando %s...", archivo_csv.name)

    df = pd.read_csv(archivo_csv, encoding="utf-8")
    columnas_productos = df.columns[3:]
    productos_cargados = 0

    for col in columnas_productos:
        producto_data = {}
        for _, row in df.iterrows():
            item = row["ítem"]
            valor = limpiar_valor(row[col])
            producto_data[item] = valor

        try:
            codigo = producto_data.get("1.1")
            if not codigo:
                continue

            match = re.search(r"(\d+)-(\d+)", str(codigo))
            if not match:
                logger.warning("No se pudo extraer tensión/corriente: %s", codigo)
                continue

            tension_nominal = int(match.group(1))
            corriente_nominal = int(match.group(2))

            regulador_diodos = None
            if "CS" in str(codigo):
                regulador_diodos = "CS"
            elif "CD" in str(codigo):
                regulador_diodos = "CD"

            with db.get_cursor() as cur:
                # 1. Producto
                cur.execute(
                    """
                    INSERT INTO productos (codigo, marca, modelo, tension_nominal,
                                          corriente_nominal, regulador_diodos, origen, tipo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        codigo,
                        producto_data.get("1.2") or "SERVELEC",
                        producto_data.get("1.3") or codigo,
                        tension_nominal,
                        corriente_nominal,
                        regulador_diodos,
                        producto_data.get("1.5") or "Argentina",
                        producto_data.get("1.6") or "Autorregulado",
                    ),
                )
                producto_id = cur.fetchone()[0]

                # 2. Especificaciones
                flote_min, flote_max = extraer_rango(producto_data.get("5"))
                fondo_min, fondo_max = extraer_rango(producto_data.get("5.2"))

                cur.execute(
                    """
                    INSERT INTO especificaciones (
                        producto_id, normas_fabricacion, apto_pb_ac, apto_ni_cd,
                        temperatura_maxima, temperatura_minima, altura_snm, humedad_relativa_max,
                        tipo_instalacion, tipo_servicio, ventilacion, tipo_rectificador,
                        nivel_ruido, proteccion_sobretension, proteccion_cortocircuito,
                        proteccion_sobrecarga, ripple_con_baterias, ripple_sin_baterias,
                        tension_flote_min, tension_flote_max, tension_fondo_min, tension_fondo_max,
                        modo_manual_automatico, modo_carga_excepcional,
                        regulador_diodos_carga, deteccion_polo_tierra
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                              %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        producto_id,
                        producto_data.get("1.4"),
                        limpiar_valor(producto_data.get("1.7")),
                        limpiar_valor(producto_data.get("1.7")),
                        extraer_numero(producto_data.get("2.1")),
                        extraer_numero(producto_data.get("2.2")),
                        extraer_numero(producto_data.get("2.3")),
                        extraer_numero(producto_data.get("2.4")),
                        producto_data.get("2.5"),
                        producto_data.get("2.6"),
                        producto_data.get("7.1"),
                        producto_data.get("7.2"),
                        producto_data.get("12.5"),
                        producto_data.get("8.1"),
                        producto_data.get("8.2"),
                        producto_data.get("8.3"),
                        producto_data.get("5.7.2001"),
                        producto_data.get("5.7.2002"),
                        flote_min,
                        flote_max,
                        fondo_min,
                        fondo_max,
                        limpiar_valor(producto_data.get("5.3.2001")),
                        limpiar_valor(producto_data.get("5.3.2002")),
                        producto_data.get("5.4"),
                        limpiar_valor(producto_data.get("5.3")),
                    ),
                )

                # 3. Alimentación
                cur.execute(
                    """
                    INSERT INTO alimentacion (
                        producto_id, tipo, tension, rango_tension, frecuencia, rango_frecuencia,
                        conexion_neutro, conductor_pe_independiente, corriente_cortocircuito,
                        tipo_interruptor_acometida, potencia_transformador, corriente_conexion_transformador
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        producto_id,
                        producto_data.get("3.1"),
                        producto_data.get("3.2"),
                        producto_data.get("3.3"),
                        extraer_numero(producto_data.get("3.4")),
                        producto_data.get("3.5"),
                        producto_data.get("3.5.2001"),
                        limpiar_valor(producto_data.get("3.5.2002")),
                        producto_data.get("3.5.2003"),
                        producto_data.get("3.5.2004"),
                        producto_data.get("3.5.2005"),
                        producto_data.get("3.5.5.1"),
                    ),
                )

                # 4. Salida
                cur.execute(
                    """
                    INSERT INTO salida (
                        producto_id, tension_nominal, corriente_nominal, maxima_corriente_consumos,
                        tipo_interruptor_consumo, tipo_interruptor_baterias, sistema_rectificacion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        producto_id,
                        extraer_numero(producto_data.get("4.1")),
                        extraer_numero(producto_data.get("4.2")),
                        extraer_numero(producto_data.get("4.3")),
                        producto_data.get("5.4"),
                        producto_data.get("5.5"),
                        producto_data.get("5.6"),
                    ),
                )

                # 5. Gabinete
                ancho, alto, profundidad = extraer_dimensiones(producto_data.get("6.8"))
                cur.execute(
                    """
                    INSERT INTO gabinete (
                        producto_id, material, acceso, grado_proteccion, espesor_chapa,
                        tipo_pintura, color, espesor_pintura, ancho, alto, profundidad
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        producto_id,
                        producto_data.get("6.1"),
                        producto_data.get("6.2"),
                        producto_data.get("6.3"),
                        extraer_numero(producto_data.get("6.4")),
                        producto_data.get("6.5"),
                        producto_data.get("6.6"),
                        extraer_numero(producto_data.get("6.7")),
                        ancho,
                        alto,
                        profundidad,
                    ),
                )

                # 6. Aparatos de medida
                mediciones = {
                    k: v
                    for k, v in {
                        "corriente_entrada": producto_data.get("11.4"),
                        "tension_entrada": producto_data.get("11.5"),
                        "corriente_rectificador": producto_data.get("11.6"),
                        "corriente_baterias": producto_data.get("11.7"),
                        "tension_rectificador": producto_data.get("11.8"),
                        "tension_baterias": producto_data.get("11.9"),
                        "tension_consumos": producto_data.get("11.10"),
                        "corriente_descarga": producto_data.get("11.11"),
                    }.items()
                    if v is not None
                }

                cur.execute(
                    """
                    INSERT INTO aparatos_medida (
                        producto_id, unidad_digital_centralizada, protocolo_comunicacion,
                        puerto_comunicacion, medicion
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        producto_id,
                        limpiar_valor(producto_data.get("11.1")),
                        producto_data.get("11.2"),
                        producto_data.get("11.3"),
                        json.dumps(mediciones) if mediciones else None,
                    ),
                )

                # 7. Accesorios
                cur.execute(
                    """
                    INSERT INTO accesorios (
                        producto_id, panel_control, resistencias_calefactoras, tension_resistencias,
                        potencia_resistencias, cables_incluidos, tension_aislacion_cables,
                        material_cables, baja_emision_halogenos, bornes_reserva,
                        placas_identificacion, chapa_caracteristicas
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        producto_id,
                        producto_data.get("12.1"),
                        producto_data.get("12.2"),  # VARCHAR, no convertir a boolean
                        extraer_numero(producto_data.get("12.2.2001")),
                        producto_data.get("12.2.2002"),
                        producto_data.get("12.3"),  # VARCHAR, no convertir a boolean
                        producto_data.get("12.3.2001"),
                        producto_data.get("12.3.2002"),
                        limpiar_valor(producto_data.get("12.3.2003")),
                        limpiar_valor(producto_data.get("12.4")),
                        limpiar_valor(producto_data.get("12.6")),
                        limpiar_valor(producto_data.get("12.7")),
                    ),
                )

                # 8. Garantía
                cur.execute(
                    """
                    INSERT INTO garantia (producto_id, meses)
                    VALUES (%s, %s)
                    """,
                    (producto_id, extraer_numero(producto_data.get("14")) or 24),
                )

            productos_cargados += 1
            logger.debug("Producto %s cargado", codigo)

        except Exception as e:
            logger.error("Error procesando %s: %s", col, e)
            continue

    return productos_cargados


def load_catalog(db: DatabaseConnection, csv_dir: Path | None = None) -> int:
    """Carga el catálogo completo desde los archivos CSV.

    Args:
        db: Conexión a la base de datos.
        csv_dir: Directorio con los CSVs. Si no se especifica, usa el default.

    Returns:
        Total de productos cargados.
    """
    if csv_dir is None:
        csv_dir = DEFAULT_CATALOG_DIR

    if not csv_dir.exists():
        logger.error("Directorio de catálogo no encontrado: %s", csv_dir)
        return 0

    archivos = ["RDT_productos.csv", "RCTI_productos.csv", "RCMI_productos.csv"]
    archivos_encontrados = [csv_dir / a for a in archivos if (csv_dir / a).exists()]

    if not archivos_encontrados:
        logger.warning("No se encontraron archivos CSV en: %s", csv_dir)
        return 0

    total = 0
    for archivo in archivos_encontrados:
        try:
            total += procesar_csv(archivo, db)
        except Exception as e:
            logger.error("Error procesando %s: %s", archivo.name, e)

    logger.info("Catálogo cargado: %d productos", total)
    return total
