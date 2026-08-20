import { http, fetchWithAuth } from './http'
import { authService } from '@features/auth/services/auth.service'
import { dashboardService } from '@features/dashboard/services/dashboard.service'
import { personalService } from '@features/personal/services/personal.service'
import { cronologiaService } from '@features/cronologia/services/cronologia.service'
import { syncService } from '@features/sincronizar/services/sync.service'
import { estadisticasService } from '@features/estadisticas/services/estadisticas.service'
import { reportesService } from '@features/reportes/services/reportes.service'

export { fetchWithAuth }

export async function fetchFechas(): Promise<string[]> {
  return http.get<string[]>('/api/fechas')
}

// Re-exports delegating to specialized domain services
export const fetchKPIs = dashboardService.getKPIs
export const fetchCambios = dashboardService.getCambios
export const fetchEvolucion = dashboardService.getEvolucion
export const fetchNovedadesFrecuentes = dashboardService.getNovedadesFrecuentes
export const fetchDistribucion = dashboardService.getDistribucion

export const buscarPersonal = personalService.buscar
export const fetchPersonalDetalle = personalService.getDetalle
export const fetchPersonalHistorial = personalService.getHistorial
export const fetchPersonalAcumulado = personalService.getAcumulado

export const fetchCalendario = cronologiaService.getCalendario
export const fetchReporteDia = cronologiaService.getReporteDia
export const fetchStatsHeatmap = cronologiaService.getHeatmapMensual

export const fetchStatsRanking = estadisticasService.getRankings

export const fetchDriveStatus = authService.getDriveStatus
export const fetchOAuthUrl = authService.getOAuthUrl

export const uploadReportFile = syncService.uploadReportFile
export const getExportUrl = reportesService.getExportUrl
