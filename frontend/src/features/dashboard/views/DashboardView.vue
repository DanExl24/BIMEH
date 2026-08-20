<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-3">
      <Loader2 class="w-10 h-10 text-cyan-400 animate-spin" />
      <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Cargando datos operacionales...</p>
    </div>

    <!-- Error / Día sin registros -->
    <div v-else-if="hasError" class="glass-panel p-8 sm:p-12 rounded-3xl text-center space-y-4 border-amber-500/40">
      <div class="w-14 h-14 rounded-2xl bg-amber-500/15 border border-amber-500/30 text-amber-400 flex items-center justify-center mx-auto shadow-lg shadow-amber-500/10">
        <CalendarOff class="w-7 h-7 stroke-[2]" />
      </div>
      <div>
        <h3 class="text-base font-bold text-slate-100 uppercase tracking-wide">Día Sin Registro de Datos</h3>
        <p class="text-xs text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
          El día seleccionado ({{ appStore.selectedDashboardDay }} de {{ appStore.selectedDashboardMonth || 'Todos los meses' }}) aún no ha sido cargado o sincronizado en la base de datos.
        </p>
      </div>
      <div class="pt-2 flex justify-center gap-3">
        <button 
          @click="appStore.selectedDashboardDay = ''"
          class="px-5 py-2.5 bg-darkBg border border-slate-700 hover:border-slate-500 rounded-xl text-xs font-bold text-slate-200 transition-all cursor-pointer shadow-sm flex items-center gap-2"
        >
          <RefreshCw class="w-3.5 h-3.5 text-cyan-400" />
          <span>Ver Todo el Mes ({{ appStore.selectedDashboardMonth || 'Consolidado' }})</span>
        </button>
      </div>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="space-y-6">
      <!-- 1. KPIs Section -->
      <DashboardKpis :kpis="kpis" />

      <!-- 2. Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <DashboardEvolutionChart 
          class="lg:col-span-2"
          :month="appStore.selectedDashboardMonth" 
          :day="appStore.selectedDashboardDay" 
        />
        <DashboardNovedadesChart 
          :month="appStore.selectedDashboardMonth" 
          :day="appStore.selectedDashboardDay" 
        />
      </div>

      <!-- 3. Lower Section: Distribution and Changes -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <DashboardDistribucionChart 
          :month="appStore.selectedDashboardMonth" 
          :day="appStore.selectedDashboardDay" 
        />
        <DashboardCambiosList 
          class="lg:col-span-2"
          :cambios="cambios"
          :total-cambios="kpis?.cambios_vs_ayer"
          :month="appStore.selectedDashboardMonth"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { Loader2, CalendarOff, RefreshCw } from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'
import { useDashboardData } from '../composables/useDashboardData'

import DashboardKpis from '../components/DashboardKpis.vue'
import DashboardEvolutionChart from '../components/DashboardEvolutionChart.vue'
import DashboardNovedadesChart from '../components/DashboardNovedadesChart.vue'
import DashboardDistribucionChart from '../components/DashboardDistribucionChart.vue'
import DashboardCambiosList from '../components/DashboardCambiosList.vue'

const appStore = useAppStore()
const { loading, hasError, kpis, cambios, loadDashboardData } = useDashboardData()

onMounted(() => {
  loadDashboardData()
})

watch(
  () => [appStore.selectedDashboardMonth, appStore.selectedDashboardDay],
  () => {
    loadDashboardData()
  }
)

watch(
  () => appStore.syncStatus,
  (newStatus) => {
    if (newStatus === 'success') {
      loadDashboardData()
    }
  }
)
</script>
