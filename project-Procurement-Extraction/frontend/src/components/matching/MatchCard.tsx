import { Package, Check, X, AlertTriangle } from 'lucide-react'
import type { MatchResult } from '../../types'
import { Card, Badge } from '../ui'

/**
 * MatchCard: Muestra un item y los productos que matchean
 */

interface MatchCardProps {
  match: MatchResult
}

// Funcion para determinar el color segun el score
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 bg-green-100'
  if (score >= 50) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
}

function getScoreIcon(score: number) {
  if (score >= 80) return Check
  if (score >= 50) return AlertTriangle
  return X
}

export default function MatchCard({ match }: MatchCardProps) {
  const { item, productos, bestScore, notas } = match
  const ScoreIcon = getScoreIcon(bestScore)

  return (
    <Card>
      <Card.Body>
        {/* Header del item */}
        <div className="flex items-start gap-4 mb-4">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-blue-600" />
            </div>
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="info">Item {item.numero_item}</Badge>
              {item.cantidad && (
                <span className="text-sm text-gray-500">Cantidad: {item.cantidad}</span>
              )}
            </div>
            <p className="font-medium text-gray-900">{item.descripcion}</p>
            <div className="flex gap-4 mt-1 text-sm text-gray-600">
              {item.salida?.tension_nominal_v && (
                <span>Tension: {item.salida.tension_nominal_v}V</span>
              )}
              {item.salida?.corriente_nominal_a && (
                <span>Corriente: {item.salida.corriente_nominal_a}A</span>
              )}
            </div>
          </div>

          {/* Score Badge */}
          <div
            className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(bestScore)}`}
          >
            <ScoreIcon className="w-4 h-4" />
            {bestScore}%
          </div>
        </div>

        {/* Productos que matchean */}
        {productos.length > 0 ? (
          <div className="border-t border-gray-100 pt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-3">
              Productos Coincidentes ({productos.length})
            </h4>
            <div className="space-y-2">
              {productos.map((producto) => (
                <div
                  key={producto.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">{producto.codigo}</p>
                    <p className="text-sm text-gray-500">
                      {producto.marca} - {producto.modelo}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">
                      {producto.tension_nominal}V / {producto.corriente_nominal}A
                    </p>
                    <p className="text-sm text-gray-500">
                      Regulador: {producto.regulador_diodos}
                    </p>
                  </div>
                  <div
                    className={`ml-4 px-2 py-1 rounded text-xs font-medium ${getScoreColor(producto.score)}`}
                  >
                    {producto.score}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="border-t border-gray-100 pt-4">
            <p className="text-sm text-gray-500 text-center py-2">
              No se encontraron productos coincidentes
            </p>
          </div>
        )}

        {/* Notas */}
        {notas && (
          <p className="mt-3 text-sm text-gray-500 italic">{notas}</p>
        )}
      </Card.Body>
    </Card>
  )
}
