import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'

// Paginas
import UploadPage from './pages/UploadPage'
import HistoryPage from './pages/HistoryPage'
import ExtractionDetailPage from './pages/ExtractionDetailPage'
import MatchingPage from './pages/MatchingPage'

// Layout y Error Boundary
import MainLayout from './components/layout/MainLayout'
import ErrorBoundary from './components/layout/ErrorBoundary'

// Cliente de React Query (maneja cache de datos)
const queryClient = new QueryClient()

function App() {
  return (
    // ErrorBoundary: Captura errores de React y muestra fallback
    <ErrorBoundary>
      {/* QueryClientProvider: Provee el cliente a toda la app */}
      <QueryClientProvider client={queryClient}>
        {/* BrowserRouter: Habilita navegacion por URL */}
        <BrowserRouter>
          {/* Routes: Define las rutas disponibles */}
          <Routes>
            {/* Route con element={<MainLayout />}: Layout que envuelve todas las paginas */}
            <Route element={<MainLayout />}>
              {/* index: Ruta por defecto (/) */}
              <Route index element={<UploadPage />} />
              <Route path="history" element={<HistoryPage />} />
              <Route path="extraction/:id" element={<ExtractionDetailPage />} />
              <Route path="extraction/:id/matching" element={<MatchingPage />} />
            </Route>
          </Routes>
        </BrowserRouter>

        {/* Toaster: Renderiza los toasts (posicion arriba-derecha) */}
        <Toaster
          position="top-right"
          richColors
          closeButton
          toastOptions={{
            duration: 4000, // 4 segundos
          }}
        />
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
