import { ref, computed } from 'vue'
import { personalService } from '../services/personal.service'
import type { PersonalDetalle, HistorialRegistro } from '@/types'
import { useDateStore } from '@stores/dateStore'

export function usePersonalProfile() {
  const loading = ref(true)
  const profile = ref<PersonalDetalle | null>(null)
  const historial = ref<HistorialRegistro[]>([])

  const loadProfile = async (cedula: number) => {
    loading.value = true
    try {
      const [pData, hData] = await Promise.all([
        personalService.getDetalle(cedula),
        personalService.getHistorial(cedula)
      ])
      profile.value = pData
      historial.value = hData
      loading.value = false
    } catch (error) {
      console.error('Error al cargar perfil de personal:', error)
      loading.value = false
    }
  }

  const dateStore = useDateStore()

  const activeMonths = computed<string[]>(() => {
    return dateStore.getPersonnelActiveMonths(historial.value)
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
