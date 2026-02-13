/**
 * Progress: Barra de progreso
 *
 * Uso:
 * <Progress value={75} /> // 75% completo
 */

interface ProgressProps {
  value: number // 0-100
  className?: string
  showLabel?: boolean
}

export default function Progress({ value, className = '', showLabel = false }: ProgressProps) {
  // Asegurar que value este entre 0 y 100
  const clampedValue = Math.min(100, Math.max(0, value))

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between mb-1">
          <span className="text-sm font-medium text-gray-700">Progreso</span>
          <span className="text-sm font-medium text-gray-700">{clampedValue}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${clampedValue}%` }}
        />
      </div>
    </div>
  )
}
