<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col space-y-5 max-w-full overflow-hidden border border-darkBorder shadow-xl">
    <div class="border-b border-darkBorder/60 pb-4">
      <div class="flex items-center gap-2.5">
        <div class="w-2 h-5 bg-cyan-400 rounded-sm"></div>
        <h4 class="text-sm sm:text-base font-bold text-slate-100 uppercase tracking-tight">
          Matriz de Disponibilidad: Personal vs Días del Mes
        </h4>
      </div>
      <p class="text-xs text-slate-400 mt-1 font-medium">
        Muestra la disponibilidad diaria de toda la unidad. La columna con el nombre se mantiene visible mientras te desplazas horizontalmente.
      </p>
    </div>

    <!-- Search and Legend inside Heatmap -->
    <div class="flex flex-col md:flex-row gap-4 items-stretch md:items-center justify-between">
      <div class="relative w-full md:w-80">
        <input 
          type="text" 
          :value="heatmapSearch"
          @input="$emit('update:heatmapSearch', ($event.target as HTMLInputElement).value)"
          placeholder="Buscar por apellidos o cédula..."
          class="w-full bg-darkBg border border-darkBorder rounded-xl pl-10 pr-4 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 shadow-inner"
        />
        <Search class="w-4 h-4 absolute left-3.5 top-3 text-slate-400 pointer-events-none" />
      </div>

      <!-- Tactical Legend -->
      <div class="flex items-center gap-3 text-xs text-slate-300 flex-wrap">
        <div class="flex items-center gap-1.5 font-medium">
          <span class="w-3 h-3 bg-emerald-500 rounded-sm shadow-sm"></span>
          <span>Disponible</span>
        </div>
        <div class="flex items-center gap-1.5 font-medium">
          <span class="w-3 h-3 bg-amber-500 rounded-sm shadow-sm"></span>
          <span>Novedad</span>
        </div>
        <div class="flex items-center gap-1.5 font-medium">
          <span class="w-3 h-3 bg-red-500 rounded-sm flex items-center justify-center font-bold text-[9px] text-white">R</span>
          <span>Retirado</span>
        </div>
        <div class="flex items-center gap-1.5 font-medium">
          <span class="w-3 h-3 bg-darkBg border border-darkBorder rounded-sm"></span>
          <span class="text-slate-500">Sin registro</span>
        </div>
      </div>
    </div>

    <!-- Matrix container with Sticky Left Column -->
    <div class="overflow-x-auto border border-darkBorder rounded-2xl shadow-inner bg-darkBg/40">
      <div v-if="loadingHeatmap" class="flex justify-center items-center py-24">
        <Loader2 class="w-8 h-8 text-cyan-400 animate-spin" />
      </div>
      <div v-else-if="paginatedHeatmap.length > 0" class="min-w-[1200px]">
        <table class="w-full text-left border-collapse table-fixed">
          <thead>
            <tr class="border-b border-darkBorder text-xs text-slate-300 font-mono bg-darkBg/90 backdrop-blur-md">
              <!-- Sticky Integrante Header Column -->
              <th class="py-3 px-3 sm:px-4 w-36 sm:w-48 md:w-56 text-left font-bold sticky left-0 bg-darkCard/95 z-20 sticky-col-shadow text-slate-100 uppercase tracking-wider text-xs">
                Integrante
              </th>
              <!-- Day Columns -->
              <th 
                v-for="d in heatmapData.fechas" 
                :key="d"
                class="py-3 text-center w-9 font-bold text-slate-400"
                :title="d"
              >
                {{ getDayNum(d) }}
              </th>
            </tr>
          </thead>
          <tbody class="text-xs">
            <tr 
              v-for="p in paginatedHeatmap" 
              :key="p.cedula"
              class="border-b border-darkBorder/30 hover:bg-slate-800/30 transition-colors group"
            >
              <!-- Sticky Integrante Name and CC -->
              <td class="py-2.5 px-3 sm:px-4 truncate font-bold text-slate-200 uppercase sticky left-0 bg-darkCard/95 z-10 sticky-col-shadow group-hover:bg-slate-900 transition-colors w-36 sm:w-48 md:w-56" :title="p.nombre">
                <router-link :to="`/personal/${p.cedula}`" class="hover:text-cyan-300 block truncate">
                  {{ p.nombre }}
                </router-link>
                <span class="text-[11px] text-slate-400 block font-mono font-normal">CC {{ p.cedula }}</span>
              </td>

              <!-- Day cells -->
              <td 
                v-for="(est, i) in p.estados" 
                :key="i"
                class="py-2.5 text-center w-9"
                :title="`${p.nombre} - ${heatmapData.fechas[i]}: ${est}`"
              >
                <div 
                  class="w-6 h-6 mx-auto rounded-md transition-all flex items-center justify-center font-bold text-xs shadow-sm group-hover:scale-105"
                  :class="getHeatmapCellClass(est)"
                >
                  <span v-if="est === 'RETIRADO'" class="text-white font-bold text-[10px]">R</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-20 text-slate-400 text-xs font-medium">
        No se encontraron registros en la matriz para el mes seleccionado.
      </div>
    </div>

    <!-- Pagination controls -->
    <div v-if="!loadingHeatmap && filteredHeatmap.length > 0" class="flex flex-col sm:flex-row justify-between items-center gap-3 text-xs pt-2">
      <span class="text-slate-400 font-medium">
        Mostrando <strong class="text-slate-200">{{ (heatmapPage - 1) * heatmapLimit + 1 }} - {{ Math.min(heatmapPage * heatmapLimit, filteredHeatmap.length) }}</strong> de <strong class="text-slate-200">{{ filteredHeatmap.length }}</strong> integrantes
      </span>
      <div class="flex items-center gap-2">
        <button 
          type="button"
          @click="$emit('update:heatmapPage', heatmapPage - 1)" 
          :disabled="heatmapPage <= 1"
          class="px-3.5 py-1.5 bg-darkCard border border-darkBorder rounded-xl text-slate-300 hover:text-white disabled:opacity-30 disabled:pointer-events-none cursor-pointer flex items-center gap-1 font-bold shadow-sm"
        >
          <ChevronLeft class="w-3.5 h-3.5" />
          <span>Anterior</span>
        </button>
        <span class="font-bold text-slate-200 px-2">Pág. {{ heatmapPage }} / {{ maxHeatmapPage }}</span>
        <button 
          type="button"
          @click="$emit('update:heatmapPage', heatmapPage + 1)" 
          :disabled="heatmapPage >= maxHeatmapPage"
          class="px-3.5 py-1.5 bg-darkCard border border-darkBorder rounded-xl text-slate-300 hover:text-white disabled:opacity-30 disabled:pointer-events-none cursor-pointer flex items-center gap-1 font-bold shadow-sm"
        >
          <span>Siguiente</span>
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  Loader2 
} from 'lucide-vue-next'
import type { HeatmapResponse, HeatmapRow } from '@/types'
import { isAvailable } from '@utils/personal.utils'

defineProps<{
  heatmapData: HeatmapResponse
  filteredHeatmap: HeatmapRow[]
  paginatedHeatmap: HeatmapRow[]
  heatmapSearch: string
  loadingHeatmap: boolean
  heatmapPage: number
  heatmapLimit: number
  maxHeatmapPage: number
}>()

defineEmits<{
  (e: 'update:heatmapSearch', val: string): void
  (e: 'update:heatmapPage', page: number): void
}>()

const getHeatmapCellClass = (est: string) => {
  if (est === 'RETIRADO') return 'bg-red-500/80 text-white border border-red-500'
  if (est === 'N/A') return 'bg-darkBg border border-darkBorder/40 text-transparent'
  return isAvailable(est) ? 'bg-emerald-500/35 border border-emerald-500/50 text-emerald-300' : 'bg-amber-500/35 border border-amber-500/50 text-amber-300'
}

const getDayNum = (date_str: string) => {
  try {
    return date_str.split('-')[2]
  } catch {
    return date_str
  }
}
</script>
