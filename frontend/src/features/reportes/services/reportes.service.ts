import { getApiBase } from '@services/http'

export const reportesService = {
  getExportUrl: (tipo: string, format: 'excel' | 'pdf' | 'csv', params: Record<string, string>): string => {
    const base = getApiBase()
    const query = new URLSearchParams({ tipo, ...params }).toString()
    return `${base}/api/exportar/${format}?${query}`
  }
}
