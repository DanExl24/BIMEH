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

      <!-- Card 3: Consolidado Mensual Operacional -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group md:col-span-2">
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div class="space-y-3 flex-1">
            <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Consolidado Diario Mensual (Heatmap)</h3>
              <p class="text-xs text-slate-500 mt-1">Genera una grilla completa del mes seleccionado con el estado diario de cada integrante de la unidad (D = Disponible, N = Novedad, - = N/A). El formato Excel se genera coloreado imitando el Heatmap.</p>
            </div>
          </div>
          
          <!-- Month Selector -->
          <div class="flex flex-col gap-1.5 w-full md:w-56">
            <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Mes a exportar:</label>
            <select 
              v-model="selectedMonth"
              class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
            >
              <option value="TODOS">TODOS LOS MESES</option>
              <option v-for="m in meses" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-8">
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=consolidado_mensual&mes=${selectedMonth}`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL Consolidado ({{ selectedMonth }})
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=consolidado_mensual&mes=${selectedMonth}`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV Consolidado ({{ selectedMonth }})
          </a>
          <a 
            v-if="selectedMonth !== 'TODOS'"
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=consolidado_mensual&mes=${selectedMonth}`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF Consolidado ({{ selectedMonth }})
          </a>
          <button
            v-else
            disabled
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase border bg-slate-800/50 border-darkBorder text-slate-500 cursor-not-allowed select-none"
            title="El formato PDF no admite consolidar todos los meses por espacio horizontal"
          >
            PDF NO DISPONIBLE (TODOS)
          </button>
        </div>
      </div>

      <!-- Card 4: Reporte Diario de Personal (Por Fecha) -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group md:col-span-2">
        <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div class="space-y-3 flex-1">
            <div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform duration-200">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Reporte Diario de Personal</h3>
              <p class="text-xs text-slate-500 mt-1">Exporta el listado completo de novedades, disponibilidad y justificaciones del personal asignado para un día específico registrado en el sistema.</p>
            </div>
          </div>
          
          <!-- Date Selector -->
          <div class="flex flex-col gap-1.5 w-full md:w-56">
            <label class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Fecha a exportar:</label>
            <select 
              v-model="selectedDate"
              class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
            >
              <option v-for="d in sortedDates" :key="d" :value="d">{{ formatDate(d) }}</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-8">
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=dia&fecha=${selectedDate}`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL Reporte Diario
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=dia&fecha=${selectedDate}`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV Reporte Diario
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=dia&fecha=${selectedDate}`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF Reporte Diario
          </a>
        </div>
      </div>

      <!-- Card 5: Historial Completo de Novedades -->
      <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300 group md:col-span-2">
        <div class="space-y-3">
          <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 group-hover:scale-105 transition-transform duration-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide">Historial Completo de Novedades</h3>
            <p class="text-xs text-slate-500 mt-1">Exporta todos los registros operacionales e historial de novedades diario generados en el sistema desde el primer día registrado. Útil para análisis estadísticos avanzados a largo plazo.</p>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-6">
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=historial_novedades`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/20 hover:border-emerald-500/30"
          >
            EXCEL Historial
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=historial_novedades`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-slate-500/10 border-slate-500/20 text-slate-400 hover:bg-slate-500/20 hover:border-slate-500/30"
          >
            CSV Historial
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=historial_novedades`"
            download
            class="flex items-center justify-center text-center px-3 py-2.5 rounded-xl text-[10px] font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/30"
          >
            PDF Historial
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

const meses = [
  'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO',
  'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
]

const selectedMonth = ref(appStore.selectedMonth || 'JUNIO')
const selectedDate = ref('')

onMounted(() => {
  if (appStore.availableDates.length === 0) {
    appStore.fetchAvailableDates()
  }
})

const sortedDates = computed(() => {
  return [...appStore.availableDates].sort((a, b) => b.localeCompare(a))
})

watch(sortedDates, (newDates) => {
  if (newDates.length > 0 && !selectedDate.value) {
    selectedDate.value = newDates[0]
  }
}, { immediate: true })

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length !== 3) return dateStr
  return `${parts[2]}/${parts[1]}/${parts[0]}`
}
</script>
