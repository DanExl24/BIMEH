export interface User {
  nombre: string
  correo: string
  roles: string[]
}

export interface LoginCredentials {
  correo: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  usuario: User
}

export interface DriveStatusResponse {
  connected: boolean
  message?: string
}

export interface OAuthUrlResponse {
  auth_url: string
}
