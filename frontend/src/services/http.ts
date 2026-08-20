import { useAppStore } from '@stores/appStore'

export const getApiBase = (): string => {
  try {
    const store = useAppStore()
    return store.apiBase || ''
  } catch {
    return ''
  }
}

export const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const token = localStorage.getItem('bimej12_auth_token')
  const headers = {
    ...(options.headers || {}),
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  }
  const fullUrl = url.startsWith('http') ? url : `${getApiBase()}${url.startsWith('/') ? url : `/${url}`}`
  const res = await fetch(fullUrl, { ...options, headers })
  
  if (res.status === 401) {
    localStorage.removeItem('bimej12_auth_token')
    window.location.hash = '/login'
  }
  return res
}

export const http = {
  get: async <T>(url: string, options: RequestInit = {}): Promise<T> => {
    const res = await fetchWithAuth(url, { ...options, method: 'GET' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Error HTTP ${res.status}`)
    }
    return res.json()
  },
  
  post: async <T>(url: string, body?: any, options: RequestInit = {}): Promise<T> => {
    const isFormData = body instanceof FormData
    const headers = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options.headers || {})
    }
    const res = await fetchWithAuth(url, {
      ...options,
      method: 'POST',
      headers,
      body: isFormData ? body : (body ? JSON.stringify(body) : undefined)
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Error HTTP ${res.status}`)
    }
    return res.json()
  }
}
