import { CheckCircle, Loader2, AlertCircle, FileSearch } from 'lucide-react'
import { useUploadStore } from '../../stores/upload.store'
import Progress from '../ui/Progress'

/**
 * UploadProgress: Muestra el progreso y estado del upload/procesamiento
 */

export default function UploadProgress() {
  const { status, progress, errorMessage } = useUploadStore()

  if (status === 'idle') return null

  return (
    <div className="space-y-4">
      {/* Barra de progreso durante upload */}
      {status === 'uploading' && (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-blue-600">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="font-medium">Subiendo archivo...</span>
          </div>
          <Progress value={progress} showLabel />
        </div>
      )}

      {/* Estado de procesamiento */}
      {status === 'processing' && (
        <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <FileSearch className="w-6 h-6 text-blue-600 animate-pulse" />
          <div>
            <p className="font-medium text-blue-900">Procesando documento...</p>
            <p className="text-sm text-blue-700">
              Extrayendo especificaciones tecnicas con IA
            </p>
          </div>
        </div>
      )}

      {/* Completado */}
      {status === 'completed' && (
        <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
          <CheckCircle className="w-6 h-6 text-green-600" />
          <div>
            <p className="font-medium text-green-900">Extraccion completada</p>
            <p className="text-sm text-green-700">
              Los datos fueron extraidos exitosamente
            </p>
          </div>
        </div>
      )}

      {/* Error */}
      {status === 'error' && (
        <div className="flex items-center gap-3 p-4 bg-red-50 rounded-lg border border-red-200">
          <AlertCircle className="w-6 h-6 text-red-600" />
          <div>
            <p className="font-medium text-red-900">Error en el procesamiento</p>
            <p className="text-sm text-red-700">
              {errorMessage || 'Ocurrio un error inesperado'}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
