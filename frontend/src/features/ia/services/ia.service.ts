import { http } from '@services/http'
import type {
  IAStatusResponse,
  IAChatResponse,
  IAApreciacionResponse,
  ActiveMilitar
} from '../types/ia.types'

export const iaService = {
  /**
   * Consulta el estado de conectividad con Ollama en el backend
   */
  obtenerEstado: async (): Promise<IAStatusResponse> => {
    return http.get<IAStatusResponse>('/api/ia/status')
  },

  /**
   * Envía una consulta en lenguaje natural al Asistente IA junto con historial previo y militar en contexto
   */
  enviarMensaje: async (
    message: string,
    history?: any[],
    activeMilitar?: ActiveMilitar | null,
    signal?: AbortSignal,
    model?: string
  ): Promise<IAChatResponse> => {
    return http.post<IAChatResponse>(
      '/api/ia/chat',
      {
        message,
        history,
        active_militar: activeMilitar,
        model
      },
      { signal }
    )
  },

  /**
   * Genera una Apreciación de Situación de Personal para la Comandancia
   */
  generarApreciacion: async (
    mes: string = 'TODOS',
    signal?: AbortSignal,
    model?: string
  ): Promise<IAApreciacionResponse> => {
    return http.post<IAApreciacionResponse>('/api/ia/apreciacion', { mes, model }, { signal })
  },

  /**
   * Actualiza el modelo activo de Gemini/Ollama o la URL en el backend
   */
  actualizarConfig: async (baseUrl?: string, model?: string): Promise<IAStatusResponse> => {
    return http.post<IAStatusResponse>('/api/ia/config', { base_url: baseUrl, model })
  }
}
