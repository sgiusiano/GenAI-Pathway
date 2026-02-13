/**
 * Datos mock de extracciones
 *
 * Basado en: results/gemini/DOC_TECNICO_LICITACION_002_multi_item.json
 */

import type { ExtractionRecord } from '../types'

export const mockExtractions: ExtractionRecord[] = [
  {
    id: 'ext-001',
    filename: 'DOC_TECNICO_LICITACION_001.pdf',
    uploadedAt: '2024-12-23T10:30:00Z',
    status: 'completed',
    pageRanges: '1-25',
    result: {
      especificaciones_comunes: {
        generales: {
          tipo: 'Self-regulated Rectifiers and Battery Chargers',
        },
        condiciones_ambientales: {
          temperatura_max_c: 45,
          temperatura_min_c: -10,
          humedad_relativa_max_pct: 80,
        },
        alimentacion: {
          tipo: 'trifásica',
          tension_v: 380,
          frecuencia_hz: 50,
        },
        salida: {
          tension_nominal_v: 110,
        },
        protecciones: {
          sobretensiones_cc: true,
          sobretensiones_ca: true,
          cortocircuito: true,
          sobrecarga: true,
          lvd: true,
        },
        garantia: {
          descripcion: 'Two (2) years from the date of receipt',
          meses: 24,
        },
      },
      items: [
        {
          numero_item: 1,
          cantidad: 4,
          descripcion: 'Rectifier/Battery Charger with Electronic Regulation',
          alimentacion: {
            tipo: 'trifásica',
            tension_v: 380,
            frecuencia_hz: 50,
          },
          salida: {
            tension_nominal_v: 110,
            corriente_nominal_a: 50,
          },
        },
        {
          numero_item: 2,
          cantidad: 2,
          descripcion: 'Rectifier/Battery Charger with Electronic Regulation',
          alimentacion: {
            tipo: 'trifásica',
            tension_v: 380,
            frecuencia_hz: 50,
          },
          salida: {
            tension_nominal_v: 110,
            corriente_nominal_a: 40,
          },
        },
        {
          numero_item: 3,
          cantidad: 1,
          descripcion: 'Rectifier/Battery Charger (Monophasic)',
          alimentacion: {
            tipo: 'monofásica',
            tension_v: 220,
            frecuencia_hz: 50,
          },
          salida: {
            tension_nominal_v: 110,
            corriente_nominal_a: 30,
          },
        },
        {
          numero_item: 4,
          cantidad: 1,
          descripcion: 'Semiautomatic Rectifier with Potentiometer',
          alimentacion: {
            tipo: 'monofásica',
            tension_v: 220,
            frecuencia_hz: 50,
          },
          salida: {
            tension_ajustable: { min: 0, max: 150, unidad: 'V' },
            corriente_ajustable: { min: 0, max: 15, unidad: 'A' },
          },
        },
      ],
    },
  },
  {
    id: 'ext-002',
    filename: 'DOC_TECNICO_LICITACION_002.pdf',
    uploadedAt: '2024-12-22T15:45:00Z',
    status: 'completed',
    result: {
      especificaciones_comunes: {
        generales: {
          tipo: 'Cargador de Baterias Industrial',
        },
        alimentacion: {
          tipo: 'trifásica',
          tension_v: 380,
          frecuencia_hz: 50,
        },
        salida: {
          tension_nominal_v: 48,
          corriente_nominal_a: 100,
        },
      },
      items: [
        {
          numero_item: 1,
          cantidad: 2,
          descripcion: 'Cargador de Baterias 48V 100A',
          salida: {
            tension_nominal_v: 48,
            corriente_nominal_a: 100,
          },
        },
      ],
    },
  },
  {
    id: 'ext-003',
    filename: 'DOC_TECNICO_LICITACION_003.pdf',
    uploadedAt: '2024-12-21T09:00:00Z',
    status: 'processing',
  },
  {
    id: 'ext-004',
    filename: 'DOC_TECNICO_ERROR.pdf',
    uploadedAt: '2024-12-20T14:30:00Z',
    status: 'error',
    errorMessage: 'No se pudo extraer texto del PDF. Verifique que no esté escaneado.',
  },
]
