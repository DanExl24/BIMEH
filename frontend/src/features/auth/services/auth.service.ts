import { http, getApiBase } from '@services/http'
import type { DriveStatusResponse, OAuthUrlResponse } from '@types'

export interface LoginCredentials {
  correo: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: {
    nombre: string
    correo: string
    roles: string[]
  }
}

export const authService = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    return http.post<LoginResponse>('/api/auth/login', credentials)
  },

  checkMe: async (): Promise<{ nombre: string; correo: string; roles: string[] }> => {
    return http.get('/api/auth/me')
  },

  getDriveStatus: async (): Promise<DriveStatusResponse> => {
    return http.get<DriveStatusResponse>('/api/auth/drive-status')
  },

  getOAuthUrl: async (redirectUri: string): Promise<OAuthUrlResponse> => {
    const res = await fetch(`${getApiBase()}/api/sincronizar/oauth/url?redirect_uri=${encodeURIComponent(redirectUri)}`)
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || `Error en el servidor (${res.status})`)
    }
    return res.json()
  }
}
