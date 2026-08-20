<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2">
      <div class="w-2 h-4 bg-cyan-400 rounded-sm"></div>
      <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">Configuración de la Carga</h4>
    </div>
    
    <!-- Data Source Switcher -->
    <div class="space-y-1.5">
      <label class="text-xs uppercase font-bold text-slate-300">Origen de los Datos:</label>
      <div class="grid grid-cols-2 gap-2 bg-darkBg p-1.5 rounded-2xl border border-darkBorder max-w-md shadow-inner">
        <button 
          type="button"
          @click="$emit('update:source', 'local')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="source === 'local' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <HardDrive class="w-4 h-4" />
          <span>Subir Archivo</span>
        </button>
        <button 
          type="button"
          @click="$emit('update:source', 'drive')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="source === 'drive' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <Cloud class="w-4 h-4" />
          <span>Google Drive</span>
        </button>
      </div>
    </div>

    <!-- Mode Switcher -->
    <div class="space-y-1.5">
      <label class="text-xs uppercase font-bold text-slate-300">Modo de Carga:</label>
      <div class="grid grid-cols-2 gap-2 bg-darkBg p-1.5 rounded-2xl border border-darkBorder max-w-md shadow-inner">
        <button 
          type="button"
          @click="$emit('update:mode', 'dias')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'dias' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <CalendarDays class="w-4 h-4" />
          <span>Por Días</span>
        </button>
        <button 
          type="button"
          @click="$emit('update:mode', 'mes')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'mes' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <Calendar class="w-4 h-4" />
          <span>Mes Completo</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { HardDrive, Cloud, CalendarDays, Calendar } from 'lucide-vue-next'

defineProps<{
  source: 'local' | 'drive'
  mode: 'dias' | 'mes'
}>()

defineEmits<{
  (e: 'update:source', value: 'local' | 'drive'): void
  (e: 'update:mode', value: 'dias' | 'mes'): void
}>()
</script>
