<script setup lang="ts">
import { onMounted } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'
import { useAppStore } from './stores/appStore'

const appStore = useAppStore()
const diasDelMes = Array.from({ length: 31 }, (_, i) => String(i + 1).padStart(2, '0'))

onMounted(() => {
  appStore.fetchAvailableDates()
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
                <option v-for="d in diasDelMes" :key="d" :value="d">{{ d }}</option>
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

      <!-- Timer overlay if running -->
      <div v-if="appStore.syncStatus === 'running'" class="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded-md font-bold">
        {{ Math.floor(appStore.syncSecondsElapsed / 60) }}m {{ appStore.syncSecondsElapsed % 60 }}s
      </div>
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
