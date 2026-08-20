<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl h-full flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-300 group border border-darkBorder shadow-xl">
    <div class="space-y-3.5">
      <div class="flex items-center gap-3">
        <div class="w-12 h-12 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform duration-200 shadow-sm">
          <TableProperties class="w-6 h-6 stroke-[2]" />
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">
            Consolidado Mensual (Matriz Heatmap)
          </h3>
          <span class="text-xs text-slate-400">Matriz completa de novedades por mes</span>
        </div>
      </div>

      <p class="text-xs text-slate-400 leading-relaxed">
        Matriz integral de la unidad día a día. Refleja la operatividad de cada militar en el mes con codificación de colores o letras.
      </p>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 bg-darkBg/60 p-3.5 rounded-2xl border border-darkBorder/60">
        <div class="space-y-1">
          <label class="text-[11px] uppercase font-bold text-slate-300 tracking-wider">Mes Operacional:</label>
          <select 
            v-model="selectedMonth" 
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 shadow-sm cursor-pointer"
          >
            <option value="TODOS">TODOS LOS MESES (ANUAL)</option>
            <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <div class="space-y-1">
          <label class="text-[11px] uppercase font-bold text-slate-300 tracking-wider">Formato de Celdas:</label>
          <select 
            v-model="selectedMode" 
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 shadow-sm cursor-pointer"
          >
            <option value="letras">Abreviado (D / N / R)</option>
            <option value="completo">Nombre de Subnovedad</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Download Buttons -->
    <div class="grid grid-cols-3 gap-2 mt-6 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/excel?tipo=consolidado_mensual&mes=${selectedMonth}&modo=${selectedMode}`, `Consolidado (${selectedMonth}) - Excel`, 'excel')" 
        class="py-2.5 px-2 bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/pdf?tipo=consolidado_mensual&mes=${selectedMonth}&modo=${selectedMode}`, `Consolidado (${selectedMonth}) - PDF`, 'pdf')" 
        class="py-2.5 px-2 bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileText class="w-4 h-4" />
        <span>PDF</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(`${apiBase}/api/exportar/csv?tipo=consolidado_mensual&mes=${selectedMonth}&modo=${selectedMode}`, `Consolidado (${selectedMonth}) - CSV`, 'csv')" 
        class="py-2.5 px-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileCode class="w-4 h-4" />
        <span>CSV</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { TableProperties, FileSpreadsheet, FileText, FileCode } from 'lucide-vue-next'
import { useReportDownloadStore } from '@stores/reportDownloadStore'

const props = defineProps<{
  apiBase: string
  activeMonths: string[]
  defaultMonth?: string
}>()

const selectedMonth = ref(props.defaultMonth || 'MAYO')
const selectedMode = ref<'letras' | 'completo'>('letras')
const reportStore = useReportDownloadStore()

watch(() => props.defaultMonth, (newMonth) => {
  if (newMonth) selectedMonth.value = newMonth
})
</script>
