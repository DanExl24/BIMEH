<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col justify-between hover:border-purple-500/40 transition-all duration-300 group border border-darkBorder shadow-xl">
    <div class="space-y-3.5">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-2xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 group-hover:scale-105 transition-transform duration-200 shadow-sm">
          <UserCheck class="w-6 h-6 stroke-[2]" />
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">
            Expediente Individual de Personal
          </h3>
          <p class="text-xs text-slate-400 mt-1 leading-relaxed">
            Genera la hoja de vida operacional e historial de novedades detallado de un integrante por número de cédula.
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 bg-darkBg/60 p-3.5 rounded-2xl border border-darkBorder/60">
        <div class="space-y-1">
          <label class="text-[11px] uppercase font-bold text-slate-300 tracking-wider">Cédula del Integrante:</label>
          <input 
            v-model="cedulaInput" 
            type="number"
            placeholder="Ej: 1005234890"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 placeholder-slate-500 outline-none focus:border-purple-500/60 shadow-sm"
          />
        </div>

        <div class="space-y-1">
          <label class="text-[11px] uppercase font-bold text-slate-300 tracking-wider">Filtrar por Mes:</label>
          <select 
            v-model="selectedMonth" 
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-purple-500/60 shadow-sm cursor-pointer"
          >
            <option value="TODOS">TODOS LOS MESES (HISTORIAL COMPLETO)</option>
            <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Download Buttons -->
    <div class="grid grid-cols-3 gap-2 mt-6 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        :disabled="!cedulaInput"
        @click="reportStore.downloadReport(individualExcelUrl, `Expediente Individual (${cedulaInput}) - Excel`, 'excel')" 
        class="py-2.5 px-3 bg-emerald-500/15 hover:bg-emerald-500/25 disabled:opacity-40 disabled:cursor-not-allowed border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel</span>
      </button>
      <button 
        type="button"
        :disabled="!cedulaInput"
        @click="reportStore.downloadReport(individualPdfUrl, `Expediente Individual (${cedulaInput}) - PDF`, 'pdf')" 
        class="py-2.5 px-3 bg-cyan-500/15 hover:bg-cyan-500/25 disabled:opacity-40 disabled:cursor-not-allowed border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileText class="w-4 h-4" />
        <span>PDF</span>
      </button>
      <button 
        type="button"
        :disabled="!cedulaInput"
        @click="reportStore.downloadReport(individualCsvUrl, `Expediente Individual (${cedulaInput}) - CSV`, 'csv')" 
        class="py-2.5 px-3 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed border border-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileCode class="w-4 h-4" />
        <span>CSV</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { UserCheck, FileSpreadsheet, FileText, FileCode } from 'lucide-vue-next'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

const props = defineProps<{
  apiBase: string
  activeMonths: string[]
}>()

const cedulaInput = ref<number | ''>('')
const selectedMonth = ref<string>('TODOS')
const reportStore = useReportDownloadStore()

const individualExcelUrl = computed(() => {
  let url = `${props.apiBase}/api/exportar/excel?tipo=personal&cedula=${cedulaInput.value}`
  if (selectedMonth.value && selectedMonth.value !== 'TODOS') url += `&mes=${selectedMonth.value}`
  return url
})

const individualPdfUrl = computed(() => {
  let url = `${props.apiBase}/api/exportar/pdf?tipo=personal&cedula=${cedulaInput.value}`
  if (selectedMonth.value && selectedMonth.value !== 'TODOS') url += `&mes=${selectedMonth.value}`
  return url
})

const individualCsvUrl = computed(() => {
  let url = `${props.apiBase}/api/exportar/csv?tipo=personal&cedula=${cedulaInput.value}`
  if (selectedMonth.value && selectedMonth.value !== 'TODOS') url += `&mes=${selectedMonth.value}`
  return url
})
</script>
