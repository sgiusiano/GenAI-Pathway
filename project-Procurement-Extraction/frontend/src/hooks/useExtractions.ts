import { useQuery } from '@tanstack/react-query'
import { getExtractions, getExtractionById } from '../services'

/**
 * Hooks de React Query para extracciones
 *
 * React Query maneja automaticamente:
 * - Loading states
 * - Error handling
 * - Caching
 * - Refetching
 */

/**
 * Hook para obtener todas las extracciones (historial)
 */
export function useExtractionHistory() {
  return useQuery({
    queryKey: ['extractions'], // Clave unica para el cache
    queryFn: getExtractions,   // Funcion que obtiene los datos
  })
}

/**
 * Hook para obtener una extraccion por ID
 */
export function useExtraction(id: string) {
  return useQuery({
    queryKey: ['extraction', id],
    queryFn: () => getExtractionById(id),
    enabled: !!id, // Solo ejecutar si hay ID
  })
}
