import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchFechas } from '../services/api'

export const useAppStore = defineStore('app', () => {
  const defaultApiBase = import.meta.env.VITE_API_BASE ?? ''
  const savedApiBase = localStorage.getItem('bimej12_custom_api_url')
  const apiBase = ref(savedApiBase !== null ? savedApiBase : defaultApiBase)

  const setCustomApiBase = (url: string) => {
    const cleanUrl = url.trim().replace(/\/$/, '')
    apiBase.value = cleanUrl
    localStorage.setItem('bimej12_custom_api_url', cleanUrl)
  }
  
  const selectedDate = ref('2026-07-05') // Keep for fallback/reference
  const selectedMonth = ref('JULIO')
  const availableDates = ref<string[]>([])

  
  // Dashboard month/day filters
  const selectedDashboardMonth = ref('JULIO')
  const selectedDashboardDay = ref('05')
  
  const months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

  const MONTH_NAME_TO_NUMBER: Record<string, string> = {
    'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
    'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
    'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
  }

  // Lista de todos los meses con su estado de disponibilidad en la base de datos
  const monthsWithAvailability = computed(() => {
    const loadedMonthNumbers = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3) loadedMonthNumbers.add(parts[1])
    })

    return months.map(m => {
      const num = MONTH_NAME_TO_NUMBER[m]
      const isAvailable = loadedMonthNumbers.has(num)
      return {
        name: m,
        num,
        isAvailable,
        label: isAvailable ? m : `${m} - (SIN REGISTRO)`
      }
    })
  })

  // Obtener los 31 días de un mes con su disponibilidad exacta (o todos si no hay mes)
  const getFormattedDaysForMonth = (monthName?: string) => {
    if (!monthName) {
      const availableDays = new Set(
        availableDates.value.map(d => d.split('-')[2]).filter(Boolean)
      )
      return Array.from({ length: 31 }, (_, i) => {
        const d = String(i + 1).padStart(2, '0')
        const isAvailable = availableDays.has(d)
        return {
          val: d,
          isAvailable,
          label: isAvailable ? d : `${d} - (SIN REGISTRO)`
        }
      })
    }

    const mNum = MONTH_NAME_TO_NUMBER[monthName.toUpperCase()]
    if (!mNum) {
      return Array.from({ length: 31 }, (_, i) => {
        const d = String(i + 1).padStart(2, '0')
        return { val: d, isAvailable: false, label: `${d} - (SIN REGISTRO)` }
      })
    }

    const availableDaysInMonth = new Set(
      availableDates.value
        .filter(d => {
          const parts = d.split('-')
          return parts.length === 3 && parts[1] === mNum
        })
        .map(d => d.split('-')[2])
    )

    return Array.from({ length: 31 }, (_, i) => {
      const d = String(i + 1).padStart(2, '0')
      const isAvailable = availableDaysInMonth.has(d)
      return {
        val: d,
        isAvailable,
        label: isAvailable ? d : `${d} - (SIN REGISTRO)`
      }
    })
  }

  // Días del mes del Dashboard calculados reactivamente
  const dashboardDaysFormatted = computed(() => {
    return getFormattedDaysForMonth(selectedDashboardMonth.value)
  })

  // Filter months to only those that actually exist in availableDates
  const availableMonths = computed<string[]>(() => {
    if (!availableDates.value || availableDates.value.length === 0) {
      return months
    }
    const monthSet = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3) monthSet.add(parts[1])
    })

    const result = months.filter(m => {
      const num = MONTH_NAME_TO_NUMBER[m]
      return monthSet.has(num)
    })
    return result.length > 0 ? result : months
  })

  // Get days that actually have records for a given month
  const getAvailableDaysForMonth = (monthName: string): string[] => {
    if (!monthName) {
      const daySet = new Set<string>()
      availableDates.value.forEach(d => {
        const parts = d.split('-')
        if (parts.length === 3) daySet.add(parts[2])
      })
      return Array.from(daySet).sort()
    }

    const mNum = MONTH_NAME_TO_NUMBER[monthName.toUpperCase()]
    if (!mNum) return []

    const daySet = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3 && parts[1] === mNum) {
        daySet.add(parts[2])
      }
    })

    return Array.from(daySet).sort()
  }

  
  const isSyncingDrive = ref(false)
  const syncSecondsElapsed = ref(0)
  const syncTimer = ref<any>(null)
  const syncAbortController = ref<AbortController | null>(null)
  const syncStatus = ref<'idle' | 'running' | 'success' | 'error'>('idle')
  const syncMessage = ref('')
  const syncErrors = ref<any[]>([])
  const syncLogs = ref<any[]>([])

  const cancelDriveSync = () => {
    if (syncAbortController.value) {
      syncAbortController.value.abort()
      syncAbortController.value = null
    }
    isSyncingDrive.value = false
    if (syncTimer.value) {
      clearInterval(syncTimer.value)
      syncTimer.value = null
    }
    syncStatus.value = 'error'
    syncMessage.value = 'Sincronización cancelada por el usuario.'
    autoDismissSyncStatus(4000)
  }

  const MONTH_MAP_REVERSE: Record<number, string> = {
    1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
    5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
    9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
  }

  const fetchAvailableDates = async () => {
    try {
      const data = await fetchFechas()
      availableDates.value = data
      if (data && data.length > 0) {
        const sorted = [...data].sort()
        const latestDate = sorted[sorted.length - 1]
        selectedDate.value = latestDate
        
        const parts = latestDate.split('-')
        if (parts.length === 3) {
          const mNum = parseInt(parts[1], 10)
          const mName = MONTH_MAP_REVERSE[mNum]
          const dayStr = parts[2]
          
          if (mName) {
            selectedMonth.value = mName
            selectedDashboardMonth.value = mName
            selectedDashboardDay.value = dayStr
          }
        }
      }
    } catch (error) {
      console.error('Error fetching available dates:', error)
    }
  }


  let dismissTimeout: any = null

  const clearSyncStatus = () => {
    if (dismissTimeout) {
      clearTimeout(dismissTimeout)
      dismissTimeout = null
    }
    syncStatus.value = 'idle'
  }

  const DEFAULT_AUTO_DISMISS_MS = 20000 // 20 segundos para revisar los logs

  const autoDismissSyncStatus = (delayMs = DEFAULT_AUTO_DISMISS_MS) => {
    if (dismissTimeout) clearTimeout(dismissTimeout)
    dismissTimeout = setTimeout(() => {
      syncStatus.value = 'idle'
    }, delayMs)
  }

  const startDriveSync = async (params: { tipo: string; fecha?: string | null; fechas?: string[] | null; mes?: string | null; overwrite: boolean }) => {
    if (isSyncingDrive.value) return

    if (dismissTimeout) {
      clearTimeout(dismissTimeout)
      dismissTimeout = null
    }

    isSyncingDrive.value = true
    syncSecondsElapsed.value = 0
    syncStatus.value = 'running'
    syncMessage.value = 'Sincronizando con Google Drive...'
    syncErrors.value = []
    syncLogs.value = []
    syncAbortController.value = new AbortController()

    // Iniciar temporizador de segundos transcurridos
    syncTimer.value = setInterval(() => {
      syncSecondsElapsed.value++
    }, 1000)

    try {
      const token = localStorage.getItem('bimej12_auth_token')
      const res = await fetch(`${apiBase.value}/api/sincronizar/drive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          tipo: params.tipo,
          fecha: params.fecha || null,
          fechas: params.fechas || null,
          mes: params.mes || null,
          overwrite: params.overwrite
        }),
        signal: syncAbortController.value.signal
      })


      if (res.status === 401) {
        localStorage.removeItem('bimej12_auth_token')
        window.location.hash = '/login'
        syncStatus.value = 'error'
        syncMessage.value = 'Sesión expirada. Redirigiendo...'
        autoDismissSyncStatus(DEFAULT_AUTO_DISMISS_MS)
        return
      }

      const contentType = res.headers.get('content-type') || ''
      if (!contentType.includes('application/json')) {
        const textErr = await res.text()
        console.error('Non-JSON response from server:', textErr)
        throw new Error(`El servidor en la nube está iniciando (${res.status}). Por favor reintenta en un momento.`)
      }

      const data = await res.json()

      const dismissMs = data.auto_dismiss_seconds ? (data.auto_dismiss_seconds * 1000) : DEFAULT_AUTO_DISMISS_MS

      if (res.ok && data.status === 'success') {
        syncStatus.value = 'success'
        syncErrors.value = data.errors || []
        syncLogs.value = data.logs || []
        if (syncErrors.value.length > 0) {
          syncMessage.value = `Sincronizado. ${syncErrors.value.length} archivos omitidos por errores de formato/lectura.`
        } else {
          syncMessage.value = data.message || 'Sincronización completada con éxito.'
        }
        await fetchAvailableDates()
        autoDismissSyncStatus(dismissMs)
      } else {
        syncStatus.value = 'error'
        syncMessage.value = data.detail || 'Ocurrió un error al sincronizar con Google Drive.'
        autoDismissSyncStatus(dismissMs)
      }
    } catch (error) {
      console.error('Error in background drive sync:', error)
      syncStatus.value = 'error'
      syncMessage.value = 'Error de conexión con el servidor.'
      autoDismissSyncStatus(DEFAULT_AUTO_DISMISS_MS)
    } finally {
      isSyncingDrive.value = false
      if (syncTimer.value) {
        clearInterval(syncTimer.value)
        syncTimer.value = null
      }
    }
  }


  return {
    apiBase,
    setCustomApiBase,
    selectedDate,
    selectedMonth,
    selectedDashboardMonth,
    selectedDashboardDay,
    availableDates,
    months,
    monthsWithAvailability,
    availableMonths,
    getAvailableDaysForMonth,
    getFormattedDaysForMonth,
    dashboardDaysFormatted,
    isSyncingDrive,

    syncSecondsElapsed,
    syncStatus,
    syncMessage,
    syncErrors,
    syncLogs,
    fetchAvailableDates,
    startDriveSync,
    cancelDriveSync,
    clearSyncStatus
  }


})
