<template>
  <div class="glass-panel p-5 sm:p-6 rounded-3xl flex flex-col justify-between border border-darkBorder hover:border-slate-600 transition-all duration-300 shadow-xl group">
    <div class="space-y-3">
      <div class="flex items-center gap-3">
        <div :class="['w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-sm transition-transform group-hover:scale-105', iconBgClass]">
          <slot name="icon" />
        </div>
        <div>
          <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wide">
            {{ title }}
          </h4>
          <span class="text-[11px] text-slate-400 font-medium leading-tight line-clamp-2 mt-0.5">
            {{ description }}
          </span>
        </div>
      </div>
    </div>

    <!-- Export format buttons -->
    <div class="grid grid-cols-3 gap-2 mt-5 pt-3.5 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="reportStore.downloadReport(excelUrl, `${title} - Excel`, 'excel')"
        class="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-300 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileSpreadsheet class="w-3.5 h-3.5" />
        <span>Excel</span>
      </button>

      <button 
        type="button"
        @click="reportStore.downloadReport(pdfUrl, `${title} - PDF`, 'pdf')"
        class="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileText class="w-3.5 h-3.5" />
        <span>PDF</span>
      </button>

      <button 
        type="button"
        @click="reportStore.downloadReport(csvUrl, `${title} - CSV`, 'csv')"
        class="flex items-center justify-center gap-1.5 py-2 px-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileCode class="w-3.5 h-3.5" />
        <span>CSV</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileSpreadsheet, FileText, FileCode } from 'lucide-vue-next'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

defineProps<{
  title: string
  description: string
  excelUrl: string
  pdfUrl: string
  csvUrl: string
  iconBgClass?: string
}>()

const reportStore = useReportDownloadStore()
</script>
