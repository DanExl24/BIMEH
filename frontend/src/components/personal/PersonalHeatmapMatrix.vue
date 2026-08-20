<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl space-y-6 border border-darkBorder shadow-xl">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-darkBorder/60 pb-5">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="w-2 h-5 bg-cyan-400 rounded-sm"></div>
          <h3 class="text-sm sm:text-base font-bold text-slate-100 uppercase tracking-wide">
            Hoja de Ruta & Mapa de Calor
          </h3>
        </div>
        <p class="text-xs text-slate-400 mt-1 font-medium">
          Matriz de disponibilidad diaria: <span class="text-emerald-400 font-bold">D = Disponible</span>, <span class="text-amber-400 font-bold">N = Novedad</span>, <span class="text-red-400 font-bold">R = Retirado</span>.
        </p>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex bg-darkBg border border-darkBorder p-1 rounded-xl self-start sm:self-auto overflow-x-auto max-w-full">
        <button 
          type="button"
          @click="activeHeatmapTab = 'mensual'"
          class="px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all cursor-pointer flex items-center gap-1.5 whitespace-nowrap select-none"
          :class="activeHeatmapTab === 'mensual' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
        >
          <Calendar class="w-3.5 h-3.5" />
          <span>Vista Mensual</span>
        </button>
        <button 
          type="button"
          @click="activeHeatmapTab = 'anual'"
          class="px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all cursor-pointer flex items-center gap-1.5 whitespace-nowrap select-none"
          :class="activeHeatmapTab === 'anual' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
        >
          <Layers class="w-3.5 h-3.5" />
          <span>Vista Anual</span>
        </button>
        <button 
          type="button"
          @click="activeHeatmapTab = 'diario'"
          class="px-3.5 py-1.5 text-xs font-bold uppercase tracking-wider rounded-lg transition-all cursor-pointer flex items-center gap-1.5 whitespace-nowrap select-none"
          :class="activeHeatmapTab === 'diario' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
        >
          <FileSpreadsheet class="w-3.5 h-3.5" />
          <span>Reporte Detallado</span>
        </button>
      </div>
    </div>

    <!-- 1. Content: Vista Mensual -->
    <div v-if="activeHeatmapTab === 'mensual'" class="space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-darkBg/60 p-4 rounded-2xl border border-darkBorder/60">
        <div class="flex items-center gap-3">
          <label class="text-xs uppercase font-bold text-slate-300">Seleccionar Mes:</label>
          <select 
            v-model="selectedMonthlyHeatmapMonth"
            class="bg-darkCard border border-darkBorder rounded-xl px-3 py-1.5 text-xs font-bold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Export Monthly Heatmap -->
        <button 
          type="button"
          @click="$emit('export-month', selectedMonthlyHeatmapMonth)"
          class="px-4 py-2 bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center gap-2 transition-all cursor-pointer select-none active:scale-95 shadow-sm"
        >
          <Download class="w-4 h-4" />
          <span>Exportar Heatmap ({{ selectedMonthlyHeatmapMonth }})</span>
        </button>
      </div>

      <div class="bg-darkBg/80 p-4 rounded-2xl border border-darkBorder/60 overflow-x-auto shadow-inner">
        <div class="flex items-center gap-1.5 min-w-[720px] font-mono text-center pb-2">
          <div v-for="d in 31" :key="d" class="flex-1">
            <span class="text-xs text-slate-400 uppercase block mb-1.5 font-sans font-semibold">D{{ d }}</span>
            <div 
              class="w-8 h-8 mx-auto rounded-lg transition-colors flex items-center justify-center text-xs font-black shadow-sm"
              :class="getIndividualHeatmapCellClass(selectedMonthlyHeatmapMonth, d)"
              :title="`${selectedMonthlyHeatmapMonth} día ${d}: ${getStatusForDate(selectedMonthlyHeatmapMonth, d)}`"
            >
              {{ getIndividualHeatmapCellLetter(selectedMonthlyHeatmapMonth, d) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. Content: Vista Anual (Con Columna Congelada) -->
    <div v-else-if="activeHeatmapTab === 'anual'" class="space-y-4">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-darkBg/60 p-4 rounded-2xl border border-darkBorder/60">
        <span class="text-xs font-bold text-slate-200 uppercase tracking-wider">Matriz Heatmap Anual Completa</span>
        <button 
          type="button"
          @click="$emit('export-month', '')"
          class="px-4 py-2 bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center gap-2 transition-all cursor-pointer select-none active:scale-95 shadow-sm"
        >
          <Download class="w-4 h-4" />
          <span>Exportar Matriz Anual (Todos los Meses)</span>
        </button>
      </div>

      <div class="bg-darkBg/80 p-4 rounded-2xl border border-darkBorder/60 overflow-x-auto shadow-inner">
        <div class="space-y-2.5 min-w-[900px]">
          <!-- Header row for days -->
          <div class="flex items-center gap-1.5 font-mono text-xs text-slate-400">
            <div class="w-28 text-left font-bold pl-2 sticky left-0 bg-darkBg z-10 sticky-col-shadow">Mes</div>
            <div v-for="d in 31" :key="d" class="w-6.5 text-center font-bold">D{{ d }}</div>
          </div>
          
          <!-- Rows for months with Sticky Left Month Column -->
          <div v-for="m in activeMonths" :key="m" class="flex items-center gap-1.5 font-mono">
            <div class="w-28 text-xs font-bold text-slate-200 uppercase tracking-wider pl-2 py-1 sticky left-0 bg-darkBg z-10 sticky-col-shadow">
              {{ m }}
            </div>
            <div 
              v-for="d in 31" 
              :key="d" 
              class="w-6.5 h-6.5 rounded-md transition-colors flex items-center justify-center text-xs font-bold shadow-sm"
              :class="getIndividualHeatmapCellClass(m, d)"
              :title="`${m} ${d}: ${getStatusForDate(m, d)}`"
            >
              {{ getIndividualHeatmapCellLetter(m, d) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Content: Reporte Detallado (Tabla) -->
    <div v-else-if="activeHeatmapTab === 'diario'" class="space-y-4">
      <!-- Filters Row -->
      <div class="flex flex-col sm:flex-row gap-3 bg-darkBg/60 p-4 rounded-2xl border border-darkBorder/60">
        <div class="flex-1 relative">
          <input 
            type="text" 
            v-model="tableSearchQuery" 
            placeholder="Filtrar por descripción o subnovedad..."
            class="w-full bg-darkCard border border-darkBorder rounded-xl pl-10 pr-4 py-2.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 transition-colors shadow-inner"
          />
          <Search class="w-4 h-4 absolute left-3.5 top-3 text-slate-400 pointer-events-none" />
        </div>

        <!-- Subnovedad Selector -->
        <div class="flex items-center gap-2">
          <label class="text-xs uppercase font-bold text-slate-300">Subnovedad:</label>
          <select 
            v-model="tableSubnovedadFilter"
            class="bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option value="">Todas</option>
            <option v-for="s in subnovedadesList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <!-- Table Container -->
      <div class="glass-panel rounded-2xl border border-darkBorder overflow-hidden shadow-xl">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr class="border-b border-darkBorder text-xs text-slate-400 uppercase font-semibold bg-darkBg/60">
                <th class="py-3 px-4 font-mono">Fecha</th>
                <th class="py-3 px-4 text-center">Estado</th>
                <th class="py-3 px-4">Subnovedad</th>
                <th class="py-3 px-4">Descripción / Justificación</th>
                <th class="py-3 px-4">Desde</th>
                <th class="py-3 px-4">Hasta</th>
              </tr>
            </thead>
            <tbody class="text-xs">
              <tr 
                v-for="row in tablePaginatedHistory" 
                :key="row.fecha"
                class="border-b border-darkBorder/30 hover:bg-slate-800/30 transition-colors"
              >
                <!-- Date -->
                <td class="py-3 px-4 font-mono font-bold text-cyan-300">{{ row.fecha }}</td>
                
                <!-- Estado Badge -->
                <td class="py-3 px-4 text-center">
                  <span 
                    class="text-xs font-bold px-2.5 py-0.5 rounded-md border uppercase inline-block"
                    :class="isAvailable(row.subnovedad) ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400' : 'bg-amber-500/15 border-amber-500/30 text-amber-400'"
                  >
                    {{ isAvailable(row.subnovedad) ? 'DISP' : 'NOVEDAD' }}
                  </span>
                </td>
                
                <!-- Subnovedad -->
                <td class="py-3 px-4 font-bold text-slate-200 uppercase">{{ row.subnovedad }}</td>
                
                <!-- Descripción -->
                <td class="py-3 px-4 text-slate-300 uppercase max-w-xs truncate" :title="row.descripcion || undefined">
                  {{ row.descripcion || 'Sin justificación registrada' }}
                </td>
                
                <!-- Desde -->
                <td class="py-3 px-4 font-mono text-slate-400">{{ row.desde || '-' }}</td>
                
                <!-- Hasta -->
                <td class="py-3 px-4 font-mono text-slate-400">{{ row.hasta || '-' }}</td>
              </tr>
              
              <!-- Empty state -->
              <tr v-if="tableFilteredHistory.length === 0">
                <td colspan="6" class="text-center py-12 text-slate-400 font-medium">
                  No se encontraron registros para los filtros ingresados.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Table Pagination Controls -->
        <div v-if="tableFilteredHistory.length > 0" class="flex justify-between items-center text-xs p-3.5 bg-darkBg/60 border-t border-darkBorder/40">
          <span class="text-slate-400 font-medium">
            Mostrando <strong class="text-slate-200">{{ pagination.rangeStart }} - {{ pagination.rangeEnd }}</strong> de <strong class="text-slate-200">{{ pagination.totalCount }}</strong> registros
          </span>
          <div class="flex items-center gap-2">
            <button 
              type="button"
              @click="pagination.prevPage" 
              :disabled="!pagination.hasPrevPage.value"
              class="px-3 py-1.5 bg-darkCard border border-darkBorder rounded-xl text-slate-300 hover:text-white disabled:opacity-30 disabled:pointer-events-none cursor-pointer flex items-center gap-1 font-bold shadow-sm"
            >
              <ChevronLeft class="w-3.5 h-3.5" />
              <span>Anterior</span>
            </button>
            <span class="font-bold text-slate-200 px-1">Pág. {{ pagination.currentPage.value }} / {{ pagination.totalPages.value }}</span>
            <button 
              type="button"
              @click="pagination.nextPage" 
              :disabled="!pagination.hasNextPage.value"
              class="px-3 py-1.5 bg-darkCard border border-darkBorder rounded-xl text-slate-300 hover:text-white disabled:opacity-30 disabled:pointer-events-none cursor-pointer flex items-center gap-1 font-bold shadow-sm"
            >
              <span>Siguiente</span>
              <ChevronRight class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  Calendar, 
  Layers, 
  FileSpreadsheet, 
  Search, 
  Download, 
  ChevronLeft, 
  ChevronRight 
} from 'lucide-vue-next'

import type { PersonalDetalle, HistorialRegistro } from '../../types'
import { isAvailable } from '../../utils/personal.utils'
import { MONTH_TO_NUMBER } from '../../utils/date'
import { usePagination } from '../../composables/usePagination'

const props = defineProps<{
  profile: PersonalDetalle
  historial: HistorialRegistro[]
  activeMonths: string[]
  currentYear: string
  subnovedadesList: string[]
}>()

defineEmits<{
  (e: 'export-month', month: string): void
}>()

const activeHeatmapTab = ref<'mensual' | 'anual' | 'diario'>('mensual')
const selectedMonthlyHeatmapMonth = ref('JULIO')
const tableSearchQuery = ref('')
const tableSubnovedadFilter = ref('')

const isRetiredForDate = (monthName: string, dayNum: number) => {
  if (!props.profile || !props.profile.fecha_retiro) return false
  const mm = MONTH_TO_NUMBER[monthName]
  if (!mm) return false
  const dd = String(dayNum).padStart(2, '0')
  const targetDate = `${props.currentYear}-${mm}-${dd}`
  return targetDate >= props.profile.fecha_retiro
}

const getStatusForDate = (monthName: string, dayNum: number) => {
  if (isRetiredForDate(monthName, dayNum)) return 'RETIRADO'
  const mm = MONTH_TO_NUMBER[monthName]
  if (!mm) return 'N/A'
  const dd = String(dayNum).padStart(2, '0')
  const targetDate = `${props.currentYear}-${mm}-${dd}`
  const found = props.historial.find(h => h.fecha === targetDate)
  return found ? found.subnovedad : 'N/A'
}

const getIndividualHeatmapCellClass = (monthName: string, dayNum: number) => {
  const est = getStatusForDate(monthName, dayNum)
  if (est === 'RETIRADO') return 'bg-red-500/80 shadow shadow-red-500/10 text-red-100'
  if (est === 'N/A') return 'bg-darkBg border border-darkBorder/40 text-slate-600'
  return isAvailable(est) 
    ? 'bg-emerald-500/80 shadow shadow-emerald-500/10 text-emerald-100' 
    : 'bg-amber-500/80 shadow shadow-amber-500/10 text-amber-100'
}

const getIndividualHeatmapCellLetter = (monthName: string, dayNum: number) => {
  const est = getStatusForDate(monthName, dayNum)
  if (est === 'RETIRADO') return 'R'
  if (est === 'N/A') return '-'
  return isAvailable(est) ? 'D' : 'N'
}

const tableFilteredHistory = computed(() => {
  return props.historial.filter(h => {
    const matchSearch = !tableSearchQuery.value || 
      (h.descripcion && h.descripcion.toLowerCase().includes(tableSearchQuery.value.toLowerCase())) ||
      (h.subnovedad && h.subnovedad.toLowerCase().includes(tableSearchQuery.value.toLowerCase()))
      
    const matchSubnovedad = !tableSubnovedadFilter.value || h.subnovedad === tableSubnovedadFilter.value
    
    return matchSearch && matchSubnovedad
  })
})

const pagination = usePagination(tableFilteredHistory, 10)
const tablePaginatedHistory = pagination.paginatedItems

watch([tableSearchQuery, tableSubnovedadFilter], () => {
  pagination.resetPage()
})

watch(() => props.activeMonths, (newMonths) => {
  if (newMonths && newMonths.length > 0) {
    if (!newMonths.includes(selectedMonthlyHeatmapMonth.value)) {
      selectedMonthlyHeatmapMonth.value = newMonths[newMonths.length - 1]
    }
  }
}, { immediate: true })
</script>
