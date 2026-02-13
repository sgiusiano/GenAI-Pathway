import os
import re

import pandas as pd
import psycopg2

# Configuración de conexión a la base de datos
DB_CONFIG = {
    'dbname': 'catalogo_servelec',
    'user': 'postgres',
    'password': 'Postgres.22',
    'host': 'localhost',
    'port': 5432
}

def limpiar_valor(valor):
    """Limpia y convierte valores del CSV"""
    if pd.isna(valor) or valor == '' or valor == 'N/A':
        return None
    if isinstance(valor, str):
        valor_lower = valor.strip().lower()
        # Detectar "Sí" o "Si" incluso si viene con otro texto
        if 'sí' in valor_lower or valor_lower.startswith('si ') or valor_lower == 'si' or 'yes' in valor_lower:
            return True
        # Detectar "No" al inicio de la cadena o como palabra completa
        if valor_lower.startswith('no ') or valor_lower == 'no':
            return False
    return valor

def extraer_numero(texto):
    """Extrae el primer número de un texto"""
    if pd.isna(texto):
        return None
    match = re.search(r'(\d+\.?\d*)', str(texto))
    return float(match.group(1)) if match else None

def extraer_rango(texto):
    """Extrae valores min y max de un rango como '55.0-143.0'"""
    if pd.isna(texto):
        return None, None
    match = re.search(r'(\d+\.?\d*)\s*-\s*(\d+\.?\d*)', str(texto))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

def extraer_dimensiones(texto):
    """Extrae dimensiones del formato 'ancho x alto x profundidad'"""
    if pd.isna(texto):
        return None, None, None
    match = re.search(r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)', str(texto))
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return None, None, None

def procesar_csv_rdt(archivo_csv, conn):
    """Procesa el CSV de productos RDT"""
    print(f"Procesando {archivo_csv}...")

    # Leer CSV
    df = pd.read_csv(archivo_csv, encoding='utf-8')

    # Obtener los nombres de las columnas de productos (desde la 4ta columna en adelante)
    columnas_productos = df.columns[3:]

    cur = conn.cursor()

    for col in columnas_productos:
        print(f"  Procesando producto: {col}")

        # Crear diccionario con los datos del producto
        producto_data = {}
        for idx, row in df.iterrows():
            item = row['ítem']
            valor = row[col]
            producto_data[item] = valor

        try:
            # 1. Insertar producto principal
            codigo = limpiar_valor(producto_data.get('1.1'))
            marca = limpiar_valor(producto_data.get('1.2'))
            modelo = limpiar_valor(producto_data.get('1.3'))

            # Extraer tensión y corriente del código (ej: RDT-110-15)
            match = re.search(r'(\d+)-(\d+)', str(codigo))
            if match:
                tension_nominal = int(match.group(1))
                corriente_nominal = int(match.group(2))
            else:
                continue

            # Determinar regulador_diodos
            regulador_diodos = None
            if 'CS' in str(codigo):
                regulador_diodos = 'CS'
            elif 'CD' in str(codigo):
                regulador_diodos = 'CD'

            cur.execute("""
                INSERT INTO productos (codigo, marca, modelo, tension_nominal, corriente_nominal, regulador_diodos, origen, tipo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (codigo, marca, modelo, tension_nominal, corriente_nominal, regulador_diodos,
                  limpiar_valor(producto_data.get('1.5')), limpiar_valor(producto_data.get('1.6'))))

            producto_id = cur.fetchone()[0]

            # 2. Insertar especificaciones
            flote_min, flote_max = extraer_rango(producto_data.get('5'))
            fondo_min, fondo_max = extraer_rango(producto_data.get('5.2'))

            cur.execute("""
                INSERT INTO especificaciones (
                    producto_id, normas_fabricacion, apto_pb_ac, apto_ni_cd,
                    temperatura_maxima, temperatura_minima, altura_snm, humedad_relativa_max,
                    tipo_instalacion, tipo_servicio, ventilacion, tipo_rectificador,
                    nivel_ruido, rendimiento_minimo,
                    proteccion_sobretension, proteccion_cortocircuito, proteccion_sobrecarga,
                    ripple_con_baterias, ripple_sin_baterias,
                    tension_flote_min, tension_flote_max, tension_fondo_min, tension_fondo_max,
                    modo_manual_automatico, modo_carga_excepcional,
                    regulador_diodos_carga, deteccion_polo_tierra
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                producto_id,
                limpiar_valor(producto_data.get('1.4')),  # normas_fabricacion
                limpiar_valor(producto_data.get('1.7')),  # apto_pb_ac (BOOLEAN)
                limpiar_valor(producto_data.get('1.8')),  # apto_ni_cd (BOOLEAN) - Corregido
                extraer_numero(producto_data.get('2.1')),  # temperatura_maxima
                extraer_numero(producto_data.get('2.2')),  # temperatura_minima
                extraer_numero(producto_data.get('2.3')),  # altura_snm
                extraer_numero(producto_data.get('2.4')),  # humedad_relativa_max
                limpiar_valor(producto_data.get('2.5')),  # tipo_instalacion
                limpiar_valor(producto_data.get('2.6')),  # tipo_servicio
                limpiar_valor(producto_data.get('7.1')),  # ventilacion
                limpiar_valor(producto_data.get('7.2')),  # tipo_rectificador
                limpiar_valor(producto_data.get('12.5')),  # nivel_ruido
                None,  # rendimiento_minimo (no especificado en RDT)
                limpiar_valor(producto_data.get('8.1')),  # proteccion_sobretension
                limpiar_valor(producto_data.get('8.2')),  # proteccion_cortocircuito
                limpiar_valor(producto_data.get('8.3')),  # proteccion_sobrecarga
                limpiar_valor(producto_data.get('5.7.2001')),  # ripple_con_baterias
                limpiar_valor(producto_data.get('5.7.2002')),  # ripple_sin_baterias
                flote_min, flote_max, fondo_min, fondo_max,
                limpiar_valor(producto_data.get('5.3.2001')),  # modo_manual_automatico (BOOLEAN)
                limpiar_valor(producto_data.get('5.3.2002')),  # modo_carga_excepcional (BOOLEAN)
                limpiar_valor(producto_data.get('5.4')),  # regulador_diodos_carga
                limpiar_valor(producto_data.get('5.3'))  # deteccion_polo_tierra (BOOLEAN)
            ))

            # 3. Insertar alimentación
            cur.execute("""
                INSERT INTO alimentacion (
                    producto_id, tipo, tension, rango_tension, frecuencia, rango_frecuencia,
                    conexion_neutro, conductor_pe_independiente, corriente_cortocircuito,
                    tipo_interruptor_acometida, potencia_transformador, corriente_conexion_transformador
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                producto_id,
                limpiar_valor(producto_data.get('3.1')),  # tipo
                limpiar_valor(producto_data.get('3.2')),  # tension
                limpiar_valor(producto_data.get('3.3')),  # rango_tension
                extraer_numero(producto_data.get('3.4')),  # frecuencia
                limpiar_valor(producto_data.get('3.5')),  # rango_frecuencia
                limpiar_valor(producto_data.get('3.5.2001')),  # conexion_neutro
                limpiar_valor(producto_data.get('3.5.2002')),  # conductor_pe_independiente (BOOLEAN)
                limpiar_valor(producto_data.get('3.5.2003')),  # corriente_cortocircuito
                limpiar_valor(producto_data.get('3.5.2004')),  # tipo_interruptor_acometida
                limpiar_valor(producto_data.get('3.5.2005')),  # potencia_transformador
                limpiar_valor(producto_data.get('3.5.5.1'))  # corriente_conexion_transformador
            ))

            # 4. Insertar salida
            cur.execute("""
                INSERT INTO salida (
                    producto_id, tension_nominal, corriente_nominal, maxima_corriente_consumos,
                    tipo_interruptor_consumo, tipo_interruptor_baterias, sistema_rectificacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                producto_id,
                extraer_numero(producto_data.get('4.1')),  # tension_nominal
                extraer_numero(producto_data.get('4.2')),  # corriente_nominal
                extraer_numero(producto_data.get('4.3')),  # maxima_corriente_consumos
                limpiar_valor(producto_data.get('5.4')),  # tipo_interruptor_consumo
                limpiar_valor(producto_data.get('5.5')),  # tipo_interruptor_baterias
                limpiar_valor(producto_data.get('5.6'))  # sistema_rectificacion
            ))

            # 5. Insertar gabinete
            ancho, alto, profundidad = extraer_dimensiones(producto_data.get('6.8'))

            cur.execute("""
                INSERT INTO gabinete (
                    producto_id, material, acceso, grado_proteccion, espesor_chapa,
                    tipo_pintura, color, espesor_pintura, ancho, alto, profundidad, peso
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                producto_id,
                limpiar_valor(producto_data.get('6.1')),  # material
                limpiar_valor(producto_data.get('6.2')),  # acceso
                limpiar_valor(producto_data.get('6.3')),  # grado_proteccion
                extraer_numero(producto_data.get('6.4')),  # espesor_chapa
                limpiar_valor(producto_data.get('6.5')),  # tipo_pintura
                limpiar_valor(producto_data.get('6.6')),  # color
                extraer_numero(producto_data.get('6.7')),  # espesor_pintura
                ancho, alto, profundidad,
                None  # peso (no especificado en RDT)
            ))

            # 6. Insertar aparatos_medida
            mediciones = {
                'corriente_entrada': limpiar_valor(producto_data.get('11.4')),
                'tension_entrada': limpiar_valor(producto_data.get('11.5')),
                'corriente_rectificador': limpiar_valor(producto_data.get('11.6')),
                'corriente_baterias': limpiar_valor(producto_data.get('11.7')),
                'tension_rectificador': limpiar_valor(producto_data.get('11.8')),
                'tension_baterias': limpiar_valor(producto_data.get('11.9')),
                'tension_consumos': limpiar_valor(producto_data.get('11.10')),
                'corriente_descarga': limpiar_valor(producto_data.get('11.11'))
            }

            import json
            cur.execute("""
                INSERT INTO aparatos_medida (
                    producto_id, unidad_digital_centralizada, protocolo_comunicacion,
                    puerto_comunicacion, medicion
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                producto_id,
                limpiar_valor(producto_data.get('11.1')),  # unidad_digital_centralizada (BOOLEAN)
                limpiar_valor(producto_data.get('11.2')),  # protocolo_comunicacion
                limpiar_valor(producto_data.get('11.3')),  # puerto_comunicacion
                json.dumps(mediciones)  # medicion
            ))

            # 7. Insertar accesorios
            cur.execute("""
                INSERT INTO accesorios (
                    producto_id, panel_control, resistencias_calefactoras, tension_resistencias,
                    potencia_resistencias, cables_incluidos, tension_aislacion_cables,
                    material_cables, baja_emision_halogenos, bornes_reserva,
                    placas_identificacion, chapa_caracteristicas
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                producto_id,
                limpiar_valor(producto_data.get('12.1')),  # panel_control
                limpiar_valor(producto_data.get('12.2')),  # resistencias_calefactoras (BOOLEAN)
                extraer_numero(producto_data.get('12.2.2001')),  # tension_resistencias
                limpiar_valor(producto_data.get('12.2.2002')),  # potencia_resistencias
                limpiar_valor(producto_data.get('12.3')),  # cables_incluidos (BOOLEAN)
                limpiar_valor(producto_data.get('12.3.2001')),  # tension_aislacion_cables
                limpiar_valor(producto_data.get('12.3.2002')),  # material_cables
                limpiar_valor(producto_data.get('12.3.2003')),  # baja_emision_halogenos (BOOLEAN)
                limpiar_valor(producto_data.get('12.4')),  # bornes_reserva (BOOLEAN)
                limpiar_valor(producto_data.get('12.6')),  # placas_identificacion (BOOLEAN)
                limpiar_valor(producto_data.get('12.7'))  # chapa_caracteristicas (BOOLEAN)
            ))

            # 8. Insertar garantía
            cur.execute("""
                INSERT INTO garantia (producto_id, meses)
                VALUES (%s, %s)
            """, (producto_id, extraer_numero(producto_data.get('14'))))

            conn.commit()
            print(f"    ✓ Producto {codigo} cargado exitosamente")

        except Exception as e:
            conn.rollback()
            print(f"    ✗ Error procesando {col}: {str(e)}")
            continue

    cur.close()

def main():
    """Función principal"""
    try:
        # Conectar a la base de datos
        print(DB_CONFIG)

        conn = psycopg2.connect(**DB_CONFIG)
        print("Conexión exitosa a la base de datos\n")

        # Procesar cada archivo CSV
        archivos = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'catalog', 'RCMI_productos.csv'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'catalog', 'RCTI_productos.csv'),
            os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'catalog', 'RDT_productos.csv')
        ]

        for archivo in archivos:
            try:
                procesar_csv_rdt(archivo, conn)
                print(f"✓ Archivo {archivo} procesado completamente\n")
            except FileNotFoundError:
                print(f"✗ Archivo {archivo} no encontrado\n")
            except Exception as e:
                print(f"✗ Error procesando {archivo}: {str(e)}\n")

        conn.close()
        print("Proceso completado")

    except Exception as e:
        print(f"Error de conexión: {str(e)}")

if __name__ == "__main__":
    main()