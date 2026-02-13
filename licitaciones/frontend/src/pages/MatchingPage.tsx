import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, GitCompare } from 'lucide-react'
import { useExtraction, useMatchResults } from '../hooks'
import { MatchCard } from '../components/matching'
import { Button, Spinner } from '../components/ui'

/**
 * MatchingPage: Resultados de matching contra catalogo
 *
 * Muestra cada item de la extraccion con los productos
 * del catalogo que coinciden y su score de compatibilidad
 */

export default function MatchingPage() {
  const { id } = useParams<{ id: string }>()
  const { data: extraction, isLoading: loadingExtraction } = useExtraction(id || '')
  const { data: matchResults, isLoading: loadingMatching } = useMatchResults(id || '')

  const isLoading = loadingExtraction || loadingMatching

  // Loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  // No encontrado
  if (!extraction) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Extraccion no encontrada</p>
        <Link to="/history">
          <Button variant="outline">
            <ArrowLeft className="w-4 h-4" />
            Volver al Historial
          </Button>
        </Link>
      </div>
    )
  }

  // Calcular resumen
  const totalItems = matchResults?.length || 0
  const itemsWithMatch = matchResults?.filter((m) => m.productos.length > 0).length || 0
  const avgScore = totalItems > 0
    ? Math.round(matchResults!.reduce((sum, m) => sum + m.bestScore, 0) / totalItems)
    : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to={`/extraction/${id}`}
          className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="w-4 h-4" />
          Volver al Detalle
        </Link>

        <div className="flex items-center gap-3 mt-2">
          <GitCompare className="w-6 h-6 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">
            Resultados de Matching
          </h1>
        </div>

        <p className="text-gray-600 mt-1">{extraction.filename}</p>

        {/* Resumen */}
        <div className="flex gap-4 mt-4">
          <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
            <p className="text-sm text-gray-500">Items Analizados</p>
            <p className="text-xl font-bold text-gray-900">{totalItems}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
            <p className="text-sm text-gray-500">Con Coincidencias</p>
            <p className="text-xl font-bold text-green-600">{itemsWithMatch}</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 px-4 py-2">
            <p className="text-sm text-gray-500">Score Promedio</p>
            <p className="text-xl font-bold text-blue-600">{avgScore}%</p>
          </div>
        </div>
      </div>

      {/* Lista de matches */}
      {matchResults && matchResults.length > 0 ? (
        <div className="space-y-4">
          {matchResults.map((match, index) => (
            <MatchCard key={match.item.numero_item || index} match={match} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
          <p className="text-gray-500">No hay resultados de matching disponibles</p>
        </div>
      )}
    </div>
  )
}
