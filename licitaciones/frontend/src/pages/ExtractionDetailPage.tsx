import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, GitCompare, FileText, Package } from 'lucide-react'
import { useExtraction } from '../hooks'
import { SpecsPanel, ItemsList } from '../components/extraction'
import { Button, Spinner, Badge, Tabs } from '../components/ui'

/**
 * ExtractionDetailPage: Detalle de una extraccion
 *
 * - Tabs: Especificaciones Comunes | Items
 * - Boton para ver matching
 */

export default function ExtractionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data: extraction, isLoading, isError } = useExtraction(id || '')

  // Loading
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  // Error o no encontrado
  if (isError || !extraction) {
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

  // Si esta procesando, mostrar mensaje
  if (extraction.status === 'processing') {
    return (
      <div className="space-y-6">
        <BackButton />
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <Spinner className="mx-auto mb-4" />
          <p className="text-yellow-800 font-medium">
            Esta extraccion aun se esta procesando
          </p>
          <p className="text-yellow-600 text-sm mt-1">
            Los resultados estaran disponibles en breve
          </p>
        </div>
      </div>
    )
  }

  // Si hay error
  if (extraction.status === 'error') {
    return (
      <div className="space-y-6">
        <BackButton />
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 font-medium">Error en la extraccion</p>
          <p className="text-red-600 text-sm mt-1">
            {extraction.errorMessage || 'Ocurrio un error durante el procesamiento'}
          </p>
        </div>
      </div>
    )
  }

  // Extraccion completada
  const result = extraction.result
  const itemCount = result?.items.length || 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <BackButton />
          <h1 className="text-2xl font-bold text-gray-900 mt-2">
            {extraction.filename}
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge variant="success">Completado</Badge>
            <span className="text-sm text-gray-500">
              {itemCount} item{itemCount !== 1 ? 's' : ''} extraido{itemCount !== 1 ? 's' : ''}
            </span>
            {extraction.pageRanges && (
              <span className="text-sm text-gray-500">
                Paginas: {extraction.pageRanges}
              </span>
            )}
          </div>
        </div>

        {/* Boton Matching */}
        <Link to={`/extraction/${id}/matching`}>
          <Button>
            <GitCompare className="w-4 h-4" />
            Ver Matching
          </Button>
        </Link>
      </div>

      {/* Tabs con contenido */}
      {result && (
        <Tabs defaultTab="specs">
          <Tabs.List>
            <Tabs.Tab value="specs">
              <FileText className="w-4 h-4 inline mr-2" />
              Especificaciones Comunes
            </Tabs.Tab>
            <Tabs.Tab value="items">
              <Package className="w-4 h-4 inline mr-2" />
              Items ({itemCount})
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="specs">
            {result.especificaciones_comunes ? (
              <SpecsPanel specs={result.especificaciones_comunes} />
            ) : (
              <div className="text-center py-8 text-gray-500">
                No hay especificaciones comunes
              </div>
            )}
          </Tabs.Panel>

          <Tabs.Panel value="items">
            <ItemsList items={result.items} />
          </Tabs.Panel>
        </Tabs>
      )}
    </div>
  )
}

// Componente helper para el boton de volver
function BackButton() {
  return (
    <Link
      to="/history"
      className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
    >
      <ArrowLeft className="w-4 h-4" />
      Volver al Historial
    </Link>
  )
}
