import { ref } from 'vue'
import { useAppStore } from '@stores/appStore'
import { dashboardService } from '../services/dashboard.service'
import type { KPIData, CambiosResponse } from '@/types'

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
      const [kpiData, cambiosData] = await Promise.all([
        dashboardService.getKPIs(appStore.selectedDashboardMonth, appStore.selectedDashboardDay),
        dashboardService.getCambios(appStore.selectedDashboardMonth, appStore.selectedDashboardDay)
      ])
      kpis.value = kpiData
      cambios.value = cambiosData
      loading.value = false
    } catch (error) {
      console.error('Error cargando datos del dashboard:', error)
      hasError.value = true
      loading.value = false
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
