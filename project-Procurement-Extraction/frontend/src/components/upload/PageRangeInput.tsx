import { useUploadStore } from '../../stores/upload.store'

/**
 * PageRangeInput: Input para especificar paginas a procesar
 *
 * Formato: "1-10, 15-25, 30"
 * Si esta vacio, se procesan todas las paginas
 */

export default function PageRangeInput() {
  const { pageRanges, setPageRanges, status } = useUploadStore()

  const isDisabled = status === 'uploading' || status === 'processing'

  return (
    <div className="space-y-2">
      <label htmlFor="pageRanges" className="block text-sm font-medium text-gray-700">
        Paginas a procesar (opcional)
      </label>
      <input
        type="text"
        id="pageRanges"
        value={pageRanges}
        onChange={(e) => setPageRanges(e.target.value)}
        disabled={isDisabled}
        placeholder="Ej: 1-10, 15-25, 30"
        className={`
          w-full px-4 py-2
          border border-gray-300 rounded-lg
          text-gray-900 placeholder-gray-400
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
          disabled:bg-gray-100 disabled:cursor-not-allowed
        `}
      />
      <p className="text-xs text-gray-500">
        Deja vacio para procesar todo el documento. Formato: 1-10, 15-25, 30
      </p>
    </div>
  )
}
