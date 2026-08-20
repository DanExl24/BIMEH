<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl space-y-4 border border-darkBorder shadow-xl flex flex-col justify-between">
    <div class="space-y-3">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center font-black text-xs shrink-0">
          01
        </div>
        <div>
          <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
            Consolidado Mensual
          </h4>
          <span class="text-xs text-slate-400">Matriz completa de novedades por mes</span>
        </div>
      </div>

      <div class="space-y-2 pt-2">
        <label class="text-xs uppercase font-bold text-slate-300">Seleccionar Mes:</label>
        <select 
          v-model="selectedMonth" 
          class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 shadow-sm cursor-pointer"
        >
          <option v-for="m in months" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>
    </div>

    <!-- Download Buttons -->
    <div class="grid grid-cols-2 gap-2 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/excel?tipo=consolidado_mensual&mes=${selectedMonth}`, `Consolidado Mensual (${selectedMonth})`, 'excel')" 
        class="py-2.5 bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/pdf?tipo=consolidado_mensual&mes=${selectedMonth}`, `Consolidado Mensual (${selectedMonth})`, 'pdf')" 
        class="py-2.5 bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileText class="w-4 h-4" />
        <span>PDF</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { FileSpreadsheet, FileText } from 'lucide-vue-next'
import { MONTHS_LIST } from '@utils/date'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

const props = defineProps<{
  apiBase: string
  defaultMonth?: string
}>()

const months = MONTHS_LIST
const selectedMonth = ref(props.defaultMonth || 'MAYO')
const reportStore = useReportDownloadStore()
</script>
