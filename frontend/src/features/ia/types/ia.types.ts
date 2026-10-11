export interface IAModelInfo {
  id: string
  name: string
  rpd: number
  rpm: number
  tpm: string
  category: string
  description: string
  recommended?: boolean
  badge?: string
  active?: boolean
}

export interface IAStatusResponse {
  online: boolean
  backend?: string
  base_url?: string
  model_configured: string
  model_available?: boolean
  models_installed?: string[]
  api_key_configured?: boolean
  available_models?: IAModelInfo[]
  error?: string | null
}

export interface IAReportInfo {
  tipo: 'consolidado_mensual' | 'mes' | 'dia' | 'personal' | 'personal_db' | 'subnovedades' | string
  formato_solicitado: 'excel' | 'pdf'
  titulo: string
  descripcion?: string
  url_excel?: string
  url_pdf?: string
  url_csv?: string
  parametros?: Record<string, any>
  mensaje?: string
}

export interface IAChatMessage {
  id: string
  sender: 'user' | 'assistant'
  text: string
  type?: 'conversation' | 'data' | 'report' | 'error'
  report_info?: IAReportInfo
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
  type: 'conversation' | 'data' | 'report' | 'error'
  answer: string
  report_info?: IAReportInfo
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
