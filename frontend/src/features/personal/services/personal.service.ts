import { http } from '@services/http'
import type { 
  PersonalSearchResult, 
  PersonalDetalle, 
  HistorialRegistro, 
  AcumuladoNovedad 
} from '@types'

export const personalService = {
  buscar: async (q: string): Promise<PersonalSearchResult[]> => {
    return http.get<PersonalSearchResult[]>(`/api/personal/buscar?q=${encodeURIComponent(q)}`)
  },

  getDetalle: async (cedula: number): Promise<PersonalDetalle> => {
    return http.get<PersonalDetalle>(`/api/personal/${cedula}`)
  },

  getHistorial: async (cedula: number): Promise<HistorialRegistro[]> => {
    return http.get<HistorialRegistro[]>(`/api/personal/${cedula}/historial`)
  },

  getAcumulado: async (cedula: number): Promise<AcumuladoNovedad[]> => {
    return http.get<AcumuladoNovedad[]>(`/api/personal/${cedula}/acumulado`)
  }
}
