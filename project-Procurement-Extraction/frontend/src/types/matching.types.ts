/**
 * Tipos para resultados de matching
 *
 * Cuando un item de la licitacion se compara
 * contra productos del catalogo SERVELEC
 */

import type { ItemLicitado } from './extraction.types'

// Resultado de matching para un item
export interface MatchResult {
  item: ItemLicitado
  productos: ProductoMatch[]
  bestScore: number // 0-100
  notas?: string
}

// Producto del catalogo que matchea
export interface ProductoMatch {
  id: number
  codigo: string // "110-50-CS"
  marca: string
  modelo: string
  tension_nominal: number // V
  corriente_nominal: number // A
  regulador_diodos: 'CS' | 'CD' // Cadena Simple / Doble
  score: number // 0-100, que tan bien matchea
}
