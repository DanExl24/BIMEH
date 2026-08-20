<template>
  <div v-if="statusState === 'conflict'" class="bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs p-5 rounded-2xl space-y-3">
    <div class="flex items-center gap-2 font-bold text-amber-400">
      <AlertTriangle class="w-4 h-4" />
      <span>Conflicto de Datos Existentes</span>
    </div>
    <p>{{ statusMessage }}</p>
    <div v-if="conflicts.length > 0" class="flex flex-wrap gap-1.5 py-1">
      <span v-for="c in conflicts" :key="c" class="bg-amber-500/20 px-2 py-0.5 rounded font-mono font-bold text-amber-300">
        {{ c }}
      </span>
    </div>
    <div class="flex items-center gap-3 pt-2">
      <button 
        type="button" 
        @click="$emit('confirm-overwrite')"
        class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-xl text-xs transition-colors cursor-pointer"
      >
        Sobrescribir y Continuar
      </button>
      <button 
        type="button" 
        @click="$emit('cancel')"
        class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold rounded-xl text-xs transition-colors cursor-pointer"
      >
        Cancelar
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'

defineProps<{
  statusState: string
  statusMessage: string
  conflicts: string[]
}>()

defineEmits<{
  (e: 'confirm-overwrite'): void
  (e: 'cancel'): void
}>()
</script>
