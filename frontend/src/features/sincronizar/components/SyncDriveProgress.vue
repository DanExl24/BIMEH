<template>
  <div v-if="appStore.syncStatus !== 'idle'" class="glass-panel p-5 sm:p-7 rounded-3xl space-y-4 border border-darkBorder shadow-xl">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <Loader2 v-if="appStore.syncStatus === 'syncing'" class="w-5 h-5 text-cyan-400 animate-spin" />
        <CheckCircle2 v-else-if="appStore.syncStatus === 'success'" class="w-5 h-5 text-emerald-400" />
        <AlertCircle v-else-if="appStore.syncStatus === 'error'" class="w-5 h-5 text-red-400" />
        <AlertTriangle v-else-if="appStore.syncStatus === 'conflict'" class="w-5 h-5 text-amber-400" />
        
        <div>
          <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
            {{ getSyncTitle() }}
          </h4>
          <p class="text-xs text-slate-400 mt-0.5">{{ appStore.syncCurrentStep || 'En cola...' }}</p>
        </div>
      </div>

      <span v-if="appStore.syncStatus === 'syncing'" class="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-lg border border-cyan-500/20">
        {{ Math.round(appStore.syncProgress) }}%
      </span>
    </div>

    <!-- Progress Bar -->
    <div class="w-full bg-darkBg h-2.5 rounded-full overflow-hidden border border-darkBorder">
      <div 
        class="h-full transition-all duration-300 rounded-full"
        :class="getProgressBarClass()"
        :style="{ width: `${appStore.syncProgress}%` }"
      ></div>
    </div>

    <!-- Conflict resolution in Drive mode -->
    <div v-if="appStore.syncStatus === 'conflict'" class="pt-2 flex items-center gap-3">
      <button 
        type="button"
        @click="$emit('confirm-drive-overwrite')"
        class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-xl text-xs transition-colors cursor-pointer"
      >
        Sobrescribir y Continuar
      </button>
      <button 
        type="button"
        @click="appStore.resetSync()"
        class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl text-xs transition-colors cursor-pointer"
      >
        Cancelar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle 
} from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'

const appStore = useAppStore()

defineEmits<{
  (e: 'confirm-drive-overwrite'): void
}>()

const getSyncTitle = () => {
  switch (appStore.syncStatus) {
    case 'syncing': return 'Sincronización en Proceso'
    case 'success': return 'Sincronización Completada'
    case 'error': return 'Error en Sincronización'
    case 'conflict': return 'Conflicto de Datos Detectado'
    default: return 'Estado de Sincronización'
  }
}

const getProgressBarClass = () => {
  switch (appStore.syncStatus) {
    case 'syncing': return 'bg-gradient-to-r from-cyan-500 to-blue-500 shadow-sm shadow-cyan-500/50'
    case 'success': return 'bg-emerald-500 shadow-sm shadow-emerald-500/50'
    case 'error': return 'bg-red-500 shadow-sm shadow-red-500/50'
    case 'conflict': return 'bg-amber-500 shadow-sm shadow-amber-500/50'
    default: return 'bg-cyan-500'
  }
}
</script>
