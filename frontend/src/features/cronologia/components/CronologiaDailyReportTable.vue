<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col space-y-5 border border-darkBorder shadow-xl">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-darkBorder/60 pb-4">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="w-2 h-5 bg-cyan-400 rounded-sm"></div>
          <h4 class="text-sm sm:text-base font-bold text-slate-100 uppercase tracking-tight">
            Reporte Diario Oficial del Personal
          </h4>
        </div>
        <p class="text-xs text-slate-400 mt-1 font-mono">
          Fecha: <strong class="text-cyan-300">{{ activeDate }}</strong> | Total efectivos registrados: <strong class="text-slate-200">{{ dailyReport.length }}</strong>
        </p>
      </div>

      <!-- Export Buttons -->
      <div v-if="dailyReport.length > 0" class="flex flex-wrap items-center gap-2.5">
        <button 
          type="button"
          @click="reportStore.downloadReport(`${apiBase}/api/exportar/csv?tipo=dia&fecha=${activeDate}`, `Reporte Diario (${activeDate})`, 'csv')"
          class="px-3.5 py-2 bg-darkBg border border-slate-700 hover:border-slate-500 rounded-xl text-xs font-bold text-slate-300 hover:text-white transition-all cursor-pointer shadow-sm flex items-center gap-1.5 active:scale-95"
        >
          <FileCode class="w-3.5 h-3.5 text-slate-400" />
          <span>CSV</span>
        </button>
        <button 
          type="button"
          @click="reportStore.downloadReport(`${apiBase}/api/exportar/excel?tipo=dia&fecha=${activeDate}`, `Reporte Diario (${activeDate})`, 'excel')"
          class="px-3.5 py-2 bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm flex items-center gap-1.5 active:scale-95"
        >
          <FileSpreadsheet class="w-3.5 h-3.5" />
          <span>Excel</span>
        </button>
        <button 
          type="button"
          @click="reportStore.downloadReport(`${apiBase}/api/exportar/pdf?tipo=dia&fecha=${activeDate}`, `Reporte Diario (${activeDate})`, 'pdf')"
          class="px-3.5 py-2 bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm flex items-center gap-1.5 active:scale-95"
        >
          <FileText class="w-3.5 h-3.5" />
          <span>PDF</span>
        </button>
      </div>

    </div>

    <!-- Search in daily report -->
    <div class="relative">
      <input 
        type="text" 
        :value="dailySearch"
        @input="$emit('update:dailySearch', ($event.target as HTMLInputElement).value)"
        placeholder="Filtrar reporte por apellidos, cédula o subnovedad..."
        class="w-full bg-darkBg border border-darkBorder rounded-2xl pl-11 pr-4 py-3 text-xs sm:text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 transition-colors shadow-inner"
      />
      <Search class="w-4 h-4 absolute left-4 top-3.5 text-slate-400 pointer-events-none" />
    </div>

    <!-- Detailed table -->
    <div class="glass-panel rounded-2xl border border-darkBorder overflow-hidden shadow-xl">
      <div v-if="loadingDaily" class="flex justify-center items-center py-20">
        <Loader2 class="w-8 h-8 text-cyan-400 animate-spin" />
      </div>
      <div v-else-if="filteredDailyReport.length > 0" class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
          <thead>
            <tr class="border-b border-darkBorder text-xs text-slate-400 uppercase font-semibold bg-darkBg/60">
              <th class="py-3 px-4">Cédula</th>
              <th class="py-3 px-4">Apellidos y Nombres</th>
              <th class="py-3 px-4 text-center">Estado</th>
              <th class="py-3 px-4">Descripción / Justificación</th>
              <th class="py-3 px-4">Desde</th>
              <th class="py-3 px-4">Hasta</th>
            </tr>
          </thead>
          <tbody class="text-xs">
            <tr 
              v-for="r in filteredDailyReport" 
              :key="r.cedula"
              class="border-b border-darkBorder/30 hover:bg-slate-800/30 transition-colors"
            >
              <td class="py-3 px-4 font-mono font-bold text-slate-300">{{ r.cedula }}</td>
              <td class="py-3 px-4 font-bold text-slate-100 hover:text-cyan-300 uppercase">
                <router-link :to="`/personal/${r.cedula}`">{{ r.nombre }}</router-link>
              </td>
              <td class="py-3 px-4 text-center">
                <span 
                  class="text-xs font-bold px-2.5 py-0.5 rounded-md border uppercase inline-block"
                  :class="isAvailable(r.subnovedad) ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400' : 'bg-amber-500/15 border-amber-500/30 text-amber-400'"
                >
                  {{ r.subnovedad }}
                </span>
              </td>
              <td class="py-3 px-4 text-slate-300 max-w-[240px] truncate uppercase" :title="r.descripcion || undefined">
                {{ r.descripcion || 'Sin justificación' }}
              </td>
              <td class="py-3 px-4 font-mono text-slate-400">{{ r.desde || '-' }}</td>
              <td class="py-3 px-4 font-mono text-slate-400">{{ r.hasta || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-20 text-slate-400 text-xs font-medium">
        No se encontraron registros que coincidan con los filtros ingresados.
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  FileCode, 
  FileSpreadsheet, 
  FileText, 
  Search, 
  Loader2 
} from 'lucide-vue-next'
import type { PersonalDia } from '@types'
import { isAvailable } from '@utils/personal.utils'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

defineProps<{
  activeDate: string
  dailyReport: PersonalDia[]
  filteredDailyReport: PersonalDia[]
  dailySearch: string
  loadingDaily: boolean
  apiBase: string
}>()

defineEmits<{
  (e: 'update:dailySearch', val: string): void
}>()

const reportStore = useReportDownloadStore()
</script>
