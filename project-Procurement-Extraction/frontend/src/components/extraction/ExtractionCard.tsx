import { Link } from 'react-router-dom'
import { FileText, ChevronRight, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import type { ExtractionRecord, ExtractionStatus } from '../../types'
import { Badge } from '../ui'

/**
 * ExtractionCard: Muestra resumen de una extraccion en el historial
 *
 * Clickeable - lleva al detalle
 */

interface ExtractionCardProps {
  extraction: ExtractionRecord
}

// Mapeo de status a variante de Badge
const statusConfig: Record<ExtractionStatus, { variant: 'success' | 'warning' | 'error' | 'info'; label: string; Icon: typeof CheckCircle }> = {
  uploading: { variant: 'info', label: 'Subiendo', Icon: Loader2 },
  processing: { variant: 'warning', label: 'Procesando', Icon: Loader2 },
  completed: { variant: 'success', label: 'Completado', Icon: CheckCircle },
  error: { variant: 'error', label: 'Error', Icon: AlertCircle },
}

export default function ExtractionCard({ extraction }: ExtractionCardProps) {
  const { variant, label, Icon } = statusConfig[extraction.status]

  // Formatear fecha
  const date = new Date(extraction.uploadedAt)
  const formattedDate = date.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  // Contar items si hay resultado
  const itemCount = extraction.result?.items.length || 0

  return (
    <Link
      to={`/extraction/${extraction.id}`}
      className="block bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all duration-200"
    >
      <div className="p-4 flex items-center gap-4">
        {/* Icono */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-medium text-gray-900 truncate">
              {extraction.filename}
            </h3>
            <Badge variant={variant}>
              <Icon className={`w-3 h-3 mr-1 ${extraction.status === 'processing' ? 'animate-spin' : ''}`} />
              {label}
            </Badge>
          </div>

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {formattedDate}
            </span>
            {itemCount > 0 && (
              <span>{itemCount} item{itemCount !== 1 ? 's' : ''}</span>
            )}
            {extraction.pageRanges && (
              <span>Paginas: {extraction.pageRanges}</span>
            )}
          </div>

          {extraction.errorMessage && (
            <p className="mt-1 text-sm text-red-600 truncate">
              {extraction.errorMessage}
            </p>
          )}
        </div>

        {/* Flecha */}
        <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
      </div>
    </Link>
  )
}
