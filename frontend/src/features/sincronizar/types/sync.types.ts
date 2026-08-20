export interface SyncLog {
  file: string
  status: 'success' | 'skipped' | 'error'
  detail: string
}

export interface SyncResponse {
  status: 'success' | 'error' | 'conflict' | 'ok'
  message?: string
  detail?: string
  errors?: string[]
  logs?: SyncLog[]
  conflicts?: string[]
  auto_dismiss_seconds?: number
  registros_procesados?: number
  novedades_insertadas?: number
}
