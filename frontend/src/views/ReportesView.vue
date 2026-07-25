<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-darkBorder/40">
      <div>
        <h2 class="text-xl font-black text-slate-100 uppercase tracking-tight flex items-center gap-3">
          <span class="w-2.5 h-6 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-sm"></span>
          Centro de Descargas y Reportes
        </h2>
        <p class="text-xs text-slate-500 mt-1">Exporta la información operacional de la unidad en formatos estandarizados Excel, CSV y PDF de alta calidad.</p>
      </div>
      <div class="flex items-center gap-2 text-xs bg-darkBg/60 px-4 py-2 rounded-xl border border-darkBorder/40">
        <span class="text-slate-400">Base de Datos:</span>
        <span class="font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/10">PostgreSQL</span>
      </div>
    </div>

    <!-- Reports Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- Card 1: Base de Datos de Personal -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group">
        <div class="space-y-3">
          <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform duration-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Base de Datos de Personal</h3>
            <p class="text-xs text-slate-500 mt-1">Listado general de todo el personal registrado en la unidad, incluyendo su cédula, nombres completos, estado actual (activo/retirado) y fecha de retiro si aplica.</p>
          </div>
        </div>
        
        <div class="grid grid-cols-3 gap-2 mt-6">
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=personal_db`"
            download
            class="flex items-center justify-center text-center px-3 py-2 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL (.xlsx)
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=personal_db`"
            download
            class="flex items-center justify-center text-center px-3 py-2 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV (.csv)
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=personal_db`"
            download
            class="flex items-center justify-center text-center px-3 py-2 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF (.pdf)
          </a>
        </div>
      </div>

      <!-- Card 2: Catálogo de Subnovedades -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group">
        <div class="space-y-3">
          <div class="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 group-hover:scale-105 transition-transform duration-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Catálogo de Novedades</h3>
            <p class="text-xs text-slate-500 mt-1">Exporta el diccionario general de novedades y clasificaciones configuradas en el sistema, ideal para auditorías de nomenclaturas operacionales.</p>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-2 mt-6">
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=subnovedades`"
            download
            class="flex items-center justify-center text-center px-3 py-2 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL (.xlsx)
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=subnovedades`"
            download
            class="flex items-center justify-center text-center px-3 py-2 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV (.csv)
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=subnovedades`"
            download
            class="flex items-center justify-center text-center px-3 py-2 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF (.pdf)
          </a>
        </div>
      </div>

      <!-- Card 3: Consolidado Diario Mensual (Heatmap) -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group md:col-span-2">
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div class="space-y-3 flex-1">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Consolidado Diario Mensual (HEATMAP)</h3>
              <p class="text-xs text-slate-500 mt-1 leading-relaxed">
                Genera la matriz de novedades del personal. Puedes elegir entre ver letras estáticas (D=Disponible, N=Novedad, R=Retirado) o el detalle completo de novedad por celda para cualquier período exportado.
              </p>
            </div>
          </div>
          
          <!-- Heatmap Filter Controls -->
          <div class="flex flex-col gap-2.5 w-full md:w-64">
            <!-- Mode Selector -->
            <div class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Modo de Celdas:</label>
              <select 
                v-model="heatmapModo"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option value="letras">LETRAS DEFINIDAS (D, N, R)</option>
                <option value="detalle">DETALLE DE NOVEDAD</option>
              </select>
            </div>

            <!-- Scope Selector -->
            <div class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Período a exportar:</label>
              <select 
                v-model="heatmapScope"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option value="ANUAL">TODOS LOS MESES (ANUAL)</option>
                <option value="MES">MES ESPECÍFICO</option>
                <option value="DIA">DÍA ESPECÍFICO</option>
              </select>
            </div>

            <!-- Month Dropdown (visible for MES or DIA) -->
            <div v-if="heatmapScope === 'MES' || heatmapScope === 'DIA'" class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seleccionar Mes:</label>
              <select 
                v-model="heatmapSelectedMonth"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Date Dropdown (filtered by selected month) -->
            <div v-if="heatmapScope === 'DIA'" class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seleccionar Día (de {{ heatmapSelectedMonth }}):</label>
              <select 
                v-model="heatmapSelectedDate"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="d in heatmapFilteredDates" :key="d" :value="d">{{ formatDate(d) }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-8">
          <a 
            :href="heatmapExcelUrl"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL Heatmap ({{ heatmapLabel }})
          </a>
          <a 
            :href="heatmapCsvUrl"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV Heatmap ({{ heatmapLabel }})
          </a>
          <a 
            :href="heatmapPdfUrl"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF Heatmap ({{ heatmapLabel }})
          </a>
        </div>
      </div>

      <!-- Card 4: Reporte Detallado de Personal -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group md:col-span-2">
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div class="space-y-3 flex-1">
            <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Reporte Detallado de Personal</h3>
              <p class="text-xs text-slate-500 mt-1">Exporta el reporte detallado con cédula, nombres, subnovedad, descripción y fechas exactas. Puedes filtrar por todos los meses (anual), un mes en específico o un día específico.</p>
            </div>
          </div>
          
          <!-- Detailed Filter Controls -->
          <div class="flex flex-col gap-2.5 w-full md:w-64">
            <div class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Período a exportar:</label>
              <select 
                v-model="detalladoScope"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option value="ANUAL">TODOS LOS MESES (ANUAL)</option>
                <option value="MES">MES ESPECÍFICO</option>
                <option value="DIA">DÍA ESPECÍFICO</option>
              </select>
            </div>

            <!-- Month Dropdown (visible for MES or DIA) -->
            <div v-if="detalladoScope === 'MES' || detalladoScope === 'DIA'" class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seleccionar Mes:</label>
              <select 
                v-model="detalladoSelectedMonth"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Date Dropdown (filtered by selected month) -->
            <div v-if="detalladoScope === 'DIA'" class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seleccionar Día (de {{ detalladoSelectedMonth }}):</label>
              <select 
                v-model="detalladoSelectedDate"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="d in detalladoFilteredDates" :key="d" :value="d">{{ formatDate(d) }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-8">
          <a 
            :href="detalladoExcelUrl"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL Detallado ({{ detalladoLabel }})
          </a>
          <a 
            :href="detalladoCsvUrl"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV Detallado ({{ detalladoLabel }})
          </a>
          <a 
            :href="detalladoPdfUrl"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF Detallado ({{ detalladoLabel }})
          </a>
        </div>
      </div>

      <!-- Card 5: Exportación Ágil de Novedades -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between border-cyan-500/30 bg-gradient-to-br from-cyan-950/20 via-darkPanel to-blue-950/20 hover:border-cyan-400/50 transition-all duration-300 group md:col-span-2 shadow-lg shadow-cyan-950/30">
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div class="space-y-3 flex-1">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform duration-200 shadow-sm">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 animate-pulse">
                NUEVO / EXCLUSIVO NOVEDADES
              </span>
            </div>
            <div>
              <h3 class="text-sm font-black text-slate-100 uppercase tracking-wide flex items-center gap-2">
                Exportación Ágil de Novedades
              </h3>
              <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                Reporte exclusivo de novedades (excluye días disponibles). Consolida y simplifica los rangos continuos de fechas (ejemplo: <span class="text-cyan-300 font-bold font-mono">ENERO: 10-15 (VACACIONES)</span>) para agilizar la lectura por día, mes o año.
              </p>
            </div>
          </div>
          
          <!-- Mode & Scope Selector -->
          <div class="flex flex-col gap-2 w-full md:w-64">
            <div class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Período Ágil:</label>
              <select 
                v-model="agilMode"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option value="ANUAL">TODOS LOS MESES (ANUAL)</option>
                <option value="MES">MES ESPECÍFICO</option>
                <option value="DIA">DÍA ESPECÍFICO</option>
              </select>
            </div>

            <!-- Month Dropdown (visible for MES or DIA) -->
            <div v-if="agilMode === 'MES' || agilMode === 'DIA'" class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seleccionar Mes:</label>
              <select 
                v-model="agilSelectedMonth"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Date Dropdown (filtered by selected month) -->
            <div v-if="agilMode === 'DIA'" class="flex flex-col gap-1">
              <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Seleccionar Día (de {{ agilSelectedMonth }}):</label>
              <select 
                v-model="agilSelectedDate"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="d in agilFilteredDates" :key="d" :value="d">{{ formatDate(d) }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-6 pt-4 border-t border-darkBorder/40">
          <a 
            :href="agilExcelUrl"
            download
            class="flex items-center justify-center gap-2 text-center px-4 py-2.5 rounded-xl text-[11px] font-black uppercase transition-all duration-200 border cursor-pointer select-none shadow-md bg-emerald-500/20 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/30 hover:border-emerald-500/60"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            EXCEL ÁGIL ({{ agilLabel }})
          </a>
          <a 
            :href="agilPdfUrl"
            download
            class="flex items-center justify-center gap-2 text-center px-4 py-2.5 rounded-xl text-[11px] font-black uppercase transition-all duration-200 border cursor-pointer select-none shadow-md bg-cyan-500/20 border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 hover:border-cyan-500/60"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            PDF ÁGIL ({{ agilLabel }})
          </a>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useAppStore } from '../stores/appStore'

const appStore = useAppStore()

const activeMonths = computed(() => appStore.availableMonths)

// Heatmap state
const heatmapModo = ref<'letras' | 'detalle'>('letras')
const heatmapScope = ref<'ANUAL' | 'MES' | 'DIA'>('ANUAL')
const heatmapSelectedMonth = ref(appStore.selectedMonth || 'JULIO')
const heatmapSelectedDate = ref('')

// Reporte Detallado state
const detalladoScope = ref<'ANUAL' | 'MES' | 'DIA'>('ANUAL')
const detalladoSelectedMonth = ref(appStore.selectedMonth || 'JULIO')
const detalladoSelectedDate = ref('')

// Exportación Ágil state
const agilMode = ref<'ANUAL' | 'MES' | 'DIA'>('ANUAL')
const agilSelectedMonth = ref(appStore.selectedMonth || 'JULIO')
const agilSelectedDate = ref('')

const monthToNumber: Record<string, string> = {
  'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04',
  'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08',
  'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
}

onMounted(() => {
  if (appStore.availableDates.length === 0) {
    appStore.fetchAvailableDates()
  }
})

const sortedDates = computed(() => {
  return [...appStore.availableDates].sort((a, b) => b.localeCompare(a))
})

// Filtered dates per card based on chosen month
const heatmapFilteredDates = computed(() => {
  const monthNum = monthToNumber[heatmapSelectedMonth.value]
  if (!monthNum) return sortedDates.value
  const filtered = sortedDates.value.filter(d => d.split('-')[1] === monthNum)
  return filtered.length > 0 ? filtered : sortedDates.value
})

const detalladoFilteredDates = computed(() => {
  const monthNum = monthToNumber[detalladoSelectedMonth.value]
  if (!monthNum) return sortedDates.value
  const filtered = sortedDates.value.filter(d => d.split('-')[1] === monthNum)
  return filtered.length > 0 ? filtered : sortedDates.value
})

const agilFilteredDates = computed(() => {
  const monthNum = monthToNumber[agilSelectedMonth.value]
  if (!monthNum) return sortedDates.value
  const filtered = sortedDates.value.filter(d => d.split('-')[1] === monthNum)
  return filtered.length > 0 ? filtered : sortedDates.value
})

watch(heatmapFilteredDates, (newDates) => {
  if (newDates.length > 0) heatmapSelectedDate.value = newDates[0]
}, { immediate: true })

watch(detalladoFilteredDates, (newDates) => {
  if (newDates.length > 0) detalladoSelectedDate.value = newDates[0]
}, { immediate: true })

watch(agilFilteredDates, (newDates) => {
  if (newDates.length > 0) agilSelectedDate.value = newDates[0]
}, { immediate: true })

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length !== 3) return dateStr
  return `${parts[2]}/${parts[1]}/${parts[0]}`
}

// Heatmap computed URLs
const heatmapLabel = computed(() => {
  if (heatmapScope.value === 'ANUAL') return 'ANUAL'
  if (heatmapScope.value === 'MES') return heatmapSelectedMonth.value
  return formatDate(heatmapSelectedDate.value)
})

const heatmapExcelUrl = computed(() => {
  let url = `${appStore.apiBase.value}/api/exportar/excel?tipo=consolidado_mensual&modo=${heatmapModo.value}`
  if (heatmapScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (heatmapScope.value === 'MES') url += `&mes=${heatmapSelectedMonth.value}`
  else url += `&fecha=${heatmapSelectedDate.value}`
  return url
})

const heatmapCsvUrl = computed(() => {
  let url = `${appStore.apiBase.value}/api/exportar/csv?tipo=consolidado_mensual&modo=${heatmapModo.value}`
  if (heatmapScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (heatmapScope.value === 'MES') url += `&mes=${heatmapSelectedMonth.value}`
  else url += `&fecha=${heatmapSelectedDate.value}`
  return url
})

const heatmapPdfUrl = computed(() => {
  let url = `${appStore.apiBase.value}/api/exportar/pdf?tipo=consolidado_mensual&modo=${heatmapModo.value}`
  if (heatmapScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (heatmapScope.value === 'MES') url += `&mes=${heatmapSelectedMonth.value}`
  else url += `&fecha=${heatmapSelectedDate.value}`
  return url
})

// Detallado computed URLs
const detalladoLabel = computed(() => {
  if (detalladoScope.value === 'ANUAL') return 'ANUAL'
  if (detalladoScope.value === 'MES') return detalladoSelectedMonth.value
  return formatDate(detalladoSelectedDate.value)
})

const detalladoExcelUrl = computed(() => {
  let url = `${appStore.apiBase.value}/api/exportar/excel?tipo=dia`
  if (detalladoScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (detalladoScope.value === 'MES') url += `&mes=${detalladoSelectedMonth.value}`
  else url += `&fecha=${detalladoSelectedDate.value}`
  return url
})

const detalladoCsvUrl = computed(() => {
  let url = `${appStore.apiBase.value}/api/exportar/csv?tipo=dia`
  if (detalladoScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (detalladoScope.value === 'MES') url += `&mes=${detalladoSelectedMonth.value}`
  else url += `&fecha=${detalladoSelectedDate.value}`
  return url
})

const detalladoPdfUrl = computed(() => {
  let url = `${appStore.apiBase.value}/api/exportar/pdf?tipo=dia`
  if (detalladoScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (detalladoScope.value === 'MES') url += `&mes=${detalladoSelectedMonth.value}`
  else url += `&fecha=${detalladoSelectedDate.value}`
  return url
})

// Ágil computed URLs
const agilLabel = computed(() => {
  if (agilMode.value === 'ANUAL') return 'ANUAL COMPLETO'
  if (agilMode.value === 'MES') return agilSelectedMonth.value
  return formatDate(agilSelectedDate.value)
})

const agilExcelUrl = computed(() => {
  if (agilMode.value === 'ANUAL') return `${appStore.apiBase.value}/api/exportar/excel?tipo=agil&mes=TODOS`
  if (agilMode.value === 'MES') return `${appStore.apiBase.value}/api/exportar/excel?tipo=agil&mes=${agilSelectedMonth.value}`
  return `${appStore.apiBase.value}/api/exportar/excel?tipo=agil&fecha=${agilSelectedDate.value}`
})

const agilPdfUrl = computed(() => {
  if (agilMode.value === 'ANUAL') return `${appStore.apiBase.value}/api/exportar/pdf?tipo=agil&mes=TODOS`
  if (agilMode.value === 'MES') return `${appStore.apiBase.value}/api/exportar/pdf?tipo=agil&mes=${agilSelectedMonth.value}`
  return `${appStore.apiBase.value}/api/exportar/pdf?tipo=agil&fecha=${agilSelectedDate.value}`
})
</script>

