<template>
  <div class="glass-panel p-5 sm:p-6 rounded-3xl flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-300 group border border-darkBorder shadow-xl">
    <div class="space-y-3.5">
      <div 
        class="w-12 h-12 rounded-2xl flex items-center justify-center group-hover:scale-105 transition-transform duration-200 shadow-sm"
        :class="iconBgClass"
      >
        <slot name="icon" />
      </div>
      <div>
        <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">{{ title }}</h3>
        <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">{{ description }}</p>
      </div>
    </div>
    
    <div class="grid grid-cols-3 gap-2 sm:gap-2.5 mt-6 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="reportStore.downloadReport(excelUrl, `${title} (Excel)`, 'excel')"
        class="flex items-center justify-center gap-1.5 text-center px-3 py-2.5 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/15 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 hover:border-emerald-500/50 active:scale-95"
      >
        <FileSpreadsheet class="w-3.5 h-3.5" />
        <span>Excel</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(csvUrl, `${title} (CSV)`, 'csv')"
        class="flex items-center justify-center gap-1.5 text-center px-3 py-2.5 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-darkBg border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 active:scale-95"
      >
        <FileCode class="w-3.5 h-3.5" />
        <span>CSV</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(pdfUrl, `${title} (PDF)`, 'pdf')"
        class="flex items-center justify-center gap-1.5 text-center px-3 py-2.5 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/15 border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 hover:border-cyan-500/50 active:scale-95"
      >
        <FileText class="w-3.5 h-3.5" />
        <span>PDF</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileSpreadsheet, FileCode, FileText } from 'lucide-vue-next'
import { useReportDownloadStore } from '../../stores/reportDownloadStore'

defineProps<{
  title: string
  description: string
  excelUrl: string
  csvUrl: string
  pdfUrl: string
  iconBgClass?: string
}>()

const reportStore = useReportDownloadStore()
</script>


