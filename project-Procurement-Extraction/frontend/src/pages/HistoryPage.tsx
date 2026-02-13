import { Link } from 'react-router-dom'
import { FileText, Plus } from 'lucide-react'
import { useExtractionHistory } from '../hooks'
import { ExtractionCard } from '../components/extraction'
import { Button, Spinner } from '../components/ui'

/**
 * HistoryPage: Lista de extracciones anteriores
 *
 * - Muestra todas las extracciones en cards clickeables
 * - Estados: loading, error, empty, con datos
 */

export default function HistoryPage() {
  // useExtractionHistory usa React Query internamente
  // Devuelve: { data, isLoading, isError, error }
  const { data: extractions, isLoading, isError, error } = useExtractionHistory()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">
          Historial de Extracciones
        </h1>
        <Link to="/">
          <Button size="sm">
            <Plus className="w-4 h-4" />
            Nueva Extraccion
          </Button>
        </Link>
      </div>

      {/* Estado: Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      )}

      {/* Estado: Error */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-600">
            Error al cargar el historial: {error?.message || 'Error desconocido'}
          </p>
        </div>
      )}

      {/* Estado: Sin datos */}
      {!isLoading && !isError && extractions?.length === 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
          <FileText className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            No hay extracciones
          </h3>
          <p className="text-gray-500 mb-4">
            Sube tu primer documento de licitacion para comenzar
          </p>
          <Link to="/">
            <Button>
              <Plus className="w-4 h-4" />
              Subir Documento
            </Button>
          </Link>
        </div>
      )}

      {/* Estado: Con datos */}
      {!isLoading && !isError && extractions && extractions.length > 0 && (
        <div className="space-y-3">
          {extractions.map((extraction) => (
            <ExtractionCard key={extraction.id} extraction={extraction} />
          ))}
        </div>
      )}
    </div>
  )
}
