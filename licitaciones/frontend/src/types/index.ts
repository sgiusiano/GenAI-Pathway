/**
 * Re-exporta todos los tipos para imports mas limpios
 *
 * En vez de:
 *   import { ExtractionRecord } from './types/extraction.types'
 *   import { MatchResult } from './types/matching.types'
 *
 * Podes hacer:
 *   import { ExtractionRecord, MatchResult } from './types'
 */

export * from './extraction.types'
export * from './matching.types'
