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
export const fetchKPIs = (mes?: string, dia?: string, fecha?: string) => dashboardService.getKPIs(mes, dia, fecha)
export const fetchCambios = (mes?: string, dia?: string, fecha?: string) => dashboardService.getCambios(mes, dia, fecha)
export const fetchEvolucion = (mes?: string, dia?: string) => dashboardService.getEvolucion(mes, dia)
export const fetchNovedadesFrecuentes = (mes?: string, dia?: string, fecha?: string) => dashboardService.getNovedadesFrecuentes(mes, dia, fecha)
export const fetchDistribucion = (mes?: string, dia?: string, fecha?: string) => dashboardService.getDistribucion(mes, dia, fecha)

export const buscarPersonal = (q: string) => personalService.buscar(q)
export const fetchPersonalDetalle = (cedula: number) => personalService.getDetalle(cedula)
export const fetchPersonalHistorial = (cedula: number) => personalService.getHistorial(cedula)
export const fetchPersonalAcumulado = (cedula: number) => personalService.getAcumulado(cedula)

export const fetchCalendario = (mes: string) => cronologiaService.getCalendario(mes)
export const fetchReporteDia = (fecha: string) => cronologiaService.getReporteDia(fecha)
export const fetchStatsHeatmap = (mes: string) => cronologiaService.getHeatmapMensual(mes)

export const fetchStatsRanking = () => estadisticasService.getRankings()

export const fetchDriveStatus = () => authService.getDriveStatus()
export const fetchOAuthUrl = (redirectUri: string) => authService.getOAuthUrl(redirectUri)

export const uploadReportFile = (formData: FormData) => syncService.uploadReportFile(formData)
export const getExportUrl = (tipo: string, format: 'excel' | 'pdf' | 'csv', params: Record<string, string>) => reportesService.getExportUrl(tipo, format, params)
