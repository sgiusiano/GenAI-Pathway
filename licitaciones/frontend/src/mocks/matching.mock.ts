/**
 * Datos mock de matching
 *
 * Simula resultados de comparar items extraidos
 * contra el catalogo SERVELEC
 */

import type { MatchResult, ProductoMatch } from '../types'
import { mockExtractions } from './extractions.mock'

// Productos del catalogo (simplificado)
export const mockCatalog: ProductoMatch[] = [
  {
    id: 1,
    codigo: '110-50-CS',
    marca: 'SERVELEC',
    modelo: 'RDT-110-50-CS',
    tension_nominal: 110,
    corriente_nominal: 50,
    regulador_diodos: 'CS',
    score: 0,
  },
  {
    id: 2,
    codigo: '110-40-CD',
    marca: 'SERVELEC',
    modelo: 'RDT-110-40-CD',
    tension_nominal: 110,
    corriente_nominal: 40,
    regulador_diodos: 'CD',
    score: 0,
  },
  {
    id: 3,
    codigo: '110-30-CS',
    marca: 'SERVELEC',
    modelo: 'RDT-110-30-CS',
    tension_nominal: 110,
    corriente_nominal: 30,
    regulador_diodos: 'CS',
    score: 0,
  },
  {
    id: 4,
    codigo: '48-100-CS',
    marca: 'SERVELEC',
    modelo: 'RDT-48-100-CS',
    tension_nominal: 48,
    corriente_nominal: 100,
    regulador_diodos: 'CS',
    score: 0,
  },
]

// Genera resultados de matching para una extraccion
export function getMockMatchResults(extractionId: string): MatchResult[] {
  const extraction = mockExtractions.find((e) => e.id === extractionId)

  if (!extraction?.result?.items) {
    return []
  }

  return extraction.result.items.map((item) => {
    // Buscar productos que matcheen por tension y corriente
    const matches = mockCatalog
      .filter((p) => {
        const tensionMatch = p.tension_nominal === item.salida?.tension_nominal_v
        const corrienteMatch = p.corriente_nominal === item.salida?.corriente_nominal_a
        return tensionMatch || corrienteMatch
      })
      .map((p) => {
        // Calcular score basico
        let score = 0
        if (p.tension_nominal === item.salida?.tension_nominal_v) score += 50
        if (p.corriente_nominal === item.salida?.corriente_nominal_a) score += 50
        return { ...p, score }
      })
      .sort((a, b) => b.score - a.score)

    return {
      item,
      productos: matches,
      bestScore: matches[0]?.score || 0,
      notas: matches.length > 0 ? 'Productos compatibles encontrados' : 'Sin coincidencias exactas',
    }
  })
}
