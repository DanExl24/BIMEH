import { ref, computed, type Ref } from 'vue'
import type { HistorialRegistro } from '../types'
import { MONTH_SPANISH_NAMES, getMonthDaysArray } from '../utils/date'

export function usePersonalTimelineFilters(historial: Ref<HistorialRegistro[]>) {
  const filtroMes = ref('')
  const filtroDia = ref('')
  const filtroSubnovedad = ref('')

  const diasDelMes = computed(() => getMonthDaysArray(filtroMes.value))

  const subnovedadesList = computed(() => {
    const set = new Set<string>()
    historial.value.forEach(h => {
      if (h.subnovedad) {
        set.add(h.subnovedad)
      }
    })
    return Array.from(set).sort()
  })

  const filteredHistorial = computed(() => {
    return historial.value.filter(h => {
      const parts = h.fecha.split('-')
      const month = parts[1]
      const day = parts[2]

      const matchMonth = !filtroMes.value || month === filtroMes.value
      const matchDay = !filtroDia.value || day === filtroDia.value
      const matchSubnovedad = !filtroSubnovedad.value || h.subnovedad === filtroSubnovedad.value

      return matchMonth && matchDay && matchSubnovedad
    })
  })

  const filterSubtitle = computed(() => {
    const parts: string[] = []
    if (filtroMes.value && MONTH_SPANISH_NAMES[filtroMes.value]) {
      parts.push(MONTH_SPANISH_NAMES[filtroMes.value])
    }
    if (filtroDia.value) {
      parts.push(`Día ${filtroDia.value}`)
    }
    if (filtroSubnovedad.value) {
      parts.push(filtroSubnovedad.value)
    }
    return parts.length > 0 ? `(${parts.join(' - ')})` : '(Anual Completo)'
  })

  return {
    filtroMes,
    filtroDia,
    filtroSubnovedad,
    diasDelMes,
    subnovedadesList,
    filteredHistorial,
    filterSubtitle
  }
}
