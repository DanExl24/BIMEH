import { http } from '@services/http'
import type {
  AlertaFatigaItem,
  AlertaSanidadItem,
  ProyeccionFuerzaData,
  ParteDiarioData
} from '../types/alertas.types'

export const alertasService = {
  getFatiga: async (
    umbral: number = 30, 
    mes?: string, 
    dia?: string, 
    fecha?: string
  ): Promise<AlertaFatigaItem[]> => {
    const params = new URLSearchParams()
    if (umbral) params.append('umbral', umbral.toString())
    if (mes) params.append('mes', mes)
    if (dia) params.append('dia', dia)
    if (fecha) params.append('fecha', fecha)
    return http.get<AlertaFatigaItem[]>(`/api/alertas/fatiga?${params.toString()}`)
  },

  getSanidad: async (
    diasMin: number = 15, 
    mes?: string, 
    dia?: string, 
    fecha?: string, 
    anio?: number
  ): Promise<AlertaSanidadItem[]> => {
    const params = new URLSearchParams()
    if (diasMin) params.append('dias_min', diasMin.toString())
    if (mes) params.append('mes', mes)
    if (dia) params.append('dia', dia)
    if (fecha) params.append('fecha', fecha)
    if (anio) params.append('anio', anio.toString())
    return http.get<AlertaSanidadItem[]>(`/api/alertas/sanidad?${params.toString()}`)
  },

  getProyeccion: async (
    dias: number = 30, 
    mes?: string, 
    dia?: string, 
    fecha?: string
  ): Promise<ProyeccionFuerzaData> => {
    const params = new URLSearchParams()
    if (dias) params.append('dias', dias.toString())
    if (mes) params.append('mes', mes)
    if (dia) params.append('dia', dia)
    if (fecha) params.append('fecha', fecha)
    return http.get<ProyeccionFuerzaData>(`/api/alertas/proyeccion?${params.toString()}`)
  },

  getParteDiario: async (
    mes?: string, 
    dia?: string, 
    fecha?: string
  ): Promise<ParteDiarioData> => {
    const params = new URLSearchParams()
    if (mes) params.append('mes', mes)
    if (dia) params.append('dia', dia)
    if (fecha) params.append('fecha', fecha)
    return http.get<ParteDiarioData>(`/api/alertas/parte-diario?${params.toString()}`)
  },

  descargarPdfParteDiario: (mes?: string, dia?: string, fecha?: string): string => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const params = new URLSearchParams()
    if (mes) params.append('mes', mes)
    if (dia) params.append('dia', dia)
    if (fecha) params.append('fecha', fecha)
    const queryString = params.toString() ? `?${params.toString()}` : ''
    return `${base}/api/exportar/pdf/parte-diario${queryString}`
  }
}
