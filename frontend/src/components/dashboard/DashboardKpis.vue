<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
    <!-- 1. Total Personal Registrado -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between relative overflow-hidden group hover:border-slate-700 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Efectivo Total</span>
        <div class="w-8 h-8 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-300 group-hover:scale-105 transition-transform">
          <Users class="w-4 h-4 text-slate-200" />
        </div>
      </div>
      <div class="mt-3">
        <span class="text-2xl sm:text-3xl font-black text-slate-100 font-mono tracking-tight">{{ kpis?.total_personal ?? 0 }}</span>
        <span class="text-xs text-slate-400 block mt-1 font-medium">Hombres registrados</span>
      </div>
      <div class="w-full bg-slate-800 h-1 rounded-full mt-3 overflow-hidden">
        <div class="bg-slate-500 h-full rounded-full w-full"></div>
      </div>
    </div>

    <!-- 2. Personal Disponible -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between relative overflow-hidden group hover:border-emerald-500/40 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Disponibles</span>
        <div class="w-8 h-8 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform shadow-sm shadow-emerald-500/10">
          <ShieldCheck class="w-4 h-4 stroke-[2.5]" />
        </div>
      </div>
      <div class="mt-3">
        <span class="text-2xl sm:text-3xl font-black text-emerald-400 font-mono tracking-tight">{{ kpis?.disponibles ?? 0 }}</span>
        <span class="text-xs text-emerald-300/80 block mt-1 font-medium">En servicio activo</span>
      </div>
      <div class="w-full bg-darkBg h-1.5 rounded-full mt-3 overflow-hidden">
        <div 
          class="bg-emerald-500 h-full rounded-full transition-all duration-500 shadow-sm shadow-emerald-500/50"
          :style="{ width: `${kpis?.total_personal ? ((kpis.disponibles / kpis.total_personal) * 100) : 0}%` }"
        ></div>
      </div>
    </div>

    <!-- 3. En Novedades -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between relative overflow-hidden group hover:border-amber-500/40 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-amber-400 uppercase tracking-wider">En Novedades</span>
        <div class="w-8 h-8 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 group-hover:scale-105 transition-transform shadow-sm shadow-amber-500/10">
          <AlertTriangle class="w-4 h-4 stroke-[2.5]" />
        </div>
      </div>
      <div class="mt-3">
        <span class="text-2xl sm:text-3xl font-black text-amber-400 font-mono tracking-tight">{{ kpis?.novedades ?? 0 }}</span>
        <span class="text-xs text-amber-300/80 block mt-1 font-medium">Permisos, excusas, etc.</span>
      </div>
      <div class="w-full bg-darkBg h-1.5 rounded-full mt-3 overflow-hidden">
        <div 
          class="bg-amber-500 h-full rounded-full transition-all duration-500 shadow-sm shadow-amber-500/50"
          :style="{ width: `${kpis?.total_personal ? ((kpis.novedades / kpis.total_personal) * 100) : 0}%` }"
        ></div>
      </div>
    </div>

    <!-- 4. Disponibilidad Operacional % -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-col justify-between relative overflow-hidden group hover:border-cyan-500/40 transition-all">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-cyan-400 uppercase tracking-wider">Índice Operativo</span>
        <div class="w-8 h-8 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform shadow-sm shadow-cyan-500/10">
          <Activity class="w-4 h-4 stroke-[2.5]" />
        </div>
      </div>
      <div class="mt-3">
        <span class="text-2xl sm:text-3xl font-black text-cyan-400 font-mono tracking-tight">{{ kpis?.disponibilidad ?? 0 }}%</span>
        <span class="text-xs text-cyan-300/80 block mt-1 font-medium">Capacidad operacional</span>
      </div>
      <div class="w-full bg-darkBg h-1.5 rounded-full mt-3 overflow-hidden">
        <div 
          class="bg-cyan-500 h-full rounded-full transition-all duration-500 shadow-sm shadow-cyan-500/50"
          :style="{ width: `${kpis?.disponibilidad || 0}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  Users, 
  ShieldCheck, 
  AlertTriangle, 
  Activity 
} from 'lucide-vue-next'
import type { KPIData } from '../../types'

defineProps<{
  kpis: KPIData | null
}>()
</script>

