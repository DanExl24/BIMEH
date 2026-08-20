import { http } from '@services/http'
import type { CalendarioItem, PersonalDia, HeatmapResponse } from '@types'

export const cronologiaService = {
  getCalendario: async (mes: string): Promise<CalendarioItem[]> => {
    return http.get<CalendarioItem[]>(`/api/reportes/calendario?mes=${mes}`)
  },

  getReporteDia: async (fecha: string): Promise<PersonalDia[]> => {
    return http.get<PersonalDia[]>(`/api/reportes/dia?fecha=${fecha}`)
  },

  getHeatmapMensual: async (mes: string): Promise<HeatmapResponse> => {
    return http.get<HeatmapResponse>(`/api/stats/heatmap?mes=${mes}`)
  }
}
