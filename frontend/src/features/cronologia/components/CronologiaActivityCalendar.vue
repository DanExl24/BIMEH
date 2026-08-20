<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col justify-between min-h-[240px] border border-darkBorder shadow-xl space-y-4">
    <div>
      <div class="flex items-center gap-2.5">
        <CalendarDays class="w-5 h-5 text-cyan-400" />
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Calendario Diario de Disponibilidad ({{ selectedMonth }})
        </h3>
      </div>
      <p class="text-xs text-slate-400 mt-1 font-medium">
        Haz clic en cualquier día para desplegar su consolidado operacional y personal en novedad.
      </p>
    </div>

    <!-- Calendar Grid -->
    <div v-if="loadingCalendar" class="flex justify-center items-center py-10">
      <Loader2 class="w-8 h-8 text-cyan-400 animate-spin" />
    </div>
    
    <div v-else class="flex flex-wrap gap-2.5 py-1">
      <button 
        v-for="day in calendarData" 
        :key="day.fecha"
        type="button"
        @click="$emit('select-date', day.fecha)"
        class="w-11 h-11 sm:w-13 sm:h-13 min-w-[42px] min-h-[42px] sm:min-w-[50px] sm:min-h-[50px] rounded-xl sm:rounded-2xl flex flex-col items-center justify-center border transition-all duration-200 relative group cursor-pointer shadow-sm select-none"
        :class="[
          getDayColorClass(day.disponibilidad),
          day.fecha === activeDate ? 'ring-2 ring-cyan-400 scale-105 border-slate-100 z-10 shadow-lg shadow-cyan-500/20' : 'hover:scale-105'
        ]"
      >
        <span class="text-xs font-black font-mono">{{ getDayNum(day.fecha) }}</span>
        <span class="text-[10px] font-mono font-bold opacity-90">{{ Math.round(day.disponibilidad) }}%</span>

        <!-- Floating Tooltip -->
        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2.5 w-40 bg-darkCard border border-darkBorder text-slate-100 text-xs p-2.5 rounded-xl shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-none transition-all z-30 text-center font-sans">
          <p class="font-bold text-slate-200">{{ day.fecha }}</p>
          <p class="text-cyan-400 font-bold mt-0.5">Disponibilidad: {{ day.disponibilidad }}%</p>
          <p class="text-slate-400 text-[11px] mt-0.5 font-medium">{{ day.disponibles }} / {{ day.total_personal }} Efectivos</p>
        </div>
      </button>
    </div>

    <!-- Legend -->
    <div class="flex items-center gap-4 text-xs text-slate-400 border-t border-darkBorder/60 pt-3 flex-wrap">
      <span class="font-bold uppercase tracking-wider text-slate-300">Rango de Operatividad:</span>
      <div class="flex items-center gap-1.5 font-medium">
        <span class="w-3 h-3 bg-emerald-500/20 border border-emerald-500/40 rounded-md"></span>
        <span class="text-emerald-400 font-bold">&gt;= 80%</span> (Alta)
      </div>
      <div class="flex items-center gap-1.5 font-medium">
        <span class="w-3 h-3 bg-amber-500/20 border border-amber-500/40 rounded-md"></span>
        <span class="text-amber-400 font-bold">60% - 79%</span> (Media)
      </div>
      <div class="flex items-center gap-1.5 font-medium">
        <span class="w-3 h-3 bg-red-500/20 border border-red-500/40 rounded-md"></span>
        <span class="text-red-400 font-bold">&lt; 60%</span> (Baja)
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CalendarDays, Loader2 } from 'lucide-vue-next'
import type { CalendarioItem } from '@/types'

defineProps<{
  selectedMonth: string
  activeDate: string
  calendarData: CalendarioItem[]
  loadingCalendar: boolean
}>()

defineEmits<{
  (e: 'select-date', date: string): void
}>()

const getDayColorClass = (pct: number) => {
  if (pct >= 80) return 'bg-emerald-500/15 border-emerald-500/35 text-emerald-300 hover:bg-emerald-500/25'
  if (pct >= 60) return 'bg-amber-500/15 border-amber-500/35 text-amber-300 hover:bg-amber-500/25'
  return 'bg-red-500/15 border-red-500/35 text-red-300 hover:bg-red-500/25'
}

const getDayNum = (date_str: string) => {
  try {
    return date_str.split('-')[2]
  } catch {
    return date_str
  }
}
</script>
