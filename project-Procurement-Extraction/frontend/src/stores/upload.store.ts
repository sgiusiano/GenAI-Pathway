import { create } from 'zustand'

/**
 * Store de Zustand para el estado del upload
 *
 * Zustand es como un "useState global" - cualquier componente
 * puede leer y modificar este estado.
 *
 * Ventajas sobre Context:
 * - Mas simple (menos boilerplate)
 * - Mejor performance (solo re-renderiza lo necesario)
 * - Facil de usar fuera de componentes
 */

// Tipo del estado
interface UploadState {
  // Datos
  file: File | null
  pageRanges: string
  progress: number
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error'
  errorMessage: string | null
  extractionId: string | null

  // Acciones (funciones para modificar el estado)
  setFile: (file: File | null) => void
  setPageRanges: (ranges: string) => void
  setProgress: (progress: number) => void
  setStatus: (status: UploadState['status']) => void
  setError: (message: string) => void
  setExtractionId: (id: string) => void
  reset: () => void
}

// Estado inicial
const initialState = {
  file: null,
  pageRanges: '',
  progress: 0,
  status: 'idle' as const,
  errorMessage: null,
  extractionId: null,
}

// Crear el store
export const useUploadStore = create<UploadState>((set) => ({
  ...initialState,

  // Setters simples
  setFile: (file) => set({ file }),
  setPageRanges: (pageRanges) => set({ pageRanges }),
  setProgress: (progress) => set({ progress }),
  setStatus: (status) => set({ status }),
  setExtractionId: (extractionId) => set({ extractionId }),

  // Setter de error (tambien cambia el status)
  setError: (errorMessage) => set({ errorMessage, status: 'error' }),

  // Reset a estado inicial
  reset: () => set(initialState),
}))
