import { http } from '@services/http'
import type { 
  KPIData, 
  CambiosResponse, 
  EvolucionItem, 
  NovedadFrecuente, 
  DistribucionItem 
} from '@/types'

export const dashboardService = {
  getKPIs: async (mes?: string, dia?: string, fecha?: string): Promise<KPIData> => {
    let url = '/api/dashboard/kpis?'
    if (fecha) {
      url += `fecha=${fecha}`
    } else {
      const params: string[] = []
      if (typeof mes === 'string' && mes) params.push(`mes=${mes}`)
      if (typeof dia === 'string' && dia) params.push(`dia=${dia}`)
      url += params.join('&')
    }
    return http.get<KPIData>(url)
  },

  getCambios: async (mes?: string, dia?: string, fecha?: string): Promise<CambiosResponse> => {
    let url = '/api/dashboard/cambios?'
    if (fecha) {
      url += `fecha=${fecha}`
    } else {
      const params: string[] = []
      if (typeof mes === 'string' && mes) params.push(`mes=${mes}`)
      if (typeof dia === 'string' && dia) params.push(`dia=${dia}`)
      url += params.join('&')
    }
    return http.get<CambiosResponse>(url)
  },

  getEvolucion: async (mes?: string, dia?: string): Promise<EvolucionItem[]> => {
    const params: string[] = []
    if (typeof mes === 'string' && mes) params.push(`mes=${mes}`)
    if (typeof dia === 'string' && dia) params.push(`dia=${dia}`)
    return http.get<EvolucionItem[]>(`/api/dashboard/evolucion?${params.join('&')}`)
  },

  getNovedadesFrecuentes: async (mes?: string, dia?: string, fecha?: string): Promise<NovedadFrecuente[]> => {
    let url = '/api/dashboard/novedades-frecuentes?'
    if (fecha) {
      url += `fecha=${fecha}`
    } else {
      const params: string[] = []
      if (typeof mes === 'string' && mes) params.push(`mes=${mes}`)
      if (typeof dia === 'string' && dia) params.push(`dia=${dia}`)
      url += params.join('&')
    }
    return http.get<NovedadFrecuente[]>(url)
  },

  getDistribucion: async (mes?: string, dia?: string, fecha?: string): Promise<DistribucionItem[]> => {
    let url = '/api/dashboard/distribucion?'
    if (fecha) {
      url += `fecha=${fecha}`
    } else {
      const params: string[] = []
      if (typeof mes === 'string' && mes) params.push(`mes=${mes}`)
      if (typeof dia === 'string' && dia) params.push(`dia=${dia}`)
      url += params.join('&')
    }
    return http.get<DistribucionItem[]>(url)
  }
}
