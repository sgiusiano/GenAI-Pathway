/**
 * Servicio de matching
 *
 * Obtiene resultados de comparar items extraidos
 * contra el catalogo de productos
 */

import type { MatchResult } from '../types'
import { getMockMatchResults } from '../mocks/matching.mock'

// Simula delay de red
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const randomDelay = () => delay(500 + Math.random() * 1000)

/**
 * Obtiene resultados de matching para una extraccion
 */
export async function getMatchResults(extractionId: string): Promise<MatchResult[]> {
  await randomDelay()
  return getMockMatchResults(extractionId)
}
