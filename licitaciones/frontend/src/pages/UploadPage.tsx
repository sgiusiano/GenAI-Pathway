import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { useUploadStore } from '../stores/upload.store'
import { uploadPdf } from '../services'
import { DropZone, PageRangeInput, UploadProgress } from '../components/upload'
import { Button, Card } from '../components/ui'
import { Send, RotateCcw } from 'lucide-react'

/**
 * UploadPage: Pagina principal para subir PDFs
 *
 * Flujo:
 * 1. Usuario arrastra/selecciona PDF
 * 2. Opcionalmente especifica paginas
 * 3. Click en "Procesar"
 * 4. Se muestra progreso + toast notifications
 * 5. Al completar, puede ir al historial
 */

export default function UploadPage() {
  const navigate = useNavigate()
  const {
    file,
    pageRanges,
    status,
    setProgress,
    setStatus,
    setError,
    setExtractionId,
    reset,
  } = useUploadStore()

  // Manejar envio del formulario
  const handleSubmit = async () => {
    if (!file) return

    try {
      setStatus('uploading')
      toast.info('Subiendo documento...')

      // Llamar al servicio de upload
      const result = await uploadPdf(file, pageRanges || undefined, (progress) => {
        setProgress(progress)
      })

      // Cambiar a estado processing
      setStatus('processing')
      setExtractionId(result.id)
      toast.info('LiciBot procesando...', {
        description: 'Extrayendo especificaciones del documento',
      })

      // Simular que despues de 3 segundos se completa
      // En una app real, harias polling o usarias websockets
      setTimeout(() => {
        setStatus('completed')
        toast.success('Extraccion completada!', {
          description: 'Los datos fueron extraidos exitosamente',
        })
      }, 3000)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido'
      setError(errorMessage)
      toast.error('Error al procesar', {
        description: errorMessage,
      })
    }
  }

  // Determinar si el boton debe estar habilitado
  const canSubmit = file && status === 'idle'
  const isProcessing = status === 'uploading' || status === 'processing'

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Subir Documento
        </h1>
        <p className="mt-1 text-gray-600">
          Sube un PDF de licitacion y LiciBot extraera las especificaciones tecnicas
        </p>
      </div>

      <Card>
        <Card.Body className="space-y-6">
          {/* DropZone */}
          <DropZone />

          {/* Input de rango de paginas */}
          {file && status === 'idle' && <PageRangeInput />}

          {/* Progreso */}
          <UploadProgress />

          {/* Acciones */}
          <div className="flex gap-3">
            {/* Boton Procesar */}
            {(status === 'idle' || status === 'error') && (
              <Button
                onClick={handleSubmit}
                disabled={!canSubmit}
                isLoading={isProcessing}
              >
                <Send className="w-4 h-4" />
                Procesar Documento
              </Button>
            )}

            {/* Boton Reset (cuando hay error o completado) */}
            {(status === 'error' || status === 'completed') && (
              <Button variant="outline" onClick={reset}>
                <RotateCcw className="w-4 h-4" />
                Subir otro documento
              </Button>
            )}

            {/* Boton Ver Historial (cuando completa) */}
            {status === 'completed' && (
              <Button variant="secondary" onClick={() => navigate('/history')}>
                Ver Historial
              </Button>
            )}
          </div>
        </Card.Body>
      </Card>
    </div>
  )
}
