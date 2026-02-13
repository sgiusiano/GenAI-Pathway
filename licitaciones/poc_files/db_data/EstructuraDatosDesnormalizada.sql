-- ============================================
-- Script de Creación de Base de Datos
-- Sistema de Gestión de Productos Rectificadores
-- ============================================

-- Conectar a la base de datos
-- catalogo_servelec

-- ============================================
-- TABLA PRINCIPAL: PRODUCTOS
-- ============================================
CREATE TABLE productos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    marca VARCHAR(100) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    tension_nominal INTEGER NOT NULL,
    corriente_nominal INTEGER NOT NULL,
    regulador_diodos VARCHAR(20), -- 'CS', 'CD', NULL
    origen VARCHAR(100) DEFAULT 'Argentina',
    tipo VARCHAR(100) DEFAULT 'Autorregulado',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para productos
CREATE INDEX idx_productos_codigo ON productos(codigo);
CREATE INDEX idx_productos_tension ON productos(tension_nominal);
CREATE INDEX idx_productos_corriente ON productos(corriente_nominal);
CREATE INDEX idx_productos_marca_modelo ON productos(marca, modelo);

-- Comentarios
COMMENT ON TABLE productos IS 'Tabla principal de productos rectificadores';
COMMENT ON COLUMN productos.regulador_diodos IS 'Tipo de regulador: CS (Cadena Simple), CD (Cadena Doble), o NULL';

-- ============================================
-- TABLA: ESPECIFICACIONES
-- ============================================
CREATE TABLE especificaciones (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    
    -- Generales
    normas_fabricacion TEXT,
    apto_pb_ac BOOLEAN DEFAULT TRUE,
    apto_ni_cd BOOLEAN DEFAULT TRUE,
    
    -- Condiciones ambientales
    temperatura_maxima DECIMAL(5,2),
    temperatura_minima DECIMAL(5,2),
    altura_snm INTEGER,
    humedad_relativa_max DECIMAL(5,2),
    tipo_instalacion VARCHAR(50),
    tipo_servicio VARCHAR(50),
    
    -- Características técnicas
    ventilacion VARCHAR(50),
    tipo_rectificador TEXT,
    nivel_ruido VARCHAR(10),
    rendimiento_minimo DECIMAL(5,2),
    
    -- Protecciones
    proteccion_sobretension TEXT,
    proteccion_cortocircuito TEXT,
    proteccion_sobrecarga TEXT,
    
    -- Ripple
    ripple_con_baterias VARCHAR(10),
    ripple_sin_baterias VARCHAR(10),
    
    -- Tensiones de carga
    tension_flote_min DECIMAL(6,2),
    tension_flote_max DECIMAL(6,2),
    tension_fondo_min DECIMAL(6,2),
    tension_fondo_max DECIMAL(6,2),
    
    -- Modos de operación
    modo_manual_automatico BOOLEAN,
    modo_carga_excepcional BOOLEAN,
    regulador_diodos_carga VARCHAR(50),
    rango_salida_nicd VARCHAR(50),
    rango_salida_pbca VARCHAR(50),
    deteccion_polo_tierra BOOLEAN
);

-- Índices para especificaciones
CREATE INDEX idx_especificaciones_producto ON especificaciones(producto_id);

-- Comentarios
COMMENT ON TABLE especificaciones IS 'Especificaciones técnicas detalladas de los productos';
COMMENT ON COLUMN especificaciones.apto_pb_ac IS 'Apto para baterías de Plomo-Ácido';
COMMENT ON COLUMN especificaciones.apto_ni_cd IS 'Apto para baterías de Níquel-Cadmio';

-- ============================================
-- TABLA: ALIMENTACIÓN
-- ============================================
CREATE TABLE alimentacion (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    
    tipo VARCHAR(50), -- 'Trifásico', 'Monofásico'
    tension VARCHAR(50),
    rango_tension VARCHAR(50),
    frecuencia INTEGER,
    rango_frecuencia VARCHAR(50),
    conexion_neutro VARCHAR(50),
    conductor_pe_independiente BOOLEAN,
    corriente_cortocircuito VARCHAR(100),
    tipo_interruptor_acometida TEXT,
    potencia_transformador VARCHAR(50),
    corriente_conexion_transformador VARCHAR(50)
);

-- Índices para alimentacion
CREATE INDEX idx_alimentacion_producto ON alimentacion(producto_id);
CREATE INDEX idx_alimentacion_tipo ON alimentacion(tipo);

-- Comentarios
COMMENT ON TABLE alimentacion IS 'Características de alimentación eléctrica de entrada';

-- ============================================
-- TABLA: SALIDA
-- ============================================
CREATE TABLE salida (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    
    tension_nominal INTEGER,
    corriente_nominal INTEGER,
    maxima_corriente_consumos INTEGER,
    tipo_interruptor_consumo TEXT,
    tipo_interruptor_baterias TEXT,
    sistema_rectificacion TEXT
);

-- Índices para salida
CREATE INDEX idx_salida_producto ON salida(producto_id);

-- Comentarios
COMMENT ON TABLE salida IS 'Características de salida eléctrica del rectificador';

-- ============================================
-- TABLA: GABINETE
-- ============================================
CREATE TABLE gabinete (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    
    material VARCHAR(100),
    acceso VARCHAR(100),
    grado_proteccion VARCHAR(10), -- IP21, IP54, etc.
    espesor_chapa DECIMAL(5,2),
    tipo_pintura VARCHAR(100),
    color VARCHAR(20), -- RAL 7032, etc.
    espesor_pintura DECIMAL(5,2),
    ancho INTEGER, -- mm
    alto INTEGER, -- mm
    profundidad INTEGER, -- mm
    peso INTEGER -- kg
);

-- Índices para gabinete
CREATE INDEX idx_gabinete_producto ON gabinete(producto_id);
CREATE INDEX idx_gabinete_dimensiones ON gabinete(ancho, alto, profundidad);

-- Comentarios
COMMENT ON TABLE gabinete IS 'Características físicas del gabinete del producto';
COMMENT ON COLUMN gabinete.grado_proteccion IS 'Grado de protección IP (Ingress Protection)';

-- ============================================
-- TABLA: APARATOS DE MEDIDA
-- ============================================
CREATE TABLE aparatos_medida (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    
    unidad_digital_centralizada BOOLEAN,
    protocolo_comunicacion VARCHAR(50), -- 'Modbus RTU', etc.
    puerto_comunicacion VARCHAR(100), -- 'RS485', 'TCP-IP', etc.
    medicion JSONB -- Mediciones disponibles en formato flexible
);

-- Índices para aparatos_medida
CREATE INDEX idx_aparatos_medida_producto ON aparatos_medida(producto_id);
CREATE INDEX idx_aparatos_medida_medicion ON aparatos_medida USING GIN (medicion);

-- Comentarios
COMMENT ON TABLE aparatos_medida IS 'Características de medición y comunicación del producto';
COMMENT ON COLUMN aparatos_medida.medicion IS 'Mediciones disponibles en formato JSON';

-- ============================================
-- TABLA: ACCESORIOS
-- ============================================
CREATE TABLE accesorios (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    
    panel_control TEXT,
    resistencias_calefactoras BOOLEAN,
    tension_resistencias INTEGER,
    potencia_resistencias VARCHAR(100),
    cables_incluidos BOOLEAN,
    tension_aislacion_cables VARCHAR(20),
    material_cables VARCHAR(50),
    baja_emision_halogenos BOOLEAN,
    bornes_reserva BOOLEAN,
    placas_identificacion BOOLEAN,
    chapa_caracteristicas BOOLEAN
);

-- Índices para accesorios
CREATE INDEX idx_accesorios_producto ON accesorios(producto_id);

-- Comentarios
COMMENT ON TABLE accesorios IS 'Accesorios y componentes adicionales del producto';

-- ============================================
-- TABLA: TIPOS DE ALARMA (Catálogo)
-- ============================================
CREATE TABLE tipos_alarma (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL
);

-- Índices para tipos_alarma
CREATE INDEX idx_tipos_alarma_codigo ON tipos_alarma(codigo);

-- Datos iniciales de tipos de alarma
INSERT INTO tipos_alarma (codigo, descripcion) VALUES
    ('FALLA_RED', 'Falla de Red'),
    ('ALTA_TENSION_BAT', 'Alta Tensión en baterías'),
    ('BAJA_TENSION_BAT', 'Baja Tensión en baterías'),
    ('TENSION_BAT_CRITICA', 'Tensión en baterías Crítica (Batería descargada)'),
    ('ALTA_TENSION_CONS', 'Alta Tensión en consumos'),
    ('BAJA_TENSION_CONS', 'Baja Tensión en consumos'),
    ('TENSION_CONS_CRITICA', 'Tensión en consumo Crítica'),
    ('FALLA_RECTIFICADOR', 'Falla de rectificador'),
    ('ALTA_CORRIENTE_RECT', 'Alta corriente de rectificador'),
    ('ALTA_CORRIENTE_BAT', 'Alta corriente de baterías'),
    ('ALTA_CORRIENTE_CONS', 'Alta corriente de consumos'),
    ('POLO_POS_TIERRA', 'Polo positivo a tierra'),
    ('POLO_NEG_TIERRA', 'Polo negativo a tierra'),
    ('FALLO_VENTILADOR', 'Fallo de un ventilador'),
    ('OBSTRUCCION_FILTROS', 'Obstrucción en los filtros'),
    ('BATERIA_DESCARGA', 'Batería en descarga'),
    ('AVERIA_RED_SALIDA', 'Avería en la red de salida (falla aislación)'),
    ('APERTURA_INTERRUPTORES', 'Apertura de interruptores'),
    ('FALLO_BATERIA', 'Fallo en batería'),
    ('TEMPERATURA', 'Temperatura (termostato)'),
    ('CARGADOR_MODO_FONDO', 'Cargador en modo fondo');

-- Comentarios
COMMENT ON TABLE tipos_alarma IS 'Catálogo de tipos de alarmas disponibles';

-- ============================================
-- TABLA: ALARMAS
-- ============================================
CREATE TABLE alarmas (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT REFERENCES productos(id) ON DELETE CASCADE,
    tipo_alarma_id BIGINT REFERENCES tipos_alarma(id),
    tipo_senal VARCHAR(100), -- 'LCD + contacto seco', 'LCD', 'Configurable', etc.
    activa BOOLEAN DEFAULT TRUE
);

-- Índices para alarmas
CREATE INDEX idx_alarmas_producto ON alarmas(producto_id);
CREATE INDEX idx_alarmas_tipo ON alarmas(tipo_alarma_id);

-- Comentarios
COMMENT ON TABLE alarmas IS 'Alarmas configuradas por producto';

-- ============================================
-- TABLA: SEÑALIZACIONES
-- ============================================
CREATE TABLE senalizaciones (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT REFERENCES productos(id) ON DELETE CASCADE,
    tipo VARCHAR(100) NOT NULL, -- 'Red Ok', 'LED FLOTE', 'LED FONDO', etc.
    descripcion TEXT,
    tipo_display VARCHAR(50) -- 'LED frontal', 'Display LCD 20x4', etc.
);

-- Índices para senalizaciones
CREATE INDEX idx_senalizaciones_producto ON senalizaciones(producto_id);
CREATE INDEX idx_senalizaciones_tipo ON senalizaciones(tipo);

-- Comentarios
COMMENT ON TABLE senalizaciones IS 'Señalizaciones visuales del producto';

-- ============================================
-- TABLA: TIPOS DE ENSAYO (Catálogo)
-- ============================================
CREATE TABLE tipos_ensayo (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    orden INTEGER
);

-- Índices para tipos_ensayo
CREATE INDEX idx_tipos_ensayo_codigo ON tipos_ensayo(codigo);
CREATE INDEX idx_tipos_ensayo_orden ON tipos_ensayo(orden);

-- Datos iniciales de tipos de ensayo
INSERT INTO tipos_ensayo (codigo, descripcion, orden) VALUES
    ('RESIST_AISLACION', 'Medida de la resistencia de aislación', 1),
    ('DIELECTRICO', 'Ensayo dieléctrico (2.500V potencia, 2.000V control/auxiliares)', 2),
    ('RESIST_POST_DIELECTRICO', 'Medida de resistencia de aislación después del ensayo dieléctrico', 3),
    ('ELEMENTOS_MECANICOS', 'Funcionamiento de elementos mecánicos y efectividad de enclavamientos', 4),
    ('TOLERANCIA_TENSION', 'Medida de la tolerancia de la tensión de salida', 5),
    ('NIVEL_RIZADO', 'Comprobación del nivel de rizado', 6),
    ('VERIFICACION_ELECTRICA', 'Ensayo eléctrico de verificación de valores de salida y circuitos', 7),
    ('VERIFICACION_TENSIONES', 'Verificación de tensiones de flotación, carga rápida y excepcional', 8),
    ('VARIACION_TENSION_ALIM', 'Comprobación de estabilidad con variación de tensión de alimentación', 9),
    ('VARIACION_CARGA', 'Verificación con variación de carga de 0 al 100%', 10),
    ('CARGA_BATERIA', 'Verificación de la carga de la batería', 11),
    ('ARMONICOS', 'Medida del contenido de armónicos en la alimentación', 12),
    ('PLENA_CARGA', 'Ensayo a plena carga (mínimo 48 horas)', 13),
    ('RENDIMIENTO', 'Ensayo de rendimiento', 14),
    ('REPARTO_INTENSIDADES', 'Ensayo de reparto de intensidades (cargadores en paralelo)', 15),
    ('SENALIZACION_ALARMA', 'Prueba de señalización y alarma', 16),
    ('FUNCIONAL_COMPLETO', 'Prueba funcional en todas las condiciones de operación', 17),
    ('CORTOCIRCUITO', 'Prueba de capacidad de suministro de corriente de cortocircuito', 18);

-- Comentarios
COMMENT ON TABLE tipos_ensayo IS 'Catálogo de tipos de ensayos de rutina';

-- ============================================
-- TABLA: ENSAYOS
-- ============================================
CREATE TABLE ensayos (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT REFERENCES productos(id) ON DELETE CASCADE,
    tipo_ensayo_id BIGINT REFERENCES tipos_ensayo(id),
    realizado BOOLEAN DEFAULT TRUE,
    observaciones TEXT
);

-- Índices para ensayos
CREATE INDEX idx_ensayos_producto ON ensayos(producto_id);
CREATE INDEX idx_ensayos_tipo ON ensayos(tipo_ensayo_id);

-- Comentarios
COMMENT ON TABLE ensayos IS 'Ensayos realizados por producto';

-- ============================================
-- TABLA: GARANTÍA
-- ============================================
CREATE TABLE garantia (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id BIGINT UNIQUE REFERENCES productos(id) ON DELETE CASCADE,
    meses INTEGER DEFAULT 24,
    condiciones TEXT
);

-- Índices para garantia
CREATE INDEX idx_garantia_producto ON garantia(producto_id);

-- Comentarios
COMMENT ON TABLE garantia IS 'Información de garantía del producto';

-- ============================================
-- TRIGGERS PARA UPDATED_AT
-- ============================================

-- Función para actualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para productos
CREATE TRIGGER update_productos_updated_at
    BEFORE UPDATE ON productos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista completa de productos con información principal
CREATE VIEW v_productos_completo AS
SELECT 
    p.id,
    p.codigo,
    p.marca,
    p.modelo,
    p.tension_nominal,
    p.corriente_nominal,
    p.regulador_diodos,
    p.origen,
    p.tipo,
    e.temperatura_maxima,
    e.temperatura_minima,
    e.tipo_instalacion,
    a.tipo as tipo_alimentacion,
    a.tension as tension_alimentacion,
    g.ancho,
    g.alto,
    g.profundidad,
    g.peso,
    ga.meses as garantia_meses,
    p.created_at,
    p.updated_at
FROM productos p
LEFT JOIN especificaciones e ON p.id = e.producto_id
LEFT JOIN alimentacion a ON p.id = a.producto_id
LEFT JOIN gabinete g ON p.id = g.producto_id
LEFT JOIN garantia ga ON p.id = ga.producto_id;

-- Vista de productos por tensión nominal
CREATE VIEW v_productos_por_tension AS
SELECT 
    tension_nominal,
    COUNT(*) as cantidad,
    array_agg(DISTINCT marca) as marcas,
    MIN(corriente_nominal) as corriente_min,
    MAX(corriente_nominal) as corriente_max
FROM productos
GROUP BY tension_nominal
ORDER BY tension_nominal;

-- ============================================
-- FUNCIONES ÚTILES
-- ============================================

-- Función para obtener productos por rango de corriente
CREATE OR REPLACE FUNCTION buscar_productos_por_corriente(
    corriente_min INTEGER,
    corriente_max INTEGER
)
RETURNS TABLE (
    id BIGINT,
    codigo VARCHAR(50),
    marca VARCHAR(100),
    modelo VARCHAR(50),
    tension_nominal INTEGER,
    corriente_nominal INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.codigo,
        p.marca,
        p.modelo,
        p.tension_nominal,
        p.corriente_nominal
    FROM productos p
    WHERE p.corriente_nominal BETWEEN corriente_min AND corriente_max
    ORDER BY p.tension_nominal, p.corriente_nominal;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener alarmas de un producto
CREATE OR REPLACE FUNCTION obtener_alarmas_producto(producto_codigo VARCHAR(50))
RETURNS TABLE (
    tipo_alarma VARCHAR(50),
    descripcion TEXT,
    tipo_senal VARCHAR(100),
    activa BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ta.codigo,
        ta.descripcion,
        a.tipo_senal,
        a.activa
    FROM productos p
    INNER JOIN alarmas a ON p.id = a.producto_id
    INNER JOIN tipos_alarma ta ON a.tipo_alarma_id = ta.id
    WHERE p.codigo = producto_codigo
    ORDER BY ta.codigo;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PERMISOS (ajustar según necesidades)
-- ============================================

-- Crear rol de solo lectura
-- CREATE ROLE readonly_user;
-- GRANT CONNECT ON DATABASE rectificadores_db TO readonly_user;
-- GRANT USAGE ON SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO readonly_user;

-- Crear rol de escritura
-- CREATE ROLE readwrite_user;
-- GRANT CONNECT ON DATABASE rectificadores_db TO readwrite_user;
-- GRANT USAGE ON SCHEMA public TO readwrite_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO readwrite_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO readwrite_user;

-- ============================================
-- INFORMACIÓN DE LA BASE DE DATOS
-- ============================================

COMMENT ON DATABASE rectificadores_db IS 'Base de datos para gestión de productos SERVELEC';

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

-- Verificar la creación exitosa
SELECT 'Base de datos creada exitosamente!' AS mensa je;
SELECT 'Total de tablas creadas: ' || COUNT(*) AS total_tablas 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';