import { ref } from 'vue'
import { useAppStore } from '../stores/appStore'
import { fetchKPIs, fetchCambios } from '../services/api'
import type { KPIData, CambiosResponse } from '../types'

export function useDashboardData() {
  const appStore = useAppStore()
  const loading = ref(true)
  const hasError = ref(false)
  const kpis = ref<KPIData | null>(null)
  const cambios = ref<CambiosResponse | null>(null)

  const loadDashboardData = async () => {
    loading.value = true
    hasError.value = false
    try {
      const mes = appStore.selectedDashboardMonth
      const dia = appStore.selectedDashboardDay

      // Cargar KPIs y Cambios en paralelo
      const [kpisData, cambiosData] = await Promise.all([
        fetchKPIs(mes, dia),
        fetchCambios(mes, dia)
      ])

      kpis.value = kpisData
      cambios.value = cambiosData
      loading.value = false
    } catch (error) {
      console.error('Error cargando datos del dashboard:', error)
      loading.value = false
      hasError.value = true
    }
  }

  return {
    loading,
    hasError,
    kpis,
    cambios,
    loadDashboardData
  }
}
