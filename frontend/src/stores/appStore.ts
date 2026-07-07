import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchFechas } from '../services/api'

export const useAppStore = defineStore('app', () => {
  const apiBase = 'http://127.0.0.1:8000'
  
  const selectedDate = ref('2026-07-05') // Keep for fallback/reference
  const selectedMonth = ref('JULIO')
  const availableDates = ref<string[]>([])
  
  // Dashboard month/day filters
  const selectedDashboardMonth = ref('JULIO')
  const selectedDashboardDay = ref('05')
  
  const months = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO']
  
  const fetchAvailableDates = async () => {
    try {
      const data = await fetchFechas()
      availableDates.value = data
    } catch (error) {
      console.error('Error fetching available dates:', error)
    }
  }
  
  return {
    apiBase,
    selectedDate,
    selectedMonth,
    selectedDashboardMonth,
    selectedDashboardDay,
    availableDates,
    months,
    fetchAvailableDates
  }
})
