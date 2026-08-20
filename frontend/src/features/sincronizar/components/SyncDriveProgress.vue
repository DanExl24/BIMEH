<template>
  <div v-if="appStore.syncStatus !== 'idle'" class="glass-panel p-5 sm:p-7 rounded-3xl space-y-4 border border-darkBorder shadow-xl">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Loader2 v-if="appStore.syncStatus === 'running'" class="w-5 h-5 text-cyan-400 animate-spin" />
        <CheckCircle2 v-else-if="appStore.syncStatus === 'success'" class="w-5 h-5 text-emerald-400" />
        <AlertCircle v-else-if="appStore.syncStatus === 'error'" class="w-5 h-5 text-red-400" />
        
        <div>
          <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
            {{ getSyncTitle() }}
          </h4>
          <p class="text-xs text-slate-400 mt-0.5">{{ appStore.syncMessage || 'Procesando en segundo plano...' }}</p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <span v-if="appStore.syncStatus === 'running'" class="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
          {{ appStore.syncSecondsElapsed }}s
        </span>
        <button 
          v-if="appStore.syncStatus === 'running'"
          type="button"
          @click="appStore.cancelDriveSync()"
          class="px-2.5 py-1 bg-red-500/15 hover:bg-red-500/25 border border-red-500/30 text-red-300 rounded-lg text-xs font-bold transition-all cursor-pointer"
        >
          Cancelar
        </button>
        <button 
          v-else
          type="button"
          @click="appStore.clearSyncStatus()"
          class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-bold transition-all cursor-pointer"
        >
          Cerrar
        </button>
      </div>
    </div>

    <!-- Progress indicator bar -->
    <div class="w-full bg-darkBg h-2 rounded-full overflow-hidden border border-darkBorder">
      <div 
        class="h-full rounded-full transition-all duration-300"
        :class="getProgressBarClass()"
        :style="{ width: appStore.syncStatus === 'running' ? '100%' : '100%' }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  Loader2, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'

const appStore = useAppStore()

const getSyncTitle = () => {
  switch (appStore.syncStatus) {
    case 'running': return 'Sincronización en Proceso'
    case 'success': return 'Sincronización Completada'
    case 'error': return 'Error en Sincronización'
    default: return 'Estado de Sincronización'
  }
}

const getProgressBarClass = () => {
  switch (appStore.syncStatus) {
    case 'running': return 'bg-gradient-to-r from-cyan-500 to-blue-500 animate-pulse shadow-sm shadow-cyan-500/50'
    case 'success': return 'bg-emerald-500 shadow-sm shadow-emerald-500/50'
    case 'error': return 'bg-red-500 shadow-sm shadow-red-500/50'
    default: return 'bg-cyan-500'
  }
}
</script>
