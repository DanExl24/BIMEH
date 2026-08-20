import { ref } from 'vue'
import { buscarPersonal } from '../services/api'
import type { PersonalSearchResult } from '../types'

export function usePersonalAutocomplete() {
  const searchQuery = ref('')
  const loading = ref(false)
  const results = ref<PersonalSearchResult[]>([])
  let timeout: number | null = null

  const handleSearch = () => {
    if (timeout) clearTimeout(timeout)

    if (searchQuery.value.trim().length < 2) {
      results.value = []
      loading.value = false
      return
    }

    loading.value = true
    timeout = window.setTimeout(async () => {
      try {
        results.value = await buscarPersonal(searchQuery.value)
      } catch (e) {
        console.error('Error al buscar personal:', e)
        results.value = []
      } finally {
        loading.value = false
      }
    }, 350)
  }

  const selectSuggestion = (val: string) => {
    searchQuery.value = val
    handleSearch()
  }

  const clearSearch = () => {
    searchQuery.value = ''
    results.value = []
    loading.value = false
    if (timeout) clearTimeout(timeout)
  }

  return {
    searchQuery,
    loading,
    results,
    handleSearch,
    selectSuggestion,
    clearSearch
  }
}
