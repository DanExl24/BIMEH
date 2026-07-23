<script setup lang="ts">
import { onMounted, computed } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'

import { useAppStore } from './stores/appStore'
import { useAuthStore } from './stores/authStore'


const appStore = useAppStore()
const authStore = useAuthStore()

const MONTH_NUMBER_MAP: Record<string, string> = {
  'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
  'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
  'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
}

const diasDelMesFormatted = computed(() => {
  const selectedMonth = appStore.selectedDashboardMonth
  if (!selectedMonth) {
    return Array.from({ length: 31 }, (_, i) => {
      const d = String(i + 1).padStart(2, '0')
      return { val: d, label: d, isAvailable: true }
    })
  }

  const mNum = MONTH_NUMBER_MAP[selectedMonth.toUpperCase()]
  if (!mNum) {
    return Array.from({ length: 31 }, (_, i) => {
      const d = String(i + 1).padStart(2, '0')
      return { val: d, label: d, isAvailable: true }
    })
  }

  const availableDaysInMonth = new Set(
    appStore.availableDates
      .filter(dateStr => {
        const parts = dateStr.split('-')
        return parts.length === 3 && parts[1] === mNum
      })
      .map(dateStr => dateStr.split('-')[2])
  )

  return Array.from({ length: 31 }, (_, i) => {
    const d = String(i + 1).padStart(2, '0')
    const hasData = availableDaysInMonth.has(d)
    return {
      val: d,
      label: hasData ? d : `${d} - (SIN REGISTRO)`,
      isAvailable: hasData
    }
  })
})

onMounted(async () => {
  await appStore.fetchAvailableDates()

  if (authStore.isAuthenticated) {
    const isValid = await authStore.checkMe()
    if (isValid) {
      // Auto-sync current month in background on app load
      const currentMonthIndex = new Date().getMonth()
      const monthNames = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
      const currentMonthName = monthNames[currentMonthIndex]

      appStore.startDriveSync({
        tipo: 'mes',
        mes: currentMonthName,
        overwrite: false
      })
    }
  }
})

</script>

<template>
  <div class="min-h-screen bg-darkBg text-slate-100 flex">
    <!-- Navigation Sidebar -->
    <Sidebar v-if="$route.name !== 'login'" />

    <!-- Main Content Area -->
    <main 
      class="flex-1 min-h-screen flex flex-col"
      :class="$route.name !== 'login' ? 'ml-64 p-8' : ''"
    >
      <!-- Top header layout -->
      <header v-if="$route.name !== 'login'" class="flex items-center justify-between mb-8 border-b border-darkBorder/40 pb-4">
        <div>
          <h2 class="text-xs text-slate-400 font-semibold uppercase tracking-widest">Unidad Militar BIMEJ 12</h2>
          <h1 class="text-xl font-bold tracking-tight text-slate-100">
            {{ $route.name === 'dashboard' ? 'Módulo de Dashboard Operacional' : 
               $route.name === 'personal' ? 'Buscador y Perfiles de Personal' :
               $route.name === 'personal-detalle' ? 'Detalle Histórico de Integrante' :
               $route.name === 'estadisticas' ? 'Análisis de Novedades y Tendencias' :
               $route.name === 'cronologia' ? 'Cronología de Actividad Diaria' : 'Reportes de Personal' }}
          </h1>
        </div>

        <!-- Global controls for selecting date/month -->
        <div class="flex items-center gap-4">
          <!-- Show Month picker only on Cronologia or Estadisticas -->
          <div v-if="$route.name === 'cronologia' || $route.name === 'estadisticas'" class="flex items-center gap-2">
            <span class="text-xs text-slate-400 font-medium">Mes:</span>
            <select 
              v-model="appStore.selectedMonth"
              class="bg-darkCard border border-darkBorder rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-cyan-500/50"
            >
              <option v-for="m in appStore.months" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>

          <!-- Show Month and Day pickers on Dashboard -->
          <div v-if="$route.name === 'dashboard'" class="flex items-center gap-3">
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400 font-medium">Mes:</span>
              <select 
                v-model="appStore.selectedDashboardMonth"
                class="bg-darkCard border border-darkBorder rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todos los Meses</option>
                <option v-for="m in appStore.months" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-400 font-medium">Día:</span>
              <select 
                v-model="appStore.selectedDashboardDay"
                class="bg-darkCard border border-darkBorder rounded-lg px-3 py-1.5 text-sm text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todos los Días</option>
                <option 
                  v-for="d in diasDelMesFormatted" 
                  :key="d.val" 
                  :value="d.val"
                  :class="!d.isAvailable ? 'text-slate-500 italic' : 'text-slate-100 font-medium'"
                >
                  {{ d.label }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </header>

      <!-- View Wrapper -->
      <div class="flex-1 flex flex-col">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Global Background Sync Floating Status -->
    <div 
      v-if="appStore.syncStatus !== 'idle'" 
      class="fixed bottom-6 right-6 z-50 glass-panel p-4 rounded-xl border max-w-sm flex items-center gap-3 transition-all duration-300 shadow-2xl animate-fade-in"
      :class="appStore.syncStatus === 'running' ? 'border-cyan-500/30 shadow-cyan-500/5' : 
              appStore.syncStatus === 'success' ? 'border-emerald-500/30 shadow-emerald-500/5' : 'border-red-500/30 shadow-red-500/5'"
    >
      <!-- Icon/Spinner -->
      <div class="flex-shrink-0">
        <div v-if="appStore.syncStatus === 'running'" class="w-8 h-8 rounded-full bg-cyan-500/10 flex items-center justify-center text-cyan-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 7.89" />
          </svg>
        </div>
        <div v-else-if="appStore.syncStatus === 'success'" class="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4" />
          </svg>
        </div>
        <div v-else class="w-8 h-8 rounded-full bg-red-500/10 flex items-center justify-center text-red-400">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
      </div>
      
      <!-- Text details -->
      <div class="flex-1 min-w-0 font-sans">
        <p class="text-xs font-bold text-slate-200">
          {{ appStore.syncStatus === 'running' ? 'Sincronizando Google Drive...' : 
             appStore.syncStatus === 'success' ? 'Sincronización Completada' : 'Error de Sincronización' }}
        </p>
        <p class="text-[10px] text-slate-500 truncate mt-0.5 font-medium">
          {{ appStore.syncMessage }}
        </p>
      </div>

      <!-- Timer overlay and Cancel button if running -->
      <div v-if="appStore.syncStatus === 'running'" class="flex items-center gap-2 shrink-0">
        <div class="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded-md font-bold">
          {{ Math.floor(appStore.syncSecondsElapsed / 60) }}m {{ appStore.syncSecondsElapsed % 60 }}s
        </div>
        <button 
          @click="appStore.cancelDriveSync()" 
          class="px-2 py-1 bg-red-500/15 hover:bg-red-500/25 text-red-400 border border-red-500/30 rounded-md text-[10px] font-bold transition-all cursor-pointer flex items-center gap-1 active:scale-95"
          title="Detener sincronización"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>Cancelar</span>
        </button>
      </div>

      <!-- Manual close button when not running -->
      <button 
        v-if="appStore.syncStatus !== 'running'"
        @click="appStore.clearSyncStatus()" 
        class="text-slate-400 hover:text-slate-200 p-1 rounded-lg hover:bg-slate-700/50 transition-all cursor-pointer shrink-0 ml-1"
        title="Cerrar notificación"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

    </div>
  </div>
</template>


<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
