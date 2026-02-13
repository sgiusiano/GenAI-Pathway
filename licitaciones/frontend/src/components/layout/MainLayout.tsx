import { Outlet, Link, useLocation } from 'react-router-dom'
import { Upload, History, Zap, Bot } from 'lucide-react'

/**
 * MainLayout: Estructura principal de la app
 *
 * - Header con logo y navegacion
 * - <Outlet /> es donde se renderiza la pagina actual (UploadPage, HistoryPage, etc.)
 */
export default function MainLayout() {
  const location = useLocation() // Hook para saber la URL actual

  // Funcion helper para saber si un link esta activo
  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo LiciBot */}
          <Link to="/" className="flex items-center gap-3 group">
            {/* Icono con fondo */}
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow">
                <Zap className="w-6 h-6 text-white" fill="currentColor" />
              </div>
              {/* Mini bot en la esquina */}
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center border-2 border-white">
                <Bot className="w-3 h-3 text-white" />
              </div>
            </div>
            {/* Nombre */}
            <div>
              <span className="text-xl font-bold text-gray-900">LiciBot</span>
              <span className="hidden sm:block text-xs text-gray-500">Extractor de Licitaciones</span>
            </div>
          </Link>

          {/* Navegacion */}
          <nav className="flex gap-4">
            <Link
              to="/"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/') && !isActive('/history') && !isActive('/extraction')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Upload className="w-4 h-4" />
              Upload
            </Link>
            <Link
              to="/history"
              className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/history') || isActive('/extraction')
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <History className="w-4 h-4" />
              Historial
            </Link>
          </nav>
        </div>
      </header>

      {/* Contenido principal - aqui se renderiza la pagina actual */}
      <main className="flex-1 p-6">
        <div className="max-w-7xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
