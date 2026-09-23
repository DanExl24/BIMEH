import { http, fetchWithAuth, getApiBase } from '@services/http'
import type { 
  NovedadCatalogoItem, 
  NovedadesConsultaFiltros, 
  NovedadesConsultaResponse 
} from '../types/novedades.types'

export const novedadesService = {
  getCatalogo: async (): Promise<NovedadCatalogoItem[]> => {
    return http.get<NovedadCatalogoItem[]>('/api/novedades/catalogo')
  },

  consultar: async (filtros: NovedadesConsultaFiltros): Promise<NovedadesConsultaResponse> => {
    const params = new URLSearchParams()
    if (filtros.id_sub_novedad) params.append('id_sub_novedad', filtros.id_sub_novedad.toString())
    if (filtros.mes && filtros.mes !== 'TODOS') params.append('mes', filtros.mes)
    if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio)
    if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin)
    if (filtros.q && filtros.q.trim()) params.append('q', filtros.q.trim())
    if (filtros.estado && filtros.estado !== 'TODOS') params.append('estado', filtros.estado)
    if (filtros.page) params.append('page', filtros.page.toString())
    if (filtros.limit) params.append('limit', filtros.limit.toString())

    const query = params.toString()
    return http.get<NovedadesConsultaResponse>(`/api/novedades/consulta${query ? `?${query}` : ''}`)
  },

  descargarReporte: async (formato: 'excel' | 'pdf', filtros: NovedadesConsultaFiltros): Promise<void> => {
    const params = new URLSearchParams()
    if (filtros.id_sub_novedad) params.append('id_sub_novedad', filtros.id_sub_novedad.toString())
    if (filtros.mes && filtros.mes !== 'TODOS') params.append('mes', filtros.mes)
    if (filtros.fecha_inicio) params.append('fecha_inicio', filtros.fecha_inicio)
    if (filtros.fecha_fin) params.append('fecha_fin', filtros.fecha_fin)
    if (filtros.q && filtros.q.trim()) params.append('q', filtros.q.trim())
    if (filtros.estado && filtros.estado !== 'TODOS') params.append('estado', filtros.estado)

    const endpoint = `/api/novedades/exportar/${formato}`
    const fullUrl = `${getApiBase()}${endpoint}?${params.toString()}`

    const res = await fetchWithAuth(fullUrl)
    if (!res.ok) {
      throw new Error(`Error al generar el archivo ${formato.toUpperCase()}: ${res.statusText}`)
    }

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    // Obtener nombre de archivo de la cabecera si existe
    const disposition = res.headers.get('Content-Disposition')
    let filename = `Reporte_Novedades_${Date.now()}.${formato === 'excel' ? 'xlsx' : 'pdf'}`
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename=(?:["']?)(.*?)(?:["']?)(?:;|$)/)
      if (match && match[1]) filename = match[1]
    }
    
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  },

  obtenerPreviewBuilder: async (config: import('../types/novedades.types').ReportBuilderConfig): Promise<import('../types/novedades.types').ReportBuilderPreviewResponse> => {
    const params = new URLSearchParams()
    params.append('modo', config.modo)
    if (config.id_sub_novedad) params.append('id_sub_novedad', config.id_sub_novedad.toString())
    if (config.mes && config.mes !== 'TODOS') params.append('mes', config.mes)
    if (config.fecha_inicio) params.append('fecha_inicio', config.fecha_inicio)
    if (config.fecha_fin) params.append('fecha_fin', config.fecha_fin)
    if (config.q && config.q.trim()) params.append('q', config.q.trim())
    if (config.estado && config.estado !== 'TODOS') params.append('estado', config.estado)
    if (config.min_dias && config.min_dias > 0) params.append('min_dias', config.min_dias.toString())
    if (config.columnas && config.columnas.length > 0) params.append('columnas', config.columnas.join(','))
    if (config.orden) params.append('orden', config.orden)

    return http.get<import('../types/novedades.types').ReportBuilderPreviewResponse>(`/api/novedades/builder/preview?${params.toString()}`)
  },

  descargarReporteBuilder: async (formato: 'excel' | 'pdf', config: import('../types/novedades.types').ReportBuilderConfig): Promise<void> => {
    const params = new URLSearchParams()
    params.append('modo', config.modo)
    if (config.id_sub_novedad) params.append('id_sub_novedad', config.id_sub_novedad.toString())
    if (config.mes && config.mes !== 'TODOS') params.append('mes', config.mes)
    if (config.fecha_inicio) params.append('fecha_inicio', config.fecha_inicio)
    if (config.fecha_fin) params.append('fecha_fin', config.fecha_fin)
    if (config.q && config.q.trim()) params.append('q', config.q.trim())
    if (config.estado && config.estado !== 'TODOS') params.append('estado', config.estado)
    if (config.min_dias && config.min_dias > 0) params.append('min_dias', config.min_dias.toString())
    if (config.columnas && config.columnas.length > 0) params.append('columnas', config.columnas.join(','))
    if (config.orden) params.append('orden', config.orden)

    const endpoint = `/api/novedades/exportar/${formato}`
    const fullUrl = `${getApiBase()}${endpoint}?${params.toString()}`

    const res = await fetchWithAuth(fullUrl)
    if (!res.ok) {
      throw new Error(`Error al generar el archivo ${formato.toUpperCase()}: ${res.statusText}`)
    }

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url

    const disposition = res.headers.get('Content-Disposition')
    let filename = `Reporte_${config.modo === 'agil' ? 'Agil' : 'Detallado'}_${Date.now()}.${formato === 'excel' ? 'xlsx' : 'pdf'}`
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename=(?:["']?)(.*?)(?:["']?)(?:;|$)/)
      if (match && match[1]) filename = match[1]
    }

    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }
}
