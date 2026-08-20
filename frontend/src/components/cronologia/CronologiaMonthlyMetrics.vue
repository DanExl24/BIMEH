<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col justify-between min-h-[240px] border border-darkBorder shadow-xl space-y-4">
    <div>
      <div class="flex items-center gap-2.5">
        <Activity class="w-5 h-5 text-teal-400" />
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Métricas Operacionales del Mes
        </h3>
      </div>
      <p class="text-xs text-slate-400 mt-1 font-medium">Consolidado general de disponibilidad.</p>
    </div>

    <div v-if="!loadingCalendar" class="space-y-3 py-1">
      <div class="p-3 bg-darkBg/60 rounded-2xl border border-darkBorder/60 flex items-center justify-between">
        <span class="text-xs text-slate-400 font-medium">Promedio Mensual:</span>
        <span class="text-sm font-black text-cyan-300 font-mono">{{ avgMonthlyDispo }}%</span>
      </div>
      <div class="p-3 bg-darkBg/60 rounded-2xl border border-darkBorder/60 flex items-center justify-between">
        <span class="text-xs text-slate-400 font-medium">Mayor Disponibilidad:</span>
        <span class="text-xs font-bold text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">{{ maxDispoDay }}</span>
      </div>
      <div class="p-3 bg-darkBg/60 rounded-2xl border border-darkBorder/60 flex items-center justify-between">
        <span class="text-xs text-slate-400 font-medium">Menor Disponibilidad:</span>
        <span class="text-xs font-bold text-red-400 font-mono bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20">{{ minDispoDay }}</span>
      </div>
    </div>
    
    <div v-else class="flex justify-center items-center py-10">
      <Loader2 class="w-8 h-8 text-teal-400 animate-spin" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Activity, Loader2 } from 'lucide-vue-next'

defineProps<{
  loadingCalendar: boolean
  avgMonthlyDispo: number
  maxDispoDay: string
  minDispoDay: string
}>()
</script>

