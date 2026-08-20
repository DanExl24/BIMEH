<template>
  <div v-if="statusState === 'conflict'" class="bg-amber-500/10 border border-amber-500/25 p-4 rounded-xl space-y-3 text-amber-500 font-sans">
    <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      Conflicto de Duplicados
    </div>
    <p class="text-xs leading-relaxed text-amber-200/90 font-medium">
      {{ statusMessage }}
    </p>
    
    <!-- Conflict list -->
    <div class="max-h-24 overflow-y-auto bg-darkBg/60 border border-darkBorder/40 rounded-lg p-2 font-mono text-[10px] text-amber-300">
      <div v-for="c in conflicts" :key="c">{{ c }}</div>
    </div>

    <!-- Overwrite decision button -->
    <button 
      type="button" 
      @click="$emit('confirm-overwrite')"
      class="w-full py-2 bg-amber-600 hover:bg-amber-500 rounded-lg text-slate-100 font-bold text-xs transition-all shadow active:scale-95 cursor-pointer"
    >
      Sobreescribir y Cargar
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  statusState: 'success' | 'error' | 'conflict' | null
  statusMessage: string
  conflicts: string[]
}>()

defineEmits<{
  (e: 'confirm-overwrite'): void
}>()
</script>
