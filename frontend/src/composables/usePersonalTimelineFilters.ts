import { ref, computed, type Ref } from 'vue'
import type { HistorialRegistro } from '../types'
import { MONTH_SPANISH_NAMES } from '../utils/date'


export function usePersonalTimelineFilters(historial: Ref<HistorialRegistro[]>) {
  const filtroMes = ref('')
  const filtroDia = ref('')
  const filtroSubnovedad = ref('')

  // Meses únicos presentes en el historial del integrante
  const mesesDisponibles = computed(() => {
    const map = new Map<string, string>()
    historial.value.forEach(h => {
      if (h.fecha) {
        const parts = h.fecha.split('-')
        if (parts.length === 3) {
          const num = parts[1]
          const name = MONTH_SPANISH_NAMES[num] || `Mes ${num}`
          map.set(num, name)
        }
      }
    })
    return Array.from(map.entries())
      .map(([num, name]) => ({ num, name }))
      .sort((a, b) => a.num.localeCompare(b.num))
  })

  // Días únicos presentes en el historial para el mes seleccionado
  const diasDelMes = computed(() => {
    const daySet = new Set<string>()
    historial.value.forEach(h => {
      if (h.fecha) {
        const parts = h.fecha.split('-')
        if (parts.length === 3) {
          if (!filtroMes.value || parts[1] === filtroMes.value) {
            daySet.add(parts[2])
          }
        }
      }
    })
    return Array.from(daySet).sort((a, b) => a.localeCompare(b))
  })

  // Subnovedades presentes en el historial
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
    mesesDisponibles,
    diasDelMes,
    subnovedadesList,
    filteredHistorial,
    filterSubtitle
  }
}

