import { ref, computed, watch, onMounted } from 'vue'
import { useAppStore } from '@stores/appStore'
import { useDateStore } from '@stores/dateStore'
import { cronologiaService } from '../services/cronologia.service'
import type { CalendarioItem, PersonalDia, HeatmapResponse } from '@types'

export function useCronologiaData() {
  const appStore = useAppStore()
  const dateStore = useDateStore()

  // Control de sub-vistas y fechas
  const activeSubView = ref<'reporte' | 'heatmap'>('reporte')
  const activeDate = ref<string>(dateStore.latestDate || dateStore.selectedDate || '')

  // Filtros de búsqueda
  const dailySearch = ref('')
  const heatmapSearch = ref('')

  // Estados de carga
  const loadingCalendar = ref(true)
  const loadingDaily = ref(true)
  const loadingHeatmap = ref(true)

  // Datos
  const calendarData = ref<CalendarioItem[]>([])
  const dailyReport = ref<PersonalDia[]>([])
  const heatmapData = ref<HeatmapResponse>({ fechas: [], data: [] })

  // Paginación del heatmap
  const heatmapPage = ref(1)
  const heatmapLimit = 25

  // Carga de calendario
  const loadCalendar = async () => {
    loadingCalendar.value = true
    try {
      calendarData.value = await cronologiaService.getCalendario(appStore.selectedMonth)
      if (calendarData.value.length > 0) {
        const datesList = calendarData.value.map(c => c.fecha)
        if (!datesList.includes(activeDate.value)) {
          activeDate.value = datesList[0]
        }
      }
      loadingCalendar.value = false
    } catch (e) {
      console.error('Error fetching calendar:', e)
      loadingCalendar.value = false
    }
  }

  // Carga de reporte diario
  const loadDailyReport = async () => {
    loadingDaily.value = true
    try {
      dailyReport.value = await cronologiaService.getReporteDia(activeDate.value)
      loadingDaily.value = false
    } catch (e) {
      console.error('Error loading daily report:', e)
      loadingDaily.value = false
    }
  }

  // Carga de matriz heatmap
  const loadHeatmapData = async () => {
    loadingHeatmap.value = true
    try {
      heatmapData.value = await cronologiaService.getHeatmapMensual(appStore.selectedMonth)
      heatmapPage.value = 1
      loadingHeatmap.value = false
    } catch (e) {
      console.error('Error loading heatmap:', e)
      loadingHeatmap.value = false
    }
  }

  const selectDate = (date: string) => {
    activeDate.value = date
  }

  // Cálculos mensuales
  const avgMonthlyDispo = computed(() => {
    if (!calendarData.value.length) return 0
    const sum = calendarData.value.reduce((acc, c) => acc + c.disponibilidad, 0)
    return Math.round(sum / calendarData.value.length)
  })

  const maxDispoDay = computed(() => {
    if (!calendarData.value.length) return 'N/A'
    const sorted = [...calendarData.value].sort((a, b) => b.disponibilidad - a.disponibilidad)
    return `${sorted[0].fecha} (${Math.round(sorted[0].disponibilidad)}%)`
  })

  const minDispoDay = computed(() => {
    if (!calendarData.value.length) return 'N/A'
    const sorted = [...calendarData.value].sort((a, b) => a.disponibilidad - b.disponibilidad)
    return `${sorted[0].fecha} (${Math.round(sorted[0].disponibilidad)}%)`
  })

  // Filtrado de reportes diarios
  const filteredDailyReport = computed(() => {
    if (!dailySearch.value.trim()) return dailyReport.value
    const query = dailySearch.value.toLowerCase()
    return dailyReport.value.filter(r =>
      r.nombre.toLowerCase().includes(query) ||
      String(r.cedula).includes(query) ||
      r.subnovedad.toLowerCase().includes(query)
    )
  })

  // Filtrado del heatmap
  const filteredHeatmap = computed(() => {
    if (!heatmapSearch.value.trim()) return heatmapData.value.data
    const query = heatmapSearch.value.toLowerCase()
    return heatmapData.value.data.filter(row =>
      row.nombre.toLowerCase().includes(query) ||
      String(row.cedula).includes(query)
    )
  })

  // Paginación del heatmap
  const maxHeatmapPage = computed(() => {
    return Math.max(1, Math.ceil(filteredHeatmap.value.length / heatmapLimit))
  })

  const paginatedHeatmap = computed(() => {
    const start = (heatmapPage.value - 1) * heatmapLimit
    const end = start + heatmapLimit
    return filteredHeatmap.value.slice(start, end)
  })

  watch(() => appStore.selectedMonth, () => {
    loadCalendar()
    loadHeatmapData()
  })

  watch(activeDate, () => {
    loadDailyReport()
  })

  onMounted(() => {
    if (appStore.selectedDate) {
      activeDate.value = appStore.selectedDate
    }
    loadCalendar()
    loadDailyReport()
    loadHeatmapData()
  })

  return {
    activeSubView,
    activeDate,
    dailySearch,
    heatmapSearch,
    loadingCalendar,
    loadingDaily,
    loadingHeatmap,
    calendarData,
    dailyReport,
    heatmapData,
    heatmapPage,
    heatmapLimit,
    maxHeatmapPage,
    avgMonthlyDispo,
    maxDispoDay,
    minDispoDay,
    filteredDailyReport,
    filteredHeatmap,
    paginatedHeatmap,
    selectDate,
    loadCalendar,
    loadDailyReport,
    loadHeatmapData
  }
}
