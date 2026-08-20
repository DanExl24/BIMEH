import type { SyncLog } from '../types'

/**
 * Genera el reporte en formato texto plano a partir de los logs de sincronización de Drive
 */
export function generateSyncLogText(logs: SyncLog[]): string {
  if (!logs || logs.length === 0) return ''

  let text = `REPORTE DE SINCRONIZACIÓN DE GOOGLE DRIVE - BIMEH\n`
  text += `Fecha de ejecución: ${new Date().toLocaleString()}\n`
  text += `=========================================================\n\n`

  logs.forEach((log) => {
    const statusUpper = (log.status || '').toUpperCase()
    text += `[${statusUpper}] ${log.file}\n`
    text += `Detalle: ${log.detail}\n`
    text += `---------------------------------------------------------\n`
  })

  return text
}
