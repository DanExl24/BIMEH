import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useDateStore } from './dateStore'
import { MONTHS_LIST } from '../utils/date'


export const useAppStore = defineStore('app', () => {
  const defaultApiBase = import.meta.env.VITE_API_BASE ?? ''
  const savedApiBase = localStorage.getItem('bimej12_custom_api_url')
  const apiBase = ref(savedApiBase !== null ? savedApiBase : defaultApiBase)

  const setCustomApiBase = (url: string) => {
    const cleanUrl = url.trim().replace(/\/$/, '')
    apiBase.value = cleanUrl
    localStorage.setItem('bimej12_custom_api_url', cleanUrl)
  }
  
  const dateStore = useDateStore()

  // Forwarded date state from unified dateStore
  const selectedDate = computed({
    get: () => dateStore.selectedDate,
    set: (val: string) => dateStore.setSelectedDate(val)
  })

  const selectedMonth = computed({
    get: () => dateStore.selectedMonth,
    set: (val: string) => dateStore.setSelectedMonth(val)
  })

  const selectedDashboardMonth = computed({
    get: () => dateStore.selectedMonth,
    set: (val: string) => dateStore.setSelectedMonth(val)
  })

  const selectedDashboardDay = computed({
    get: () => dateStore.selectedDay,
    set: (val: string) => dateStore.setSelectedDay(val)
  })

  const availableDates = computed(() => dateStore.availableDates)
  const availableMonths = computed(() => dateStore.availableMonths)
  const months = MONTHS_LIST
  const monthsWithAvailability = computed(() => dateStore.monthsWithAvailability)
  const dashboardDaysFormatted = computed(() => dateStore.selectedMonthDaysFormatted)

  const getFormattedDaysForMonth = (monthName?: string) => dateStore.getFormattedDaysForMonth(monthName)
  const getAvailableDaysForMonth = (monthName: string) => dateStore.getAvailableDaysForMonth(monthName)


  
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

  const fetchAvailableDates = async () => {
    await dateStore.fetchAvailableDates(true)
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
