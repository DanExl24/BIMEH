import { ref } from 'vue'
import { personalService } from '../services/personal.service'
import type { PersonalSearchResult } from '@types'

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
        results.value = await personalService.buscar(searchQuery.value)
        loading.value = false
      } catch (e) {
        console.error('Error fetching personnel:', e)
        loading.value = false
      }
    }, 350)
  }

  const selectSuggestion = (sug: string) => {
    searchQuery.value = sug
    handleSearch()
  }

  const clearSearch = () => {
    searchQuery.value = ''
    results.value = []
    loading.value = false
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
