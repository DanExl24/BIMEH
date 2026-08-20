<script setup lang="ts">
import { onMounted, ref } from 'vue'
import Sidebar from './components/layout/Sidebar.vue'
import ReportGenerationModal from './components/modals/ReportGenerationModal.vue'

import { 
  Menu, 
  Shield, 
  Calendar as CalendarIcon, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  Square
} from 'lucide-vue-next'

import { useAppStore } from './stores/appStore'
import { useAuthStore } from './stores/authStore'

const appStore = useAppStore()
const authStore = useAuthStore()

const isMobileMenuOpen = ref(false)

onMounted(async () => {
  await appStore.fetchAvailableDates()

  if (authStore.isAuthenticated) {
    const isValid = await authStore.checkMe()
    if (isValid) {
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
  <div class="min-h-screen bg-darkBg text-slate-100 overflow-x-hidden">
    <!-- Mobile/Tablet Top Navigation Header (visible under 1024px) -->
    <header 
      v-if="$route.name !== 'login'"
      class="lg:hidden fixed top-0 left-0 right-0 z-30 flex items-center justify-between px-4 bg-darkCard/95 border-b border-darkBorder backdrop-blur-md pt-[env(safe-area-inset-top,0px)] h-16 shadow-lg shadow-black/20"
    >
      <div class="flex items-center gap-3">
        <button 
          @click="isMobileMenuOpen = true"
          class="p-2 text-slate-300 hover:text-slate-100 rounded-xl hover:bg-darkBorder/60 transition-colors cursor-pointer"
          aria-label="Abrir menú de navegación"
        >
          <Menu class="w-6 h-6 text-cyan-400" />
        </button>
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center text-slate-950 font-black shadow-md shadow-cyan-500/20">
            <Shield class="w-4 h-4 stroke-[2.5]" />
          </div>
          <div>
            <span class="font-extrabold tracking-wider text-sm text-slate-100 uppercase block leading-tight">BIMEJ 12</span>
            <span class="text-[10px] text-cyan-400 font-semibold tracking-widest uppercase block">Comando</span>
          </div>
        </div>
      </div>

      <!-- Quick status indicator in mobile top bar -->
      <div v-if="appStore.syncStatus === 'running'" class="flex items-center gap-1.5 bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-1 rounded-lg">
        <Loader2 class="w-3.5 h-3.5 text-cyan-400 animate-spin" />
        <span class="text-[11px] font-mono text-cyan-300 font-bold">Sync...</span>
      </div>
    </header>

    <!-- Navigation Sidebar / Drawer -->
    <Sidebar 
      v-if="$route.name !== 'login'" 
      :isOpen="isMobileMenuOpen" 
      @close="isMobileMenuOpen = false" 
    />

    <!-- Main Content Area -->
    <main 
      class="min-h-screen flex flex-col min-w-0 transition-all duration-300"
      :class="$route.name !== 'login' ? 'ml-0 lg:ml-64 p-4 sm:p-6 lg:p-8 pt-20 lg:pt-8 pb-12' : ''"
    >
      <div class="max-w-7xl mx-auto w-full flex-1 flex flex-col space-y-6 min-w-0">

        <!-- Top Header & Global Context Bar -->
        <header v-if="$route.name !== 'login'" class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-darkBorder/60 pb-5">
          <div>
            <div class="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest mb-0.5">
              <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              Unidad Militar BIMEJ 12
            </div>
            <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
              {{ $route.meta.title || 'Módulo Operacional' }}
            </h1>
          </div>

          <!-- Contextual Filter Controls -->
          <div class="flex flex-wrap items-center gap-3">
            <!-- Month selector on Cronologia / Estadisticas -->
            <div 
              v-if="$route.name === 'cronologia' || $route.name === 'estadisticas'" 
              class="flex items-center gap-2 bg-darkCard/80 border border-darkBorder px-3 py-1.5 rounded-xl shadow-sm"
            >
              <CalendarIcon class="w-4 h-4 text-cyan-400 shrink-0" />
              <span class="text-xs text-slate-300 font-semibold uppercase tracking-wider">Mes:</span>
              <select 
                v-model="appStore.selectedMonth"
                class="bg-transparent text-xs font-semibold text-slate-100 outline-none cursor-pointer pr-2"
                aria-label="Seleccionar mes"
              >
                <option 
                  v-for="m in appStore.monthsWithAvailability" 
                  :key="m.name" 
                  :value="m.name"
                  :disabled="!m.isAvailable"
                  :class="!m.isAvailable ? 'text-slate-500 italic bg-darkBg' : 'text-slate-100 font-medium bg-darkCard'"
                >
                  {{ m.label }}
                </option>
              </select>
            </div>

            <!-- Month & Day Selectors on Dashboard -->
            <div 
              v-if="$route.name === 'dashboard'" 
              class="flex flex-wrap sm:flex-nowrap items-center gap-2 w-full md:w-auto"
            >
              <!-- Month dropdown -->
              <div class="flex items-center gap-2 bg-darkCard/80 border border-darkBorder px-3 py-2 rounded-xl flex-1 sm:flex-none shadow-sm">
                <CalendarIcon class="w-4 h-4 text-cyan-400 shrink-0" />
                <span class="text-xs text-slate-300 font-semibold uppercase tracking-wider">Mes:</span>
                <select 
                  v-model="appStore.selectedDashboardMonth"
                  class="bg-transparent text-xs font-semibold text-slate-100 outline-none cursor-pointer w-full sm:w-auto pr-2"
                  aria-label="Seleccionar mes del dashboard"
                >
                  <option value="" class="bg-darkCard text-slate-100">Todos los Meses</option>
                  <option 
                    v-for="m in appStore.monthsWithAvailability" 
                    :key="m.name" 
                    :value="m.name"
                    :disabled="!m.isAvailable"
                    :class="!m.isAvailable ? 'text-slate-500 italic bg-darkBg' : 'text-slate-100 font-medium bg-darkCard'"
                  >
                    {{ m.label }}
                  </option>
                </select>
              </div>

              <!-- Day dropdown -->
              <div class="flex items-center gap-2 bg-darkCard/80 border border-darkBorder px-3 py-2 rounded-xl flex-1 sm:flex-none shadow-sm">
                <span class="text-xs text-slate-300 font-semibold uppercase tracking-wider">Día:</span>
                <select 
                  v-model="appStore.selectedDashboardDay"
                  class="bg-transparent text-xs font-semibold text-slate-100 outline-none cursor-pointer w-full sm:w-auto pr-2"
                  aria-label="Seleccionar día del dashboard"
                >
                  <option value="" class="bg-darkCard text-slate-100">Todos los Días</option>
                  <option 
                    v-for="d in appStore.dashboardDaysFormatted" 
                    :key="d.val" 
                    :value="d.val"
                    :disabled="!d.isAvailable"
                    :class="!d.isAvailable ? 'text-slate-500 italic bg-darkBg' : 'text-slate-100 font-medium bg-darkCard'"
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
      </div>
    </main>

    <!-- Global Background Sync Floating Notification (Non-blocking pill) -->
    <div 
      v-if="appStore.syncStatus !== 'idle'" 
      class="fixed bottom-4 right-4 left-4 sm:left-auto z-40 glass-panel p-3 sm:p-4 rounded-2xl border flex items-center justify-between gap-3 transition-all duration-300 shadow-2xl max-w-[calc(100vw-2rem)] sm:max-w-sm"
      :class="appStore.syncStatus === 'running' ? 'border-cyan-500/40 shadow-cyan-500/10' : 
              appStore.syncStatus === 'success' ? 'border-emerald-500/40 shadow-emerald-500/10' : 'border-red-500/40 shadow-red-500/10'"
    >
      <!-- Icon/Spinner -->
      <div class="flex-shrink-0">
        <div v-if="appStore.syncStatus === 'running'" class="w-8 h-8 rounded-xl bg-cyan-500/15 flex items-center justify-center text-cyan-400">
          <Loader2 class="w-4 h-4 animate-spin" />
        </div>
        <div v-else-if="appStore.syncStatus === 'success'" class="w-8 h-8 rounded-xl bg-emerald-500/15 flex items-center justify-center text-emerald-400">
          <CheckCircle2 class="w-4 h-4 stroke-[2.5]" />
        </div>
        <div v-else class="w-8 h-8 rounded-xl bg-red-500/15 flex items-center justify-center text-red-400">
          <AlertCircle class="w-4 h-4 stroke-[2.5]" />
        </div>
      </div>
      
      <!-- Text details -->
      <div class="flex-1 min-w-0 font-sans">
        <p class="text-xs font-bold text-slate-200 truncate">
          {{ appStore.syncStatus === 'running' ? 'Sincronizando Drive' : 
             appStore.syncStatus === 'success' ? 'Sincronización Lista' : 'Error de Sincronización' }}
        </p>
        <p class="text-[11px] text-slate-400 truncate font-medium" :title="appStore.syncMessage">
          {{ appStore.syncMessage }}
        </p>
      </div>

      <!-- Timer overlay and Cancel button if running -->
      <div v-if="appStore.syncStatus === 'running'" class="flex items-center gap-1.5 shrink-0">
        <span class="text-[11px] font-mono text-cyan-400 bg-cyan-500/15 px-2 py-0.5 rounded-md font-bold">
          {{ Math.floor(appStore.syncSecondsElapsed / 60) }}m {{ appStore.syncSecondsElapsed % 60 }}s
        </span>
        <button 
          @click="appStore.cancelDriveSync()" 
          class="p-1.5 bg-red-500/15 hover:bg-red-500/25 text-red-400 border border-red-500/30 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1"
          title="Detener sincronización"
        >
          <Square class="w-3.5 h-3.5 fill-current" />
        </button>
      </div>

      <!-- Manual close button when not running -->
      <button 
        v-if="appStore.syncStatus !== 'running'"
        @click="appStore.clearSyncStatus()" 
        class="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-700/50 transition-all cursor-pointer shrink-0"
        title="Cerrar notificación"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Global Report Generation Modal Dialog -->
    <ReportGenerationModal />
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

