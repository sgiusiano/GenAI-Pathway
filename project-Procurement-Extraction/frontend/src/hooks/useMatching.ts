import { useQuery } from '@tanstack/react-query'
import { getMatchResults } from '../services'

/**
 * Hook para obtener resultados de matching
 */
export function useMatchResults(extractionId: string) {
  return useQuery({
    queryKey: ['matching', extractionId],
    queryFn: () => getMatchResults(extractionId),
    enabled: !!extractionId,
  })
}
