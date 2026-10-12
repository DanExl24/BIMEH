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
      <!-- Barra Táctica de Comandancia S-1 & Botón Parte de las 06:00 -->
      <div class="glass-panel px-4 py-3 sm:px-6 sm:py-3.5 rounded-2xl flex flex-wrap items-center justify-between gap-3 border-cyan-500/30 bg-gradient-to-r from-slate-900/90 via-cyan-950/20 to-slate-900/90 shadow-lg shadow-cyan-950/10">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
            <ShieldAlert class="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-black uppercase tracking-widest text-cyan-400">SECCIÓN PERSONAL (S-1)</span>
              <span class="text-[10px] text-slate-500">•</span>
              <span class="text-[10px] text-slate-400 font-mono">{{ kpis?.fecha || 'Vigente' }}</span>
            </div>
            <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wide">
              Mando Proactivo & Inteligencia Preventiva de Fuerza
            </h3>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <router-link
            to="/mando-s1"
            class="px-3 py-2 bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
          >
            <span>Ver Centro S-1 Completo</span>
            <ExternalLink class="w-3.5 h-3.5 text-cyan-400" />
          </router-link>

          <button 
            @click="showBriefingModal = true"
            class="px-4 py-2 sm:px-5 sm:py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black rounded-xl text-xs uppercase tracking-wider transition-all flex items-center gap-2 shadow-md shadow-cyan-500/25 hover:shadow-cyan-500/40 cursor-pointer"
          >
            <FileText class="w-4 h-4 stroke-[2.5]" />
            <span>El Parte de las 06:00</span>
          </button>
        </div>
      </div>

      <!-- 1. KPIs Section -->
      <DashboardKpis :kpis="kpis" />

      <!-- 2. Nueva Sección: Radar de Fatiga & Proyección de Fuerza -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <DashboardFatigueRadar 
          :month="appStore.selectedDashboardMonth"
          :day="appStore.selectedDashboardDay"
          :fecha="fechaEfectiva" 
        />
        <DashboardForceProjection 
          :month="appStore.selectedDashboardMonth"
          :day="appStore.selectedDashboardDay"
          :fecha="fechaEfectiva" 
        />
      </div>

      <!-- 3. Charts Section -->
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

      <!-- 4. Lower Section: Distribution and Changes -->
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

    <!-- Modal "El Parte de las 06:00" -->
    <CommandBriefingModal 
      v-model:is-open="showBriefingModal" 
      :month="appStore.selectedDashboardMonth"
      :day="appStore.selectedDashboardDay"
      :fecha="fechaEfectiva" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Loader2, CalendarOff, RefreshCw, ShieldAlert, FileText, ExternalLink } from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'
import { useDashboardData } from '../composables/useDashboardData'

import DashboardKpis from '../components/DashboardKpis.vue'
import DashboardEvolutionChart from '../components/DashboardEvolutionChart.vue'
import DashboardNovedadesChart from '../components/DashboardNovedadesChart.vue'
import DashboardDistribucionChart from '../components/DashboardDistribucionChart.vue'
import DashboardCambiosList from '../components/DashboardCambiosList.vue'
import DashboardFatigueRadar from '../components/DashboardFatigueRadar.vue'
import DashboardForceProjection from '../components/DashboardForceProjection.vue'
import CommandBriefingModal from '../components/CommandBriefingModal.vue'

const appStore = useAppStore()
const { loading, hasError, kpis, cambios, loadDashboardData } = useDashboardData()

const showBriefingModal = ref(false)

const fechaEfectiva = computed(() => {
  if (kpis.value?.fecha && /^\d{4}-\d{2}-\d{2}$/.test(kpis.value.fecha)) {
    return kpis.value.fecha
  }
  return undefined
})

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
