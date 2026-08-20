import { ref, computed } from 'vue'
import { MONTH_TO_NUMBER, getDaysInMonth } from '../utils/date'
import { useDateStore } from '../stores/dateStore'

export function useMultiDaySelection(defaultMonth?: string) {
  const dateStore = useDateStore()
  const initialMonth = defaultMonth || dateStore.selectedMonth || dateStore.latestMonth || 'MAYO'
  const multiDayMonth = ref(initialMonth)
  const selectedDates = ref<string[]>([])


  // Días del calendario para el mes seleccionado
  const calendarDays = computed(() => {
    const monthNumStr = MONTH_TO_NUMBER[multiDayMonth.value.toUpperCase()]
    if (!monthNumStr) return []
    const currentYear = new Date().getFullYear()
    const daysInMonth = getDaysInMonth(multiDayMonth.value, currentYear)
    const days: { num: number; date: string }[] = []
    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${currentYear}-${monthNumStr}-${String(d).padStart(2, '0')}`
      days.push({ num: d, date: dateStr })
    }
    return days
  })

  // Espacios vacíos al inicio del calendario para alinear con el día de la semana (Lunes = 0)
  const calendarPadding = computed(() => {
    const monthNumStr = MONTH_TO_NUMBER[multiDayMonth.value.toUpperCase()]
    if (!monthNumStr) return 0
    const monthNum = parseInt(monthNumStr, 10)
    const currentYear = new Date().getFullYear()
    const firstDay = new Date(currentYear, monthNum - 1, 1).getDay()
    // getDay: 0=Dom, 1=Lun... necesitamos que Lun=0
    return firstDay === 0 ? 6 : firstDay - 1
  })

  const toggleDay = (dateStr: string) => {
    const idx = selectedDates.value.indexOf(dateStr)
    if (idx >= 0) {
      selectedDates.value.splice(idx, 1)
    } else {
      selectedDates.value.push(dateStr)
    }
  }

  const selectAllDays = () => {
    selectedDates.value = calendarDays.value.map(d => d.date)
  }

  const clearAllDays = () => {
    selectedDates.value = []
  }

  return {
    multiDayMonth,
    selectedDates,
    calendarDays,
    calendarPadding,
    toggleDay,
    selectAllDays,
    clearAllDays
  }
}
