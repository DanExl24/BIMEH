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
   * Envía una consulta en lenguaje natural al Asistente IA junto con historial previo
   */
  enviarMensaje: async (message: string, history?: any[]): Promise<IAChatResponse> => {
    return http.post<IAChatResponse>('/api/ia/chat', { message, history })
  },

  /**
   * Genera una Apreciación de Situación de Personal para la Comandancia
   */
  generarApreciacion: async (mes: string = 'TODOS'): Promise<IAApreciacionResponse> => {
    return http.post<IAApreciacionResponse>('/api/ia/apreciacion', { mes })
  },

  /**
   * Actualiza la URL de Ollama / Cloudflare Tunnel en el backend
   */
  actualizarConfig: async (baseUrl: string, model?: string): Promise<IAStatusResponse> => {
    return http.post<IAStatusResponse>('/api/ia/config', { base_url: baseUrl, model })
  }
}
