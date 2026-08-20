<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl space-y-4 border border-darkBorder shadow-xl relative overflow-hidden">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0">
        <Zap class="w-5 h-5 stroke-[2.5]" />
      </div>
      <div>
        <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Descarga Directa: {{ selectedMonth }}
        </h4>
        <p class="text-xs text-slate-400 mt-0.5">
          Obtén el consolidado del mes seleccionado con un solo clic.
        </p>
      </div>
    </div>

    <!-- Quick Buttons Row -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/excel?tipo=consolidado_mensual&mes=${selectedMonth}`, `Consolidado Mensual (${selectedMonth})`, 'excel')" 
        class="py-3 px-4 bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 rounded-2xl text-xs font-bold text-emerald-300 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm active:scale-98 select-none"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Descargar Excel Oficial ({{ selectedMonth }})</span>
      </button>

      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/pdf?tipo=consolidado_mensual&mes=${selectedMonth}`, `Consolidado Mensual (${selectedMonth})`, 'pdf')" 
        class="py-3 px-4 bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 rounded-2xl text-xs font-bold text-cyan-300 flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm active:scale-98 select-none"
      >
        <FileText class="w-4 h-4" />
        <span>Descargar PDF Oficial ({{ selectedMonth }})</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Zap, FileSpreadsheet, FileText } from 'lucide-vue-next'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

defineProps<{
  selectedMonth: string
  apiBase: string
}>()

const reportStore = useReportDownloadStore()
</script>
