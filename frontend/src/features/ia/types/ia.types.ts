export interface IAStatusResponse {
  online: boolean
  base_url: string
  model_configured: string
  model_available: boolean
  models_installed: string[]
  error?: string | null
}

export interface IAChatMessage {
  id: string
  sender: 'user' | 'assistant'
  text: string
  type?: 'conversation' | 'data' | 'error'
  sql?: string | null
  columns?: string[]
  rows?: Record<string, any>[]
  total_records?: number
  timestamp: string
  elapsed_seconds?: number
  isError?: boolean
}

export interface ActiveMilitar {
  cedula: string | number
  nombre: string
}

export interface IAChatResponse {
  status: 'success' | 'error'
  type: 'conversation' | 'data' | 'error'
  answer: string
  sql?: string | null
  columns: string[]
  rows: Record<string, any>[]
  total_records: number
  model: string
  elapsed_seconds?: number
  active_militar?: ActiveMilitar | null
}

export interface IAApreciacionKpis {
  total_personal: number
  total_activos: number
  total_retirados: number
  companias: Array<{ compania: string; total: number }>
  top_novedades: Array<{ novedad: string; dias: number; efectivos: number }>
  casos_criticos: Array<{ cedula: number; nombre: string; novedad: string; dias: number }>
}

export interface IAApreciacionResponse {
  status: 'success' | 'error'
  periodo: string
  kpis: IAApreciacionKpis
  apreciacion: string
  fecha_generacion: string
}
