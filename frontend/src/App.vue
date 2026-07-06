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
    <Sidebar />

    <!-- Main Content Area -->
    <main class="flex-1 ml-64 p-8 min-h-screen flex flex-col">
      <!-- Top header layout -->
      <header class="flex items-center justify-between mb-8 border-b border-darkBorder/40 pb-4">
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
