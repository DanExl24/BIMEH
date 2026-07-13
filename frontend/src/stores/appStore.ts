import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchFechas } from '../services/api'

export const useAppStore = defineStore('app', () => {
  const apiBase = 'http://127.0.0.1:8000'
  
  const selectedDate = ref('2026-07-05') // Keep for fallback/reference
  const selectedMonth = ref('JULIO')
  const availableDates = ref<string[]>([])
  
  // Dashboard month/day filters
  const selectedDashboardMonth = ref('JULIO')
  const selectedDashboardDay = ref('05')
  
  const months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO']
  
  const isSyncingDrive = ref(false)
  const syncSecondsElapsed = ref(0)
  const syncTimer = ref<any>(null)
  const syncStatus = ref<'idle' | 'running' | 'success' | 'error'>('idle')
  const syncMessage = ref('')
  const syncErrors = ref<any[]>([])
  const syncLogs = ref<any[]>([])

  const fetchAvailableDates = async () => {
    try {
      const data = await fetchFechas()
      availableDates.value = data
    } catch (error) {
      console.error('Error fetching available dates:', error)
    }
  }

  const startDriveSync = async (params: { tipo: string; fecha?: string | null; mes?: string | null; overwrite: boolean }) => {
    if (isSyncingDrive.value) return

    isSyncingDrive.value = true
    syncSecondsElapsed.value = 0
    syncStatus.value = 'running'
    syncMessage.value = 'Sincronizando con Google Drive...'
    syncErrors.value = []
    syncLogs.value = []

    // Iniciar temporizador de segundos transcurridos
    syncTimer.value = setInterval(() => {
      syncSecondsElapsed.value++
    }, 1000)

    try {
      const token = localStorage.getItem('bimej12_auth_token')
      const res = await fetch(`${apiBase}/api/sincronizar/drive`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          tipo: params.tipo,
          fecha: params.fecha || null,
          mes: params.mes || null,
          overwrite: params.overwrite
        })
      })

      if (res.status === 401) {
        localStorage.removeItem('bimej12_auth_token')
        window.location.hash = '/login'
        syncStatus.value = 'error'
        syncMessage.value = 'Sesión expirada. Redirigiendo...'
        return
      }

      const data = await res.json()

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
      } else {
        syncStatus.value = 'error'
        syncMessage.value = data.detail || 'Ocurrió un error al sincronizar con Google Drive.'
      }
    } catch (error) {
      console.error('Error in background drive sync:', error)
      syncStatus.value = 'error'
      syncMessage.value = 'Error de conexión con el servidor.'
    } finally {
      isSyncingDrive.value = false
      if (syncTimer.value) {
        clearInterval(syncTimer.value)
        syncTimer.value = null
      }

      // Si no hubo errores, limpiar notificación después de 8 segundos.
      // Si hay errores, la dejamos para que el usuario pueda ver el log en la UI.
      setTimeout(() => {
        if (!isSyncingDrive.value && syncErrors.value.length === 0 && syncStatus.value !== 'error') {
          syncStatus.value = 'idle'
          syncMessage.value = ''
        }
      }, 8000)
    }
  }

  return {
    apiBase,
    selectedDate,
    selectedMonth,
    selectedDashboardMonth,
    selectedDashboardDay,
    availableDates,
    months,
    isSyncingDrive,
    syncSecondsElapsed,
    syncStatus,
    syncMessage,
    syncErrors,
    syncLogs,
    fetchAvailableDates,
    startDriveSync
  }
})
