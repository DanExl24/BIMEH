<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 min-w-0 max-w-full">
    <!-- 1. Total Registros / Días -->
    <div class="glass-panel p-3.5 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-cyan-500/40 transition-all">
      <div class="flex items-center justify-between gap-2">
        <span class="text-[11px] sm:text-xs font-semibold text-cyan-400 uppercase tracking-wider truncate">Total Registros</span>
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
          <ClipboardCheck class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-1.5">
        <span class="text-xl sm:text-3xl font-black text-cyan-300 font-mono tracking-tight">{{ kpis.total_registros.toLocaleString() }}</span>
        <span class="text-[11px] sm:text-xs font-semibold text-slate-400">días</span>
      </div>
      <p class="text-[11px] sm:text-xs text-slate-400 mt-1.5 font-medium truncate">Con la novedad asignada</p>
    </div>

    <!-- 2. Personal Único Afectado -->
    <div class="glass-panel p-3.5 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-blue-500/40 transition-all">
      <div class="flex items-center justify-between gap-2">
        <span class="text-[11px] sm:text-xs font-semibold text-blue-400 uppercase tracking-wider truncate">Efectivos Únicos</span>
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-blue-500/15 border border-blue-500/30 flex items-center justify-center text-blue-400 shrink-0">
          <Users class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-1.5">
        <span class="text-xl sm:text-3xl font-black text-blue-300 font-mono tracking-tight">{{ kpis.personal_unico.toLocaleString() }}</span>
        <span class="text-[11px] sm:text-xs font-semibold text-slate-400">integrantes</span>
      </div>
      <p class="text-[11px] sm:text-xs text-slate-400 mt-1.5 font-medium truncate">Total con este registro</p>
    </div>

    <!-- 3. Distribución Activos vs Retirados -->
    <div class="glass-panel p-3.5 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-emerald-500/40 transition-all">
      <div class="flex items-center justify-between gap-2">
        <span class="text-[11px] sm:text-xs font-semibold text-emerald-400 uppercase tracking-wider truncate">Estado Actual</span>
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
          <ShieldCheck class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
        </div>
      </div>
      <div class="mt-2 flex items-baseline gap-2">
        <span class="text-xl sm:text-2xl font-black text-emerald-300 font-mono tracking-tight">{{ kpis.activos_unicos }}</span>
        <span class="text-[10px] text-emerald-400/90 uppercase font-bold">Activos</span>
        <span class="text-slate-600">/</span>
        <span class="text-lg sm:text-xl font-black text-slate-400 font-mono tracking-tight">{{ kpis.retirados_unicos }}</span>
        <span class="text-[10px] text-slate-400 uppercase font-bold">Ret.</span>
      </div>
      <p class="text-[11px] sm:text-xs text-slate-400 mt-1.5 font-medium truncate">Distribución de fuerza</p>
    </div>

    <!-- 4. Rango Temporal -->
    <div class="glass-panel p-3.5 sm:p-5 rounded-2xl flex flex-col justify-between hover:border-slate-700 transition-all">
      <div class="flex items-center justify-between gap-2">
        <span class="text-[11px] sm:text-xs font-semibold text-slate-400 uppercase tracking-wider truncate">Rango Registrado</span>
        <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
          <Calendar class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
        </div>
      </div>
      <div class="mt-2">
        <span v-if="kpis.primera_fecha && kpis.ultima_fecha" class="text-xs sm:text-sm font-bold text-slate-200 font-mono block">
          {{ kpis.primera_fecha }} <span class="text-cyan-400 font-sans">al</span> {{ kpis.ultima_fecha }}
        </span>
        <span v-else class="text-sm font-semibold text-slate-500">Sin registros</span>
      </div>
      <p class="text-[11px] sm:text-xs text-slate-400 mt-1.5 font-medium truncate">Historial en el sistema</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ClipboardCheck, Users, ShieldCheck, Calendar } from 'lucide-vue-next'
import type { NovedadesKpis } from '../types/novedades.types'

defineProps<{
  kpis: NovedadesKpis
}>()
</script>
