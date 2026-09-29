import { http } from '@services/http'
import type {
  IAStatusResponse,
  IAChatResponse,
  IAApreciacionResponse
} from '../types/ia.types'

export const iaService = {
  /**
   * Consulta el estado de conectividad con Ollama en el backend
   */
  obtenerEstado: async (): Promise<IAStatusResponse> => {
    return http.get<IAStatusResponse>('/api/ia/status')
  },

  /**
   * Envía una consulta en lenguaje natural al Asistente IA
   */
  enviarMensaje: async (message: string): Promise<IAChatResponse> => {
    return http.post<IAChatResponse>('/api/ia/chat', { message })
  },

  /**
   * Genera una Apreciación de Situación de Personal para la Comandancia
   */
  generarApreciacion: async (mes: string = 'TODOS'): Promise<IAApreciacionResponse> => {
    return http.post<IAApreciacionResponse>('/api/ia/apreciacion', { mes })
  }
}
