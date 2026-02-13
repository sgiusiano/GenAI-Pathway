import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X } from 'lucide-react'
import { useUploadStore } from '../../stores/upload.store'
import Button from '../ui/Button'

/**
 * DropZone: Area para arrastrar y soltar archivos PDF
 *
 * Usa react-dropzone que maneja:
 * - Drag & drop
 * - Click para abrir selector
 * - Validacion de tipo de archivo
 */

export default function DropZone() {
  const { file, setFile, status } = useUploadStore()

  // Callback cuando se suelta un archivo
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        setFile(acceptedFiles[0])
      }
    },
    [setFile]
  )

  // Configuracion de react-dropzone
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'], // Solo PDFs
    },
    maxFiles: 1,
    disabled: status === 'uploading' || status === 'processing',
  })

  // Si ya hay un archivo seleccionado, mostrar preview
  if (file) {
    return (
      <div className="border-2 border-blue-200 bg-blue-50 rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-10 h-10 text-blue-600" />
            <div>
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          {status === 'idle' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFile(null)}
            >
              <X className="w-4 h-4" />
              Cambiar
            </Button>
          )}
        </div>
      </div>
    )
  }

  // Area de drop
  return (
    <div
      {...getRootProps()}
      className={`
        border-2 border-dashed rounded-lg p-12
        text-center cursor-pointer
        transition-colors duration-200
        ${isDragActive && !isDragReject ? 'border-blue-500 bg-blue-50' : ''}
        ${isDragReject ? 'border-red-500 bg-red-50' : ''}
        ${!isDragActive ? 'border-gray-300 hover:border-gray-400 hover:bg-gray-50' : ''}
      `}
    >
      <input {...getInputProps()} />

      <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />

      {isDragReject ? (
        <p className="text-red-600 font-medium">Solo se aceptan archivos PDF</p>
      ) : isDragActive ? (
        <p className="text-blue-600 font-medium">Suelta el archivo aqui...</p>
      ) : (
        <>
          <p className="text-gray-700 font-medium mb-1">
            Arrastra un archivo PDF aqui
          </p>
          <p className="text-gray-500 text-sm">
            o haz clic para seleccionar
          </p>
        </>
      )}
    </div>
  )
}
