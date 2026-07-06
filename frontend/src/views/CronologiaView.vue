<template>
  <div class="space-y-6">
    <!-- Row 1: GitHub Activity Calendar and Heatmap toggle -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- GitHub style Activity Calendar -->
      <div class="glass-panel p-6 rounded-2xl lg:col-span-2 flex flex-col justify-between min-h-[220px]">
        <div>
          <h3 class="text-sm font-bold text-slate-200 mb-2 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Calendario de Disponibilidad ({{ appStore.selectedMonth }})
          </h3>
          <p class="text-xs text-slate-500 mb-4">Muestra la disponibilidad operacional diaria. Haz clic en un día para ver su reporte detallado abajo.</p>
        </div>

        <!-- Calendar Grid -->
        <div v-if="loadingCalendar" class="flex justify-center items-center py-6">
          <div class="w-6 h-6 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
        </div>
        <div v-else class="flex flex-wrap gap-2.5 py-2">
          <button 
            v-for="day in calendarData" 
            :key="day.fecha"
            @click="selectDate(day.fecha)"
            class="w-12 h-12 rounded-xl flex flex-col items-center justify-center border transition-all duration-150 relative group"
            :class="[
              getDayColorClass(day.disponibilidad),
              day.fecha === activeDate ? 'ring-2 ring-cyan-400 scale-105 border-slate-100 z-10' : ''
            ]"
          >
            <span class="text-xs font-bold font-mono">{{ getDayNum(day.fecha) }}</span>
            <span class="text-[8px] font-mono opacity-80">{{ Math.round(day.disponibilidad) }}%</span>

            <!-- Tooltip -->
            <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-36 bg-darkCard border border-darkBorder text-slate-200 text-[10px] p-2 rounded-lg shadow-xl opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-20 text-center font-sans">
              <p class="font-bold text-slate-300">{{ day.fecha }}</p>
              <p class="text-cyan-400 font-semibold mt-0.5">Disponibilidad: {{ day.disponibilidad }}%</p>
              <p class="text-slate-500 text-[9px] mt-0.5">{{ day.disponibles }} / {{ day.total_personal }} Disponibles</p>
            </div>
          </button>
        </div>

        <!-- Legend -->
        <div class="flex items-center gap-4 text-[10px] text-slate-400 border-t border-darkBorder/40 pt-3 mt-3">
          <span class="font-semibold uppercase tracking-wider">Leyenda:</span>
          <div class="flex items-center gap-1.5">
            <span class="w-3 h-3 bg-emerald-500/10 border border-emerald-500/30 rounded-md"></span> >= 80% (Alta)
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-3 h-3 bg-amber-500/10 border border-amber-500/30 rounded-md"></span> 60% - 80% (Media)
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-3 h-3 bg-red-500/10 border border-red-500/30 rounded-md"></span> < 60% (Baja)
          </div>
        </div>
      </div>

      <!-- Quick Metrics for the selected month -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between min-h-[220px]">
        <div>
          <h3 class="text-sm font-bold text-slate-200 mb-2 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-teal-500 rounded-sm"></span> Métricas del Mes
          </h3>
          <p class="text-xs text-slate-500">Resumen acumulado del mes seleccionado.</p>
        </div>

        <div v-if="!loadingCalendar" class="space-y-3 py-2">
          <div class="flex justify-between items-center text-xs">
            <span class="text-slate-400">Promedio Disponibilidad:</span>
            <span class="font-bold text-slate-200 font-mono">{{ avgMonthlyDispo }}%</span>
          </div>
          <div class="flex justify-between items-center text-xs">
            <span class="text-slate-400">Día con Mayor Disponibilidad:</span>
            <span class="font-bold text-emerald-400 font-mono">{{ maxDispoDay }}</span>
          </div>
          <div class="flex justify-between items-center text-xs">
            <span class="text-slate-400">Día con Menor Disponibilidad:</span>
            <span class="font-bold text-red-400 font-mono">{{ minDispoDay }}</span>
          </div>
        </div>
        <div v-else class="flex justify-center items-center py-6">
          <div class="w-6 h-6 border-2 border-teal-500/20 border-t-teal-500 rounded-full animate-spin"></div>
        </div>
      </div>
    </div>

    <!-- Toggle views: Detailed Daily Report OR Heatmap Matrix -->
    <div class="flex border-b border-darkBorder">
      <button 
        @click="activeSubView = 'reporte'"
        class="px-5 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
        :class="activeSubView === 'reporte' ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        📄 Reporte Detallado del Día: {{ activeDate }}
      </button>
      <button 
        @click="activeSubView = 'heatmap'"
        class="px-5 py-3 text-xs font-bold uppercase tracking-wider transition-colors border-b-2"
        :class="activeSubView === 'heatmap' ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        🏁 Matriz de Heatmap Mensual
      </button>
    </div>

    <!-- VIEW 1: DETAILED DAILY REPORT -->
    <div v-if="activeSubView === 'reporte'" class="glass-panel p-6 rounded-2xl flex flex-col space-y-4">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h4 class="text-sm font-bold text-slate-200 uppercase tracking-tight">Reporte diario oficial del personal</h4>
          <p class="text-xs text-slate-500 font-mono">Fecha: {{ activeDate }} | Total de registros: {{ dailyReport.length }}</p>
        </div>

        <!-- Export -->
        <div v-if="dailyReport.length > 0" class="flex items-center gap-3">
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=dia&fecha=${activeDate}`"
            download
            class="px-3 py-1.5 bg-darkBg border border-darkBorder rounded-lg text-xs font-semibold text-slate-300 hover:border-slate-600 transition-all"
          >
            Exportar CSV
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=dia&fecha=${activeDate}`"
            download
            class="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-lg text-xs font-semibold hover:border-emerald-500/40 transition-all"
          >
            Exportar Excel
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=dia&fecha=${activeDate}`"
            download
            class="px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-lg text-xs font-semibold hover:border-cyan-500/40 transition-all"
          >
            Exportar PDF
          </a>
        </div>
      </div>

      <!-- Search in daily report -->
      <div class="relative">
        <input 
          type="text" 
          v-model="dailySearch"
          placeholder="Filtrar reporte por nombre, cédula o subnovedad..."
          class="w-full bg-darkBg border border-darkBorder rounded-xl pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/50"
        />
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3.5 top-3 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      <!-- Detailed table -->
      <div class="overflow-x-auto">
        <div v-if="loadingDaily" class="flex justify-center items-center py-20">
          <div class="w-8 h-8 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
        </div>
        <div v-else-if="filteredDailyReport.length > 0">
          <table class="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr class="border-b border-darkBorder text-[10px] text-slate-400 uppercase font-mono bg-darkBg/50">
                <th class="py-2.5 px-3">Cédula</th>
                <th class="py-2.5 px-3">Apellidos y Nombres</th>
                <th class="py-2.5 px-3">Subnovedad</th>
                <th class="py-2.5 px-3">Descripción</th>
                <th class="py-2.5 px-3">Desde</th>
                <th class="py-2.5 px-3">Hasta</th>
              </tr>
            </thead>
            <tbody class="text-xs">
              <tr 
                v-for="r in filteredDailyReport" 
                :key="r.cedula"
                class="border-b border-darkBorder/40 hover:bg-darkBorder/10 transition-colors"
              >
                <td class="py-2.5 px-3 font-mono text-slate-400">{{ r.cedula }}</td>
                <td class="py-2.5 px-3 font-bold text-slate-200 hover:text-cyan-400 uppercase">
                  <router-link :to="`/personal/${r.cedula}`">{{ r.nombre }}</router-link>
                </td>
                <td class="py-2.5 px-3">
                  <span 
                    class="text-[9px] font-bold px-2 py-0.5 rounded border uppercase"
                    :class="isAvailable(r.subnovedad) ? 'bg-emerald-500/10 border-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 border-amber-500/10 text-amber-500'"
                  >
                    {{ r.subnovedad }}
                  </span>
                </td>
                <td class="py-2.5 px-3 text-slate-300 max-w-[200px] truncate uppercase" :title="r.descripcion">
                  {{ r.descripcion }}
                </td>
                <td class="py-2.5 px-3 font-mono text-slate-500">{{ r.desde || '-' }}</td>
                <td class="py-2.5 px-3 font-mono text-slate-500">{{ r.hasta || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-20 text-slate-500">
          No se encontraron registros que coincidan con la búsqueda.
        </div>
      </div>
    </div>

    <!-- VIEW 2: HEATMAP MATRIX -->
    <div v-if="activeSubView === 'heatmap'" class="glass-panel p-6 rounded-2xl flex flex-col space-y-4">
      <div>
        <h4 class="text-sm font-bold text-slate-200 uppercase tracking-tight">Matriz Heatmap: Personal vs Días</h4>
        <p class="text-xs text-slate-500">Muestra la disponibilidad individual diaria de toda la unidad. Filas: Integrantes, Columnas: Días del Mes.</p>
      </div>

      <!-- Search and Legend inside Heatmap -->
      <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
        <div class="relative w-full md:w-80">
          <input 
            type="text" 
            v-model="heatmapSearch"
            placeholder="Buscar integrante por nombre o cédula..."
            class="w-full bg-darkBg border border-darkBorder rounded-xl pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/50"
          />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 absolute left-3.5 top-3 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <div class="flex items-center gap-4 text-[9px] text-slate-400">
          <div class="flex items-center gap-1">
            <span class="w-2.5 h-2.5 bg-emerald-500 rounded"></span> Disponible
          </div>
          <div class="flex items-center gap-1">
            <span class="w-2.5 h-2.5 bg-amber-500 rounded"></span> Novedad
          </div>
          <div class="flex items-center gap-1">
            <span class="w-2.5 h-2.5 bg-darkBg border border-darkBorder rounded"></span> N/A (Retirado/Sin registro)
          </div>
        </div>
      </div>

      <!-- Matrix container -->
      <div class="overflow-x-auto border border-darkBorder rounded-xl">
        <div v-if="loadingHeatmap" class="flex justify-center items-center py-20">
          <div class="w-8 h-8 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
        </div>
        <div v-else-if="paginatedHeatmap.length > 0" class="min-w-[900px] bg-darkBg/20">
          <table class="w-full text-left border-collapse table-fixed">
            <thead>
              <tr class="border-b border-darkBorder text-[9px] text-slate-400 font-mono bg-darkBg/60">
                <th class="py-2 px-3 w-48 text-left">Integrante</th>
                <!-- Day Columns -->
                <th 
                  v-for="d in heatmapData.fechas" 
                  :key="d"
                  class="py-2 text-center w-8"
                  :title="d"
                >
                  {{ getDayNum(d) }}
                </th>
              </tr>
            </thead>
            <tbody class="text-[10px]">
              <tr 
                v-for="p in paginatedHeatmap" 
                :key="p.cedula"
                class="border-b border-darkBorder/25 hover:bg-darkBorder/5 transition-colors"
              >
                <!-- Name and CC -->
                <td class="py-2 px-3 truncate font-semibold text-slate-300 uppercase" :title="p.nombre">
                  <router-link :to="`/personal/${p.cedula}`" class="hover:text-cyan-400">
                    {{ p.nombre }}
                  </router-link>
                  <span class="text-[8px] text-slate-500 block font-mono">CC {{ p.cedula }}</span>
                </td>
                <!-- Attendance boxes -->
                <td 
                  v-for="(est, i) in p.estados" 
                  :key="i"
                  class="py-2 text-center w-8"
                  :title="`${p.nombre} - ${heatmapData.fechas[i]}: ${est}`"
                >
                  <div 
                    class="w-5.5 h-5.5 mx-auto rounded transition-colors"
                    :class="getHeatmapCellClass(est)"
                  ></div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-20 text-slate-500">
          No se encontraron registros.
        </div>
      </div>

      <!-- Pagination controls -->
      <div v-if="!loadingHeatmap && filteredHeatmap.length > 0" class="flex justify-between items-center text-xs pt-2">
        <span class="text-slate-500 font-mono">
          Mostrando {{ (heatmapPage - 1) * heatmapLimit + 1 }} - {{ Math.min(heatmapPage * heatmapLimit, filteredHeatmap.length) }} de {{ filteredHeatmap.length }} integrantes
        </span>
        <div class="flex items-center gap-2">
          <button 
            @click="heatmapPage--" 
            :disabled="heatmapPage <= 1"
            class="px-3 py-1.5 bg-darkCard border border-darkBorder rounded-lg text-slate-400 hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none"
          >
            Anterior
          </button>
          <span class="font-bold text-slate-200">Pág. {{ heatmapPage }} / {{ maxHeatmapPage }}</span>
          <button 
            @click="heatmapPage++" 
            :disabled="heatmapPage >= maxHeatmapPage"
            class="px-3 py-1.5 bg-darkCard border border-darkBorder rounded-lg text-slate-400 hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const appStore = useAppStore()

interface CalendarEntry {
  fecha: string
  disponibilidad: number
  total_personal: number
  disponibles: number
  novedades: number
}

interface DailyRecord {
  cedula: number
  nombre: string
  subnovedad: string
  descripcion: string
  desde: string | null
  hasta: string | null
}

interface HeatmapRow {
  cedula: number
  nombre: string
  estados: string[]
}

interface HeatmapData {
  fechas: string[]
  data: HeatmapRow[]
}

// Views controls
const activeSubView = ref<'reporte' | 'heatmap'>('reporte')
const activeDate = ref('2026-07-05')

// Search/Filter states
const dailySearch = ref('')
const heatmapSearch = ref('')

// Loadings
const loadingCalendar = ref(true)
const loadingDaily = ref(true)
const loadingHeatmap = ref(true)

// Data containers
const calendarData = ref<CalendarEntry[]>([])
const dailyReport = ref<DailyRecord[]>([])
const heatmapData = ref<HeatmapData>({ fechas: [], data: [] })

// Heatmap Pagination
const heatmapPage = ref(1)
const heatmapLimit = 25

const DISPONIBLE_STATUSES = ["CDO UNIDAD", "AREA OPERACIONES"]
const isAvailable = (subnovedad: string) => {
  return DISPONIBLE_STATUSES.includes(subnovedad)
}

// Calendar color class based on percent
const getDayColorClass = (pct: number) => {
  if (pct >= 80) return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20'
  if (pct >= 60) return 'bg-amber-500/10 border-amber-500/30 text-amber-500 hover:bg-amber-500/20'
  return 'bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20'
}

const getHeatmapCellClass = (est: string) => {
  if (est === 'N/A') return 'bg-darkBg border border-darkBorder/40'
  return isAvailable(est) ? 'bg-emerald-500/80 shadow shadow-emerald-500/10' : 'bg-amber-500/80 shadow shadow-amber-500/10'
}

const getDayNum = (date_str: string) => {
  try {
    return date_str.split('-')[2]
  } catch {
    return date_str
  }
}

// Fetch Activity Calendar
const loadCalendar = async () => {
  loadingCalendar.value = true
  try {
    const res = await fetch(`${appStore.apiBase}/api/reportes/calendario?mes=${appStore.selectedMonth}`)
    if (res.ok) {
      calendarData.value = await res.json()
      // If dates exist, select the first date of the calendar by default
      if (calendarData.value.length > 0) {
        // Only override activeDate if it's not present in this month's calendar
        const datesList = calendarData.value.map(c => c.fecha)
        if (!datesList.includes(activeDate.value)) {
          activeDate.value = datesList[0]
        }
      }
    }
    loadingCalendar.value = false
  } catch (e) {
    console.error('Error fetching calendar:', e)
    loadingCalendar.value = false
  }
}

// Fetch Daily Report
const loadDailyReport = async () => {
  loadingDaily.value = true
  try {
    const res = await fetch(`${appStore.apiBase}/api/reportes/dia?fecha=${activeDate.value}`)
    if (res.ok) {
      dailyReport.value = await res.json()
    }
    loadingDaily.value = false
  } catch (e) {
    console.error('Error loading daily report:', e)
    loadingDaily.value = false
  }
}

// Fetch Heatmap Data
const loadHeatmapData = async () => {
  loadingHeatmap.value = true
  try {
    const res = await fetch(`${appStore.apiBase}/api/stats/heatmap?mes=${appStore.selectedMonth}`)
    if (res.ok) {
      heatmapData.value = await res.json()
      heatmapPage.value = 1
    }
    loadingHeatmap.value = false
  } catch (e) {
    console.error('Error loading heatmap:', e)
    loadingHeatmap.value = false
  }
}

// Select Date Handler
const selectDate = (date: string) => {
  activeDate.value = date
}

// Monthly calculations
const avgMonthlyDispo = computed(() => {
  if (!calendarData.value.length) return 0
  const sum = calendarData.value.reduce((acc, c) => acc + c.disponibilidad, 0)
  return Math.round(sum / calendarData.value.length)
})

const maxDispoDay = computed(() => {
  if (!calendarData.value.length) return 'N/A'
  const sorted = [...calendarData.value].sort((a, b) => b.disponibilidad - a.disponibilidad)
  return `${sorted[0].fecha} (${Math.round(sorted[0].disponibilidad)}%)`
})

const minDispoDay = computed(() => {
  if (!calendarData.value.length) return 'N/A'
  const sorted = [...calendarData.value].sort((a, b) => a.disponibilidad - b.disponibilidad)
  return `${sorted[0].fecha} (${Math.round(sorted[0].disponibilidad)}%)`
})

// Search filtration
const filteredDailyReport = computed(() => {
  if (!dailySearch.value.trim()) return dailyReport.value
  const query = dailySearch.value.toLowerCase()
  return dailyReport.value.filter(r => 
    r.nombre.toLowerCase().includes(query) ||
    String(r.cedula).includes(query) ||
    r.subnovedad.toLowerCase().includes(query)
  )
})

const filteredHeatmap = computed(() => {
  if (!heatmapSearch.value.trim()) return heatmapData.value.data
  const query = heatmapSearch.value.toLowerCase()
  return heatmapData.value.data.filter(row => 
    row.nombre.toLowerCase().includes(query) ||
    String(row.cedula).includes(query)
  )
})

// Heatmap Pagination calculations
const maxHeatmapPage = computed(() => {
  return Math.max(1, Math.ceil(filteredHeatmap.value.length / heatmapLimit))
})

const paginatedHeatmap = computed(() => {
  const start = (heatmapPage.value - 1) * heatmapLimit
  const end = start + heatmapLimit
  return filteredHeatmap.value.slice(start, end)
})

// Watchers
watch(() => appStore.selectedMonth, () => {
  loadCalendar()
  loadHeatmapData()
})

watch(activeDate, () => {
  loadDailyReport()
})

onMounted(() => {
  // Sync selectDate with global store date if applicable
  if (appStore.selectedDate) {
    activeDate.value = appStore.selectedDate
  }
  loadCalendar()
  loadDailyReport()
  loadHeatmapData()
})
</script>
