/**
 * Tipos para datos de extraccion
 *
 * Basados en los modelos Pydantic del backend:
 * - src/licitaciones/domain/extraction_models.py
 *
 * Solo incluimos los campos que usamos en el UI.
 * Si necesitamos mas campos, los agregamos aca.
 */

// Estado de una extraccion
export type ExtractionStatus = 'uploading' | 'processing' | 'completed' | 'error'

// Registro de una extraccion (wrapper con metadata)
export interface ExtractionRecord {
  id: string
  filename: string
  uploadedAt: string // ISO date string
  status: ExtractionStatus
  pageRanges?: string // "1-10, 15-25"
  result?: LicitacionCompleta
  errorMessage?: string
}

// Resultado principal de la extraccion
export interface LicitacionCompleta {
  especificaciones_comunes?: EspecificacionesComunes
  items: ItemLicitado[]
}

// Item individual de la licitacion
export interface ItemLicitado {
  numero_item?: number
  cantidad?: number
  descripcion?: string
  alimentacion?: Alimentacion
  salida?: Salida
  sistema_control?: string
  marca?: string
  modelo?: string
}

// Especificaciones comunes a todos los items
export interface EspecificacionesComunes {
  generales?: Generales
  condiciones_ambientales?: CondicionesAmbientales
  alimentacion?: Alimentacion
  salida?: Salida
  protecciones?: Protecciones
  garantia?: Garantia
  // Agregamos mas secciones segun necesidad
}

// Sub-tipos para las secciones
export interface Generales {
  codigo_producto?: string
  marca?: string
  modelo?: string
  tipo?: string
  normas_fabricacion?: string
  origen?: string
}

export interface CondicionesAmbientales {
  temperatura_max_c?: number
  temperatura_min_c?: number
  altura_snm_m?: number
  humedad_relativa_max_pct?: number
  tipo_servicio?: string
}

export interface Alimentacion {
  tipo?: string // "monofásica" | "bifásica" | "trifásica"
  tension_v?: number
  frecuencia_hz?: number
}

export interface Salida {
  tension_nominal_v?: number
  corriente_nominal_a?: number
  tension_ajustable?: NumericRange
  corriente_ajustable?: NumericRange
}

export interface NumericRange {
  min: number
  max: number
  unidad?: string
}

export interface Protecciones {
  sobretensiones_cc?: boolean
  sobretensiones_ca?: boolean
  cortocircuito?: boolean
  sobrecarga?: boolean
  lvd?: boolean
}

export interface Garantia {
  descripcion?: string
  meses?: number
}
