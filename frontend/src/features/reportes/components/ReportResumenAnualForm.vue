<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl space-y-4 border border-darkBorder shadow-xl flex flex-col justify-between">
    <div class="space-y-3">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center font-black text-xs shrink-0">
          02
        </div>
        <div>
          <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
            Resumen Anual Consolidado
          </h4>
          <span class="text-xs text-slate-400">Total acumulado de novedades de todo el año</span>
        </div>
      </div>

      <p class="text-xs text-slate-400 leading-relaxed pt-2">
        Genera el informe global con los porcentajes de disponibilidad, días acumulados en novedad y ranking del personal.
      </p>
    </div>

    <!-- Download Buttons -->
    <div class="grid grid-cols-2 gap-2 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/excel?tipo=resumen_anual`, 'Resumen Anual Completo', 'excel')" 
        class="py-2.5 bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/pdf?tipo=resumen_anual`, 'Resumen Anual Completo', 'pdf')" 
        class="py-2.5 bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileText class="w-4 h-4" />
        <span>PDF</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileSpreadsheet, FileText } from 'lucide-vue-next'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

defineProps<{
  apiBase: string
}>()

const reportStore = useReportDownloadStore()
</script>
