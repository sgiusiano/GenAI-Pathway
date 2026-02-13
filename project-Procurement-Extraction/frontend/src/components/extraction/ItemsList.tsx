import { Package } from 'lucide-react'
import type { ItemLicitado } from '../../types'
import { Card, Badge } from '../ui'

/**
 * ItemsList: Muestra la lista de items de una licitacion
 */

interface ItemsListProps {
  items: ItemLicitado[]
}

export default function ItemsList({ items }: ItemsListProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No hay items en esta licitacion
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {items.map((item, index) => (
        <Card key={item.numero_item || index}>
          <Card.Body>
            <div className="flex items-start gap-4">
              {/* Icono y numero */}
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Package className="w-5 h-5 text-blue-600" />
                </div>
              </div>

              {/* Contenido */}
              <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="info">Item {item.numero_item || index + 1}</Badge>
                  {item.cantidad && (
                    <Badge variant="neutral">Cantidad: {item.cantidad}</Badge>
                  )}
                </div>

                {/* Descripcion */}
                {item.descripcion && (
                  <p className="text-gray-900 font-medium mb-3">
                    {item.descripcion}
                  </p>
                )}

                {/* Specs del item */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  {/* Alimentacion */}
                  {item.alimentacion && (
                    <div>
                      <dt className="text-gray-500">Alimentacion</dt>
                      <dd className="text-gray-900 font-medium">
                        {item.alimentacion.tipo}
                        {item.alimentacion.tension_v && ` ${item.alimentacion.tension_v}V`}
                        {item.alimentacion.frecuencia_hz && ` ${item.alimentacion.frecuencia_hz}Hz`}
                      </dd>
                    </div>
                  )}

                  {/* Salida - Tension */}
                  {item.salida?.tension_nominal_v && (
                    <div>
                      <dt className="text-gray-500">Tension Salida</dt>
                      <dd className="text-gray-900 font-medium">
                        {item.salida.tension_nominal_v} V
                      </dd>
                    </div>
                  )}

                  {/* Salida - Corriente */}
                  {item.salida?.corriente_nominal_a && (
                    <div>
                      <dt className="text-gray-500">Corriente Salida</dt>
                      <dd className="text-gray-900 font-medium">
                        {item.salida.corriente_nominal_a} A
                      </dd>
                    </div>
                  )}

                  {/* Tension Ajustable */}
                  {item.salida?.tension_ajustable && (
                    <div>
                      <dt className="text-gray-500">Tension Ajustable</dt>
                      <dd className="text-gray-900 font-medium">
                        {item.salida.tension_ajustable.min} - {item.salida.tension_ajustable.max} {item.salida.tension_ajustable.unidad}
                      </dd>
                    </div>
                  )}

                  {/* Corriente Ajustable */}
                  {item.salida?.corriente_ajustable && (
                    <div>
                      <dt className="text-gray-500">Corriente Ajustable</dt>
                      <dd className="text-gray-900 font-medium">
                        {item.salida.corriente_ajustable.min} - {item.salida.corriente_ajustable.max} {item.salida.corriente_ajustable.unidad}
                      </dd>
                    </div>
                  )}

                  {/* Marca/Modelo */}
                  {(item.marca || item.modelo) && (
                    <div>
                      <dt className="text-gray-500">Marca/Modelo</dt>
                      <dd className="text-gray-900 font-medium">
                        {[item.marca, item.modelo].filter(Boolean).join(' - ')}
                      </dd>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </Card.Body>
        </Card>
      ))}
    </div>
  )
}
