import type { EspecificacionesComunes } from '../../types'
import { Card } from '../ui'

/**
 * SpecsPanel: Muestra especificaciones comunes en secciones
 */

interface SpecsPanelProps {
  specs: EspecificacionesComunes
}

// Componente para mostrar un grupo de campos
function SpecSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="space-y-2">
      <h4 className="font-medium text-gray-900 border-b border-gray-200 pb-1">
        {title}
      </h4>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        {children}
      </dl>
    </div>
  )
}

// Componente para un campo individual
function SpecField({ label, value }: { label: string; value: React.ReactNode }) {
  if (value === undefined || value === null) return null

  return (
    <>
      <dt className="text-gray-500">{label}</dt>
      <dd className="text-gray-900 font-medium">
        {typeof value === 'boolean' ? (value ? 'Si' : 'No') : value}
      </dd>
    </>
  )
}

export default function SpecsPanel({ specs }: SpecsPanelProps) {
  return (
    <Card>
      <Card.Body className="space-y-6">
        {/* Generales */}
        {specs.generales && (
          <SpecSection title="Generales">
            <SpecField label="Tipo" value={specs.generales.tipo} />
            <SpecField label="Marca" value={specs.generales.marca} />
            <SpecField label="Modelo" value={specs.generales.modelo} />
            <SpecField label="Normas" value={specs.generales.normas_fabricacion} />
            <SpecField label="Origen" value={specs.generales.origen} />
          </SpecSection>
        )}

        {/* Condiciones Ambientales */}
        {specs.condiciones_ambientales && (
          <SpecSection title="Condiciones Ambientales">
            <SpecField
              label="Temperatura"
              value={
                specs.condiciones_ambientales.temperatura_min_c !== undefined &&
                specs.condiciones_ambientales.temperatura_max_c !== undefined
                  ? `${specs.condiciones_ambientales.temperatura_min_c}°C a ${specs.condiciones_ambientales.temperatura_max_c}°C`
                  : undefined
              }
            />
            <SpecField
              label="Humedad Max"
              value={
                specs.condiciones_ambientales.humedad_relativa_max_pct
                  ? `${specs.condiciones_ambientales.humedad_relativa_max_pct}%`
                  : undefined
              }
            />
            <SpecField
              label="Altitud"
              value={
                specs.condiciones_ambientales.altura_snm_m
                  ? `${specs.condiciones_ambientales.altura_snm_m} m.s.n.m.`
                  : undefined
              }
            />
          </SpecSection>
        )}

        {/* Alimentacion */}
        {specs.alimentacion && (
          <SpecSection title="Alimentacion">
            <SpecField label="Tipo" value={specs.alimentacion.tipo} />
            <SpecField
              label="Tension"
              value={specs.alimentacion.tension_v ? `${specs.alimentacion.tension_v} V` : undefined}
            />
            <SpecField
              label="Frecuencia"
              value={specs.alimentacion.frecuencia_hz ? `${specs.alimentacion.frecuencia_hz} Hz` : undefined}
            />
          </SpecSection>
        )}

        {/* Salida */}
        {specs.salida && (
          <SpecSection title="Salida">
            <SpecField
              label="Tension Nominal"
              value={specs.salida.tension_nominal_v ? `${specs.salida.tension_nominal_v} V` : undefined}
            />
            <SpecField
              label="Corriente Nominal"
              value={specs.salida.corriente_nominal_a ? `${specs.salida.corriente_nominal_a} A` : undefined}
            />
          </SpecSection>
        )}

        {/* Protecciones */}
        {specs.protecciones && (
          <SpecSection title="Protecciones">
            <SpecField label="Sobretensiones CC" value={specs.protecciones.sobretensiones_cc} />
            <SpecField label="Sobretensiones CA" value={specs.protecciones.sobretensiones_ca} />
            <SpecField label="Cortocircuito" value={specs.protecciones.cortocircuito} />
            <SpecField label="Sobrecarga" value={specs.protecciones.sobrecarga} />
            <SpecField label="LVD" value={specs.protecciones.lvd} />
          </SpecSection>
        )}

        {/* Garantia */}
        {specs.garantia && (
          <SpecSection title="Garantia">
            <SpecField
              label="Duracion"
              value={specs.garantia.meses ? `${specs.garantia.meses} meses` : undefined}
            />
            <SpecField label="Descripcion" value={specs.garantia.descripcion} />
          </SpecSection>
        )}
      </Card.Body>
    </Card>
  )
}
