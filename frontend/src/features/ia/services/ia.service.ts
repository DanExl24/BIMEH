import { http } from '@services/http'
import type {
  IAStatusResponse,
  IAChatResponse,
  IAApreciacionResponse,
  ActiveMilitar,
  IASesion,
  IAMensajePersistente,
  ChatContext
} from '../types/ia.types'

export const iaService = {
  /**
   * Consulta el estado de conectividad con Gemini / Ollama en el backend
   */
  obtenerEstado: async (): Promise<IAStatusResponse> => {
    return http.get<IAStatusResponse>('/api/ia/status')
  },

  /**
   * Lista las sesiones de chat persistentes
   */
  obtenerSesiones: async (): Promise<IASesion[]> => {
    return http.get<IASesion[]>('/api/ia/sesiones')
  },

  /**
   * Crea una nueva sesión vacía de conversación
   */
  crearSesion: async (titulo: string = 'Nueva conversación'): Promise<IASesion> => {
    return http.post<IASesion>('/api/ia/sesiones', { titulo })
  },

  /**
   * Obtiene todos los mensajes de una sesión existente
   */
  obtenerMensajesSesion: async (
    sessionId: number
  ): Promise<{ id: number; titulo: string; creado_en: string; mensajes: IAMensajePersistente[] }> => {
    return http.get<{ id: number; titulo: string; creado_en: string; mensajes: IAMensajePersistente[] }>(
      `/api/ia/sesiones/${sessionId}`
    )
  },

  /**
   * Elimina una sesión de chat y sus mensajes
   */
  eliminarSesion: async (sessionId: number): Promise<{ status: string; message: string }> => {
    return http.delete<{ status: string; message: string }>(`/api/ia/sesiones/${sessionId}`)
  },

  /**
   * Envía una consulta en lenguaje natural al Asistente IA junto con historial previo,
   * contexto de pantalla, militar activo e id de sesión.
   */
  enviarMensaje: async (
    message: string,
    history?: any[],
    activeMilitar?: ActiveMilitar | null,
    signal?: AbortSignal,
    model?: string,
    mode: 'chat' | 'report' | string = 'chat',
    sessionId?: number | null,
    context?: ChatContext
  ): Promise<IAChatResponse> => {
    return http.post<IAChatResponse>(
      '/api/ia/chat',
      {
        message,
        history,
        active_militar: activeMilitar,
        model,
        mode,
        session_id: sessionId,
        context
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
