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

  const fetchAvailableDates = async () => {
    try {
      const data = await fetchFechas()
      availableDates.value = data
    } catch (error) {
      console.error('Error fetching available dates:', error)
    }
  }

  const startDriveSync = async () => {
    if (isSyncingDrive.value) return

    isSyncingDrive.value = true
    syncSecondsElapsed.value = 0
    syncStatus.value = 'running'
    syncMessage.value = 'Sincronizando con Google Drive...'

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
        }
      })

      const data = await res.json()

      if (res.ok && data.status === 'success') {
        syncStatus.value = 'success'
        syncMessage.value = data.message || 'Sincronización completada con éxito.'
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

      // Limpiar notificación automáticamente después de 5 segundos
      setTimeout(() => {
        if (!isSyncingDrive.value) {
          syncStatus.value = 'idle'
          syncMessage.value = ''
        }
      }, 5000)
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
    fetchAvailableDates,
    startDriveSync
  }
})
