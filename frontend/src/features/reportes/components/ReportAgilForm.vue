<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl h-full flex flex-col justify-between border border-cyan-500/40 bg-gradient-to-br from-cyan-950/20 via-darkPanel to-blue-950/20 hover:border-cyan-400/60 transition-all duration-300 group shadow-xl shadow-cyan-950/20">
    <div class="space-y-3.5">
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-2xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-300 group-hover:scale-105 transition-transform duration-200 shadow-md shadow-cyan-500/10">
            <Zap class="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">
              Exportación Ágil de Novedades
            </h3>
            <span class="text-xs text-slate-400">Consolidación de rangos continuos de fechas</span>
          </div>
        </div>
        <span class="hidden sm:inline-block px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-mono shrink-0">
          Exclusivo Novedades
        </span>
      </div>

      <p class="text-xs text-slate-400 leading-relaxed">
        Reporte condensado que excluye días disponibles y simplifica rangos (ej: <span class="text-cyan-300 font-bold font-mono">10-15 (VACACIONES)</span>) para lectura rápida.
      </p>

      <!-- Grid of Controls -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1 bg-darkBg/60 p-3.5 rounded-2xl border border-darkBorder/60">
        <div class="space-y-1">
          <label class="text-[11px] uppercase font-bold text-slate-300 tracking-wider">Período Ágil:</label>
          <select 
            v-model="agilMode"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option value="ANUAL">TODOS LOS MESES (ANUAL)</option>
            <option value="MES">MES ESPECÍFICO</option>
            <option value="DIA">DÍA ESPECÍFICO</option>
          </select>
        </div>

        <div v-if="agilMode === 'MES' || agilMode === 'DIA'" class="space-y-1">
          <label class="text-[11px] uppercase font-bold text-slate-300 tracking-wider">
            {{ agilMode === 'DIA' ? 'Seleccionar Día:' : 'Seleccionar Mes:' }}
          </label>
          <select 
            v-if="agilMode === 'MES'"
            v-model="agilSelectedMonth"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
          </select>

          <select 
            v-else
            v-model="agilSelectedDate"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option v-for="d in agilFilteredDates" :key="d" :value="d">{{ formatDate(d) }}</option>
          </select>
        </div>

        <div v-else class="space-y-1 flex flex-col justify-end">
          <span class="text-[11px] text-slate-500 italic pb-1">Todo el año operacional</span>
          <div class="px-3 py-1.5 bg-darkCard/50 rounded-xl border border-darkBorder/40 text-[11px] font-mono text-cyan-400/80">
            12 Meses consolidados
          </div>
        </div>
      </div>
    </div>

    <!-- Download Buttons -->
    <div class="grid grid-cols-2 gap-3 mt-6 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="reportStore.downloadReport(agilExcelUrl, `Exportación Ágil (${agilLabel}) - Excel`, 'excel')"
        class="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/20 border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/30 hover:border-emerald-500/60 active:scale-95"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel ({{ agilLabel }})</span>
      </button>
      <button 
        type="button"
        @click="reportStore.downloadReport(agilPdfUrl, `Exportación Ágil (${agilLabel}) - PDF`, 'pdf')"
        class="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/20 border-cyan-500/40 text-cyan-300 hover:bg-cyan-500/30 hover:border-cyan-500/60 active:scale-95"
      >
        <FileText class="w-4 h-4" />
        <span>PDF ({{ agilLabel }})</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Zap, FileSpreadsheet, FileText } from 'lucide-vue-next'
import { useReportDownloadStore } from '@stores/reportDownloadStore'
import { MONTH_TO_NUMBER } from '@utils/date'

const reportStore = useReportDownloadStore()

const props = defineProps<{
  apiBase: string
  activeMonths: string[]
  sortedDates: string[]
  defaultMonth: string
}>()

const agilMode = ref<'ANUAL' | 'MES' | 'DIA'>('ANUAL')
const agilSelectedMonth = ref(props.defaultMonth || 'MAYO')
const agilSelectedDate = ref('')

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length !== 3) return dateStr
  return `${parts[2]}/${parts[1]}/${parts[0]}`
}

const agilFilteredDates = computed(() => {
  const monthNum = MONTH_TO_NUMBER[agilSelectedMonth.value]
  if (!monthNum) return props.sortedDates
  const filtered = props.sortedDates.filter(d => d.split('-')[1] === monthNum)
  return filtered.length > 0 ? filtered : props.sortedDates
})

watch(() => props.activeMonths, (newMonths) => {
  if (newMonths && newMonths.length > 0) {
    if (!newMonths.includes(agilSelectedMonth.value)) {
      agilSelectedMonth.value = newMonths[newMonths.length - 1]
    }
  }
}, { immediate: true })

watch(() => props.defaultMonth, (newMonth) => {
  if (newMonth && props.activeMonths.includes(newMonth)) {
    agilSelectedMonth.value = newMonth
  }
})

watch(agilFilteredDates, (newDates) => {
  if (newDates.length > 0) agilSelectedDate.value = newDates[0]
}, { immediate: true })

const agilLabel = computed(() => {
  if (agilMode.value === 'ANUAL') return 'ANUAL'
  if (agilMode.value === 'MES') return agilSelectedMonth.value
  return formatDate(agilSelectedDate.value)
})

const agilExcelUrl = computed(() => {
  if (agilMode.value === 'ANUAL') return `${props.apiBase}/api/exportar/excel?tipo=agil&mes=TODOS`
  if (agilMode.value === 'MES') return `${props.apiBase}/api/exportar/excel?tipo=agil&mes=${agilSelectedMonth.value}`
  return `${props.apiBase}/api/exportar/excel?tipo=agil&fecha=${agilSelectedDate.value}`
})

const agilPdfUrl = computed(() => {
  if (agilMode.value === 'ANUAL') return `${props.apiBase}/api/exportar/pdf?tipo=agil&mes=TODOS`
  if (agilMode.value === 'MES') return `${props.apiBase}/api/exportar/pdf?tipo=agil&mes=${agilSelectedMonth.value}`
  return `${props.apiBase}/api/exportar/pdf?tipo=agil&fecha=${agilSelectedDate.value}`
})
</script>
