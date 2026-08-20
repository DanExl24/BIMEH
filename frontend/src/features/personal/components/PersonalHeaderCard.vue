<template>
  <div class="glass-panel p-4 sm:p-7 rounded-3xl flex flex-col md:flex-row justify-between items-start md:items-center gap-5 border border-darkBorder shadow-xl min-w-0 max-w-full overflow-hidden">
    <div class="flex items-start gap-3 sm:gap-4 min-w-0 flex-1">
      <!-- Profile Badge Icon -->
      <div class="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-cyan-500/20 to-blue-600/10 border border-cyan-500/30 rounded-2xl flex items-center justify-center text-cyan-400 shadow-md shadow-cyan-500/10 shrink-0">
        <User class="w-6 h-6 sm:w-8 sm:h-8 stroke-[2]" />
      </div>
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2.5 sm:gap-3 flex-wrap">
          <h2 class="text-base sm:text-lg font-black text-slate-100 uppercase tracking-tight break-words">{{ profile.nombre }}</h2>
          <span 
            class="text-xs font-bold tracking-wider px-2.5 py-0.5 rounded-md border uppercase inline-flex items-center gap-1.5 shrink-0"
            :class="getStatusBadgeClass(profile.estado)"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="profile.estado === 'ACTIVO' ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'"></span>
            {{ profile.estado }}
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-1 font-mono">
          Cédula de Ciudadanía: <span class="text-slate-100 font-bold">{{ profile.cedula }}</span>
        </p>
        <p v-if="profile.fecha_retiro" class="text-xs text-red-400 mt-1 font-mono font-bold flex items-center gap-1">
          <CalendarX class="w-3.5 h-3.5" />
          Fecha de Retiro: {{ profile.fecha_retiro }}
        </p>
      </div>
    </div>

    <!-- Export Button (Trigger Modal) -->
    <div class="flex items-center gap-3 self-stretch md:self-auto justify-end">
      <button 
        type="button"
        @click="$emit('export')"
        class="w-full md:w-auto px-5 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl text-xs font-bold text-white flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer select-none"
      >
        <Download class="w-4 h-4 stroke-[2.5]" />
        <span>Generar Reporte Oficial</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Download, CalendarX } from 'lucide-vue-next'
import type { PersonalDetalle } from '@types'
import { getStatusBadgeClass } from '@utils/personal.utils'

defineProps<{
  profile: PersonalDetalle
}>()

defineEmits<{
  (e: 'export'): void
}>()
</script>
