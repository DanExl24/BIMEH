<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
    <!-- 1. Tasa de Disponibilidad -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-cyan-500/40 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Disponibilidad</span>
        <div class="w-8 h-8 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
          <TrendingUp class="w-4 h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-1">
        <span class="text-2xl sm:text-3xl font-black text-cyan-300 font-mono tracking-tight">{{ profile.tiempo_disponible_pct }}%</span>
      </div>
      <p class="text-xs text-slate-400 mt-1.5 font-medium">Porcentaje en servicio activo</p>
    </div>

    <!-- 2. Tasa de Novedades -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-amber-500/40 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-amber-400 uppercase tracking-wider">En Novedad</span>
        <div class="w-8 h-8 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
          <AlertTriangle class="w-4 h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-1">
        <span class="text-2xl sm:text-3xl font-black text-amber-400 font-mono tracking-tight">{{ profile.tiempo_novedades_pct }}%</span>
      </div>
      <p class="text-xs text-slate-400 mt-1.5 font-medium">Porcentaje fuera de servicio</p>
    </div>

    <!-- 3. Total Días en Novedad -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-slate-700 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Días Novedad</span>
        <div class="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
          <ClipboardList class="w-4 h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-2">
        <span class="text-2xl sm:text-3xl font-black text-slate-100 font-mono tracking-tight">{{ profile.total_novedades }}</span>
        <span class="text-xs font-semibold text-slate-400">días</span>
      </div>
      <p class="text-xs text-slate-400 mt-1.5 font-medium">Total acumulado en el año</p>
    </div>

    <!-- 4. Promedio Duración -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-slate-700 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Duración Media</span>
        <div class="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
          <Timer class="w-4 h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-2">
        <span class="text-2xl sm:text-3xl font-black text-slate-100 font-mono tracking-tight">{{ profile.promedio_duracion_novedades }}</span>
        <span class="text-xs font-semibold text-slate-400">días / evento</span>
      </div>
      <p class="text-xs text-slate-400 mt-1.5 font-medium">Promedio por cada novedad</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  TrendingUp, 
  AlertTriangle, 
  ClipboardList, 
  Timer 
} from 'lucide-vue-next'
import type { PersonalDetalle } from '../../types'

defineProps<{
  profile: PersonalDetalle
}>()
</script>

