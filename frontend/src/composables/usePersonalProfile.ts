import { ref, computed } from 'vue'
import { fetchPersonalDetalle, fetchPersonalHistorial } from '../services/api'
import type { PersonalDetalle, HistorialRegistro } from '../types'
import { MONTHS_LIST } from '../utils/date'

export function usePersonalProfile() {
  const loading = ref(true)
  const profile = ref<PersonalDetalle | null>(null)
  const historial = ref<HistorialRegistro[]>([])

  const loadProfile = async (cedula: number) => {
    loading.value = true
    try {
      const [pData, hData] = await Promise.all([
        fetchPersonalDetalle(cedula),
        fetchPersonalHistorial(cedula)
      ])
      profile.value = pData
      historial.value = hData
      loading.value = false
    } catch (error) {
      console.error('Error al cargar perfil de personal:', error)
      loading.value = false
    }
  }

  const activeMonths = computed<string[]>(() => {
    if (!profile.value || !profile.value.fecha_retiro) {
      return [...MONTHS_LIST]
    }
    try {
      const parts = profile.value.fecha_retiro.split('-')
      const retirementMonthNum = parseInt(parts[1], 10)
      return MONTHS_LIST.slice(0, retirementMonthNum)
    } catch (e) {
      console.error('Error calculando meses activos:', e)
      return [...MONTHS_LIST]
    }
  })

  const currentYear = computed(() => {
    if (profile.value && profile.value.primer_registro_fecha) {
      return profile.value.primer_registro_fecha.split('-')[0]
    }
    return String(new Date().getFullYear())
  })

  return {
    loading,
    profile,
    historial,
    activeMonths,
    currentYear,
    loadProfile
  }
}
