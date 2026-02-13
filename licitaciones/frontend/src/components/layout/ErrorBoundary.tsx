import { Component, type ReactNode } from 'react'
import { AlertTriangle, RotateCcw } from 'lucide-react'

/**
 * ErrorBoundary: Captura errores de React y muestra un fallback
 *
 * En React, si un componente tira un error, toda la app se rompe.
 * ErrorBoundary captura esos errores y muestra un mensaje amigable.
 *
 * NOTA: Debe ser un Class Component porque los hooks no pueden
 * capturar errores de rendering (limitacion de React).
 */

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  // Este metodo se llama cuando hay un error en un child
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  // Opcional: loggear el error a un servicio
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    // Aqui podrias enviar el error a un servicio como Sentry
  }

  // Reiniciar el estado para intentar de nuevo
  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>

            <h1 className="text-xl font-bold text-gray-900 mb-2">
              Algo salio mal
            </h1>

            <p className="text-gray-600 mb-6">
              Ocurrio un error inesperado. Podes intentar recargar la pagina
              o volver a intentar.
            </p>

            {/* Mostrar error en desarrollo */}
            {import.meta.env.DEV && this.state.error && (
              <pre className="text-left text-xs bg-gray-100 p-3 rounded mb-4 overflow-auto max-h-32">
                {this.state.error.message}
              </pre>
            )}

            <div className="flex gap-3 justify-center">
              <button
                onClick={this.handleReset}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                Intentar de nuevo
              </button>

              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Recargar pagina
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
