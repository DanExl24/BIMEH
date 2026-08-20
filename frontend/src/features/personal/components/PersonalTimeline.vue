<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col h-[460px] border border-darkBorder shadow-xl min-w-0 max-w-full overflow-hidden">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 border-b border-darkBorder/60 pb-3.5">
      <div class="flex items-center gap-2">
        <Clock class="w-4 h-4 text-cyan-400" />
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Línea de Tiempo & Novedades
        </h3>
      </div>

      <!-- Selectores de Filtro -->
      <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
        <select 
          :value="filtroSubnovedad"
          @change="$emit('update:filtroSubnovedad', ($event.target as HTMLSelectElement).value)"
          class="bg-darkBg border border-darkBorder rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-200 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm flex-1 sm:flex-none"
        >
          <option value="">Todas las Novedades</option>
          <option v-for="s in subnovedadesList" :key="s" :value="s">{{ s }}</option>
        </select>
        <select 
          :value="filtroMes"
          @change="$emit('update:filtroMes', ($event.target as HTMLSelectElement).value)"
          class="bg-darkBg border border-darkBorder rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-200 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm flex-1 sm:flex-none"
        >
          <option value="">Todos los Meses</option>
          <option v-for="m in mesesDisponibles" :key="m.num" :value="m.num">{{ m.name }}</option>
        </select>

        <select 
          :value="filtroDia"
          @change="$emit('update:filtroDia', ($event.target as HTMLSelectElement).value)"
          class="bg-darkBg border border-darkBorder rounded-xl px-3 py-1.5 text-xs font-semibold text-slate-200 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm flex-1 sm:flex-none"
        >
          <option value="">Todos los Días</option>
          <option v-for="d in diasDelMes" :key="d" :value="d">{{ d }}</option>
        </select>
      </div>
    </div>

    <!-- Timeline Content -->
    <div class="flex-1 overflow-y-auto pr-2 space-y-4">
      <div v-if="filteredHistorial.length === 0" class="text-center py-20 text-slate-400 text-xs font-medium">
        No se encontraron registros para los filtros seleccionados.
      </div>
      <div 
        v-else
        v-for="h in filteredHistorial" 
        :key="h.fecha"
        class="relative pl-6 border-l-2 border-darkBorder hover:border-cyan-500/50 transition-colors pb-4 last:pb-0 group"
      >
        <!-- Timeline node -->
        <div 
          class="absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full border-2 border-darkBg shadow-sm transition-transform group-hover:scale-125"
          :class="isAvailable(h.subnovedad) ? 'bg-emerald-400 shadow-emerald-500/50' : 'bg-amber-400 shadow-amber-500/50'"
        ></div>

        <div class="flex items-center justify-between gap-2 flex-wrap">
          <span class="text-xs font-mono font-bold text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 px-2 py-0.5 rounded-md">
            {{ h.fecha }}
          </span>
          <span 
            class="text-xs font-bold px-2.5 py-0.5 rounded-md border uppercase inline-block"
            :class="isAvailable(h.subnovedad) ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400' : 'bg-amber-500/10 border-amber-500/25 text-amber-400'"
          >
            {{ h.subnovedad }}
          </span>
        </div>
        <div class="mt-1.5 space-y-1">
          <p class="text-xs text-slate-200 font-semibold uppercase leading-snug">{{ h.descripcion || 'Sin descripción registrada' }}</p>
          <p v-if="h.desde || h.hasta" class="text-xs text-slate-400 font-mono">
            Rango: <span class="text-slate-300 font-bold">{{ h.desde || 'N/A' }}</span> al <span class="text-slate-300 font-bold">{{ h.hasta || 'N/A' }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Clock } from 'lucide-vue-next'
import type { HistorialRegistro } from '@/types'
import { isAvailable } from '@utils/personal.utils'

defineProps<{
  filtroMes: string
  filtroDia: string
  filtroSubnovedad: string
  mesesDisponibles: Array<{ num: string; name: string }>
  subnovedadesList: string[]
  diasDelMes: string[]
  filteredHistorial: HistorialRegistro[]
}>()

defineEmits<{
  (e: 'update:filtroMes', val: string): void
  (e: 'update:filtroDia', val: string): void
  (e: 'update:filtroSubnovedad', val: string): void
}>()
</script>
