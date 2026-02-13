/**
 * Servicio de extracciones
 *
 * Funciones para:
 * - Obtener historial de extracciones
 * - Obtener detalle de una extraccion
 * - Subir un nuevo PDF
 *
 * Por ahora usa datos mock. Cuando el API este listo,
 * solo hay que cambiar las implementaciones aca.
 */

import type { ExtractionRecord } from '../types'
import { mockExtractions } from '../mocks/extractions.mock'

// Simula delay de red (entre 500ms y 1500ms)
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const randomDelay = () => delay(500 + Math.random() * 1000)

/**
 * Obtiene todas las extracciones (historial)
 */
export async function getExtractions(): Promise<ExtractionRecord[]> {
  await randomDelay()
  // Ordenar por fecha, mas reciente primero
  return [...mockExtractions].sort(
    (a, b) => new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime()
  )
}

/**
 * Obtiene una extraccion por ID
 */
export async function getExtractionById(id: string): Promise<ExtractionRecord | null> {
  await randomDelay()
  return mockExtractions.find((e) => e.id === id) || null
}

/**
 * Sube un PDF para procesar
 *
 * @param file - Archivo PDF
 * @param pageRanges - Opcional, ej: "1-10, 15-25"
 * @param onProgress - Callback para actualizar progreso (0-100)
 */
export async function uploadPdf(
  file: File,
  pageRanges?: string,
  onProgress?: (progress: number) => void
): Promise<ExtractionRecord> {
  // Simular progreso de upload
  for (let i = 0; i <= 100; i += 10) {
    await delay(200)
    onProgress?.(i)
  }

  // Crear nueva extraccion (mock)
  const newExtraction: ExtractionRecord = {
    id: `ext-${Date.now()}`,
    filename: file.name,
    uploadedAt: new Date().toISOString(),
    status: 'processing',
    pageRanges,
  }

  // Simular que despues de 3 segundos se completa
  setTimeout(() => {
    // En una app real, esto vendria del servidor via polling o websockets
    console.log('Extraccion completada (mock):', newExtraction.id)
  }, 3000)

  return newExtraction
}
