import { http } from '@services/http'
import type { SyncResponse } from '@/types'

export const syncService = {
  uploadReportFile: async (formData: FormData): Promise<SyncResponse> => {
    return http.post<SyncResponse>('/api/sincronizar/cargar', formData)
  }
}
