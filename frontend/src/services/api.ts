import { useAppStore } from '../stores/appStore'
import * as Types from '../types'

const getApiBase = () => {
  const store = useAppStore()
  return store.apiBase
}

export const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const token = localStorage.getItem('bimej12_auth_token')
  const headers = {
    ...(options.headers || {}),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  }
  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('bimej12_auth_token')
    window.location.hash = '/login'
  }
  return res
}


export async function fetchFechas(): Promise<string[]> {
  const res = await fetchWithAuth(`${getApiBase()}/api/fechas`)
  if (!res.ok) throw new Error('Error al obtener fechas')
  return res.json()
}

export async function fetchKPIs(mes?: string, dia?: string, fecha?: string): Promise<Types.KPIData> {
  let url = `${getApiBase()}/api/dashboard/kpis?`
  if (fecha) {
    url += `fecha=${fecha}`
  } else {
    const params: string[] = []
    if (typeof mes === 'string') params.push(`mes=${mes}`)
    if (typeof dia === 'string') params.push(`dia=${dia}`)
    url += params.join('&')
  }
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Error al obtener KPIs')
  return res.json()
}

export async function fetchCambios(mes?: string, dia?: string, fecha?: string): Promise<Types.CambiosResponse> {
  let url = `${getApiBase()}/api/dashboard/cambios?`
  if (fecha) {
    url += `fecha=${fecha}`
  } else {
    const params: string[] = []
    if (typeof mes === 'string') params.push(`mes=${mes}`)
    if (typeof dia === 'string') params.push(`dia=${dia}`)
    url += params.join('&')
  }
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Error al obtener cambios de estado')
  return res.json()
}

export async function fetchEvolucion(mes?: string, dia?: string): Promise<Types.EvolucionItem[]> {
  const params: string[] = []
  if (typeof mes === 'string') params.push(`mes=${mes}`)
  if (typeof dia === 'string') params.push(`dia=${dia}`)
  const url = `${getApiBase()}/api/dashboard/evolucion?${params.join('&')}`
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Error al obtener evolución')
  return res.json()
}

export async function fetchNovedadesFrecuentes(mes?: string, dia?: string, fecha?: string): Promise<Types.NovedadFrecuente[]> {
  let url = `${getApiBase()}/api/dashboard/novedades-frecuentes?`
  if (fecha) {
    url += `fecha=${fecha}`
  } else {
    const params: string[] = []
    if (typeof mes === 'string') params.push(`mes=${mes}`)
    if (typeof dia === 'string') params.push(`dia=${dia}`)
    url += params.join('&')
  }
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Error al obtener novedades frecuentes')
  return res.json()
}

export async function fetchDistribucion(mes?: string, dia?: string, fecha?: string): Promise<Types.DistribucionItem[]> {
  let url = `${getApiBase()}/api/dashboard/distribucion?`
  if (fecha) {
    url += `fecha=${fecha}`
  } else {
    const params: string[] = []
    if (typeof mes === 'string') params.push(`mes=${mes}`)
    if (typeof dia === 'string') params.push(`dia=${dia}`)
    url += params.join('&')
  }
  const res = await fetchWithAuth(url)
  if (!res.ok) throw new Error('Error al obtener distribución')
  return res.json()
}

export async function buscarPersonal(q: string): Promise<Types.PersonalSearchResult[]> {
  const res = await fetchWithAuth(`${getApiBase()}/api/personal/buscar?q=${q}`)
  if (!res.ok) throw new Error('Error al buscar personal')
  return res.json()
}

export async function fetchPersonalDetalle(cedula: number): Promise<Types.PersonalDetalle> {
  const res = await fetchWithAuth(`${getApiBase()}/api/personal/${cedula}`)
  if (!res.ok) throw new Error('Error al obtener detalle del personal')
  return res.json()
}

export async function fetchPersonalHistorial(cedula: number): Promise<Types.HistorialRegistro[]> {
  const res = await fetchWithAuth(`${getApiBase()}/api/personal/${cedula}/historial`)
  if (!res.ok) throw new Error('Error al obtener historial del personal')
  return res.json()
}

export async function fetchPersonalAcumulado(cedula: number): Promise<Types.AcumuladoNovedad[]> {
  const res = await fetchWithAuth(`${getApiBase()}/api/personal/${cedula}/acumulado`)
  if (!res.ok) throw new Error('Error al obtener acumulado del personal')
  return res.json()
}

export async function fetchCalendario(mes: string): Promise<Types.CalendarioItem[]> {
  const res = await fetchWithAuth(`${getApiBase()}/api/reportes/calendario?mes=${mes}`)
  if (!res.ok) throw new Error('Error al obtener calendario')
  return res.json()
}

export async function fetchReporteDia(fecha: string): Promise<Types.PersonalDia[]> {
  const res = await fetchWithAuth(`${getApiBase()}/api/reportes/dia?fecha=${fecha}`)
  if (!res.ok) throw new Error('Error al obtener reporte del día')
  return res.json()
}

export async function fetchStatsRanking(): Promise<Types.RankingsData> {
  const res = await fetchWithAuth(`${getApiBase()}/api/stats/ranking`)
  if (!res.ok) throw new Error('Error al obtener rankings de estadísticas')
  return res.json()
}

export async function fetchStatsHeatmap(mes: string): Promise<Types.HeatmapResponse> {
  const res = await fetchWithAuth(`${getApiBase()}/api/stats/heatmap?mes=${mes}`)
  if (!res.ok) throw new Error('Error al obtener heatmap')
  return res.json()
}

export async function fetchDriveStatus(): Promise<Types.DriveStatusResponse> {
  const res = await fetchWithAuth(`${getApiBase()}/api/auth/drive-status`)
  if (!res.ok) throw new Error('Error al verificar estado de Google Drive')
  return res.json()
}

export async function fetchOAuthUrl(redirectUri: string): Promise<Types.OAuthUrlResponse> {
  const res = await fetch(`${getApiBase()}/api/sincronizar/oauth/url?redirect_uri=${encodeURIComponent(redirectUri)}`)
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}))
    throw new Error(errData.detail || `Error en el servidor (${res.status})`)
  }
  return res.json()
}

export async function uploadReportFile(formData: FormData): Promise<Types.SyncResponse> {
  const res = await fetchWithAuth(`${getApiBase()}/api/sincronizar/cargar`, {
    method: 'POST',
    body: formData
  })
  return res.json()
}
