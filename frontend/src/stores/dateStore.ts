import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { http } from '@services/http'
import { 
  MONTHS_LIST, 
  MONTH_TO_NUMBER, 
  NUMBER_TO_MONTH,
  getDaysInMonth 
} from '../utils/date'
import type { HistorialRegistro } from '@/types'

export interface MonthAvailabilityItem {
  name: string
  num: string
  isAvailable: boolean
  label: string
}

export interface DayAvailabilityItem {
  val: string
  isAvailable: boolean
  label: string
}

export const useDateStore = defineStore('date', () => {
  // Estado básico
  const availableDates = ref<string[]>([])
  const isLoadingDates = ref(false)
  const isInitialized = ref(false)

  // Selecciones globales unificadas
  const selectedMonth = ref<string>('')
  const selectedDay = ref<string>('')
  const selectedDate = ref<string>('')

  // 1. Fechas ordenadas cronológicamente y descendente
  const sortedDatesAsc = computed(() => {
    return [...availableDates.value].sort((a, b) => a.localeCompare(b))
  })

  const sortedDatesDesc = computed(() => {
    return [...availableDates.value].sort((a, b) => b.localeCompare(a))
  })

  // 2. Registro más reciente disponible en la Base de Datos
  const latestDate = computed<string | null>(() => {
    if (sortedDatesDesc.value.length === 0) return null
    return sortedDatesDesc.value[0]
  })

  const latestMonth = computed<string | null>(() => {
    if (!latestDate.value) return null
    const parts = latestDate.value.split('-')
    return NUMBER_TO_MONTH[parts[1]] || null
  })

  const latestDay = computed<string | null>(() => {
    if (!latestDate.value) return null
    const parts = latestDate.value.split('-')
    return parts[2] || null
  })

  // 3. Meses disponibles REALMENTE en la Base de Datos (Únicos y ordenados por calendario)
  const availableMonths = computed<string[]>(() => {
    if (availableDates.value.length === 0) return []
    const monthNumbersSet = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3) monthNumbersSet.add(parts[1])
    })

    return MONTHS_LIST.filter(m => {
      const num = MONTH_TO_NUMBER[m]
      return monthNumbersSet.has(num)
    })
  })

  // 4. Años disponibles
  const availableYears = computed<string[]>(() => {
    const yearSet = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3) yearSet.add(parts[0])
    })
    return Array.from(yearSet).sort()
  })

  // 5. Todos los 12 meses con indicador de disponibilidad (para selects que requieran mostrar sin registro)
  const monthsWithAvailability = computed<MonthAvailabilityItem[]>(() => {
    const loadedMonthNumbers = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3) loadedMonthNumbers.add(parts[1])
    })

    return MONTHS_LIST.map(m => {
      const num = MONTH_TO_NUMBER[m]
      const isAvailable = loadedMonthNumbers.has(num)
      return {
        name: m,
        num,
        isAvailable,
        label: isAvailable ? m : `${m} - (SIN REGISTRO)`
      }
    })
  })

  // 6. Días disponibles reales para un mes específico
  const getAvailableDaysForMonth = (monthName: string): string[] => {
    if (!monthName) return []
    const mNum = MONTH_TO_NUMBER[monthName.toUpperCase()]
    if (!mNum) return []

    const daySet = new Set<string>()
    availableDates.value.forEach(d => {
      const parts = d.split('-')
      if (parts.length === 3 && parts[1] === mNum) {
        daySet.add(parts[2])
      }
    })

    return Array.from(daySet).sort((a, b) => a.localeCompare(b))
  }

  // 7. Días formateados (1 al total de días del mes) con indicador de disponibilidad
  const getFormattedDaysForMonth = (monthName?: string): DayAvailabilityItem[] => {
    const targetMonth = monthName || selectedMonth.value
    if (!targetMonth) {
      return Array.from({ length: 31 }, (_, i) => {
        const d = String(i + 1).padStart(2, '0')
        return { val: d, isAvailable: false, label: `${d} - (SIN REGISTRO)` }
      })
    }

    const totalDays = getDaysInMonth(targetMonth)
    const availableDaysInMonth = new Set(getAvailableDaysForMonth(targetMonth))



    return Array.from({ length: totalDays }, (_, i) => {
      const d = String(i + 1).padStart(2, '0')
      const isAvailable = availableDaysInMonth.has(d)
      return {
        val: d,
        isAvailable,
        label: isAvailable ? d : `${d} - (SIN REGISTRO)`
      }
    })
  }

  // Días del mes seleccionado formateados reactivamente
  const selectedMonthDaysFormatted = computed(() => {
    return getFormattedDaysForMonth(selectedMonth.value)
  })

  // 8. Métodos de verificación rápida
  const isMonthAvailable = (monthName: string): boolean => {
    if (!monthName) return false
    return availableMonths.value.includes(monthName.toUpperCase())
  }

  const isDateAvailable = (dateStr: string): boolean => {
    if (!dateStr) return false
    return availableDates.value.includes(dateStr)
  }

  // 9. Filtrado de meses activos para el expediente de un integrante
  const getPersonnelActiveMonths = (historial: HistorialRegistro[]): string[] => {
    if (!historial || historial.length === 0) {
      return availableMonths.value
    }

    const monthsInHistorial = new Set<string>()
    historial.forEach(h => {
      if (h.fecha) {
        const parts = h.fecha.split('-')
        if (parts.length === 3) {
          const mName = NUMBER_TO_MONTH[parts[1]]
          if (mName) monthsInHistorial.add(mName)
        }
      }
    })

    // Retorna solo los meses de la BD en los que el integrante tiene registros
    const active = MONTHS_LIST.filter(m => monthsInHistorial.has(m) && isMonthAvailable(m))
    return active.length > 0 ? active : availableMonths.value
  }

  // ACCIONES
  const fetchAvailableDates = async (forceRefresh = false) => {
    if (isInitialized.value && !forceRefresh && availableDates.value.length > 0) {
      return
    }

    isLoadingDates.value = true
    try {
      const data = await http.get<string[]>('/api/fechas')
      availableDates.value = Array.isArray(data) ? data : []
      isInitialized.value = true

      // Validación y asignación inteligente de defaults si no están seteados o son inválidos
      if (latestDate.value) {
        if (!selectedDate.value || !isDateAvailable(selectedDate.value)) {
          selectedDate.value = latestDate.value
        }
      }

      if (latestMonth.value) {
        if (!selectedMonth.value || !isMonthAvailable(selectedMonth.value)) {
          selectedMonth.value = latestMonth.value
        }
      }

      if (selectedMonth.value) {
        const daysInMonth = getAvailableDaysForMonth(selectedMonth.value)
        if (daysInMonth.length > 0 && (!selectedDay.value || !daysInMonth.includes(selectedDay.value))) {
          selectedDay.value = daysInMonth[daysInMonth.length - 1]
        }
      }
    } catch (error) {
      console.error('Error al obtener fechas disponibles desde la base de datos:', error)
    } finally {
      isLoadingDates.value = false
    }
  }

  const setSelectedMonth = (month: string) => {
    selectedMonth.value = month
    // Si el día actual seleccionado no pertenece a este mes, ajustar al último día disponible
    if (month) {
      const days = getAvailableDaysForMonth(month)
      if (days.length > 0 && !days.includes(selectedDay.value)) {
        selectedDay.value = days[days.length - 1]
      }
    }
  }

  const setSelectedDay = (day: string) => {
    selectedDay.value = day
  }

  const setSelectedDate = (dateStr: string) => {
    selectedDate.value = dateStr
    if (dateStr && dateStr.includes('-')) {
      const parts = dateStr.split('-')
      if (parts.length === 3) {
        const mName = NUMBER_TO_MONTH[parts[1]]
        if (mName) selectedMonth.value = mName
        selectedDay.value = parts[2]
      }
    }
  }

  const resetToLatest = () => {
    if (latestDate.value) {
      setSelectedDate(latestDate.value)
    }
  }

  return {
    // Estado
    availableDates,
    isLoadingDates,
    isInitialized,
    selectedMonth,
    selectedDay,
    selectedDate,

    // Computeds & Getters
    sortedDatesAsc,
    sortedDatesDesc,
    latestDate,
    latestMonth,
    latestDay,
    availableMonths,
    availableYears,
    monthsWithAvailability,
    selectedMonthDaysFormatted,

    // Funciones de consulta
    getAvailableDaysForMonth,
    getFormattedDaysForMonth,
    isMonthAvailable,
    isDateAvailable,
    getPersonnelActiveMonths,

    // Acciones
    fetchAvailableDates,
    setSelectedMonth,
    setSelectedDay,
    setSelectedDate,
    resetToLatest
  }
})
