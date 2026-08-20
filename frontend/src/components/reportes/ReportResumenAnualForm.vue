<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col justify-between hover:border-cyan-500/40 transition-all duration-300 group md:col-span-2 border border-darkBorder shadow-xl">
    <div class="flex flex-col md:flex-row md:items-start justify-between gap-5">
      <div class="space-y-3.5 flex-1">
        <div class="w-12 h-12 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform duration-200 shadow-sm">
          <CalendarRange class="w-6 h-6 stroke-[2]" />
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">Reporte Detallado de Personal</h3>
          <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">
            Exporta el reporte detallado con cédula, nombres, subnovedad, descripción y fechas exactas. Puedes filtrar por todos los meses (anual), un mes en específico o un día específico.
          </p>
        </div>
      </div>
      
      <!-- Detailed Filter Controls -->
      <div class="flex flex-col gap-3 w-full md:w-72 bg-darkBg/60 p-4 rounded-2xl border border-darkBorder/60">
        <div class="flex flex-col gap-1">
          <label class="text-xs uppercase font-bold text-slate-300 tracking-wider">Período a Exportar:</label>
          <select 
            v-model="detalladoScope"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option value="ANUAL">TODOS LOS MESES (ANUAL)</option>
            <option value="MES">MES ESPECÍFICO</option>
            <option value="DIA">DÍA ESPECÍFICO</option>
          </select>
        </div>

        <!-- Month Dropdown (visible for MES or DIA) -->
        <div v-if="detalladoScope === 'MES' || detalladoScope === 'DIA'" class="flex flex-col gap-1">
          <label class="text-xs uppercase font-bold text-slate-300 tracking-wider">Seleccionar Mes:</label>
          <select 
            v-model="detalladoSelectedMonth"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Date Dropdown (filtered by selected month) -->
        <div v-if="detalladoScope === 'DIA'" class="flex flex-col gap-1">
          <label class="text-xs uppercase font-bold text-slate-300 tracking-wider">Seleccionar Día (de {{ detalladoSelectedMonth }}):</label>
          <select 
            v-model="detalladoSelectedDate"
            class="w-full bg-darkCard border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option v-for="d in detalladoFilteredDates" :key="d" :value="d">{{ formatDate(d) }}</option>
          </select>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mt-8 pt-4 border-t border-darkBorder/60">
      <a 
        :href="detalladoExcelUrl"
        download
        class="flex items-center justify-center gap-2 text-center px-4 py-2.5 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-emerald-500/15 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/25 hover:border-emerald-500/50 active:scale-95"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel Detallado ({{ detalladoLabel }})</span>
      </a>
      <a 
        :href="detalladoCsvUrl"
        download
        class="flex items-center justify-center gap-2 text-center px-4 py-2.5 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-darkBg border-slate-700 text-slate-300 hover:text-white hover:border-slate-500 active:scale-95"
      >
        <FileCode class="w-4 h-4" />
        <span>CSV Detallado ({{ detalladoLabel }})</span>
      </a>
      <a 
        :href="detalladoPdfUrl"
        download
        class="flex items-center justify-center gap-2 text-center px-4 py-2.5 rounded-xl text-xs font-bold uppercase transition-all duration-200 border cursor-pointer select-none shadow-sm bg-cyan-500/15 border-cyan-500/30 text-cyan-300 hover:bg-cyan-500/25 hover:border-cyan-500/50 active:scale-95"
      >
        <FileText class="w-4 h-4" />
        <span>PDF Detallado ({{ detalladoLabel }})</span>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CalendarRange, FileSpreadsheet, FileCode, FileText } from 'lucide-vue-next'

const props = defineProps<{
  apiBase: string
  activeMonths: string[]
  sortedDates: string[]
  monthToNumber: Record<string, string>
  defaultMonth: string
}>()

const detalladoScope = ref<'ANUAL' | 'MES' | 'DIA'>('ANUAL')
const detalladoSelectedMonth = ref(props.defaultMonth || 'JULIO')
const detalladoSelectedDate = ref('')

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  const parts = dateStr.split('-')
  if (parts.length !== 3) return dateStr
  return `${parts[2]}/${parts[1]}/${parts[0]}`
}

const detalladoFilteredDates = computed(() => {
  const monthNum = props.monthToNumber[detalladoSelectedMonth.value]
  if (!monthNum) return props.sortedDates
  const filtered = props.sortedDates.filter(d => d.split('-')[1] === monthNum)
  return filtered.length > 0 ? filtered : props.sortedDates
})

watch(detalladoFilteredDates, (newDates) => {
  if (newDates.length > 0) detalladoSelectedDate.value = newDates[0]
}, { immediate: true })

const detalladoLabel = computed(() => {
  if (detalladoScope.value === 'ANUAL') return 'ANUAL'
  if (detalladoScope.value === 'MES') return detalladoSelectedMonth.value
  return formatDate(detalladoSelectedDate.value)
})

const detalladoExcelUrl = computed(() => {
  let url = `${props.apiBase}/api/exportar/excel?tipo=dia`
  if (detalladoScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (detalladoScope.value === 'MES') url += `&mes=${detalladoSelectedMonth.value}`
  else url += `&fecha=${detalladoSelectedDate.value}`
  return url
})

const detalladoCsvUrl = computed(() => {
  let url = `${props.apiBase}/api/exportar/csv?tipo=dia`
  if (detalladoScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (detalladoScope.value === 'MES') url += `&mes=${detalladoSelectedMonth.value}`
  else url += `&fecha=${detalladoSelectedDate.value}`
  return url
})

const detalladoPdfUrl = computed(() => {
  let url = `${props.apiBase}/api/exportar/pdf?tipo=dia`
  if (detalladoScope.value === 'ANUAL') url += '&mes=TODOS'
  else if (detalladoScope.value === 'MES') url += `&mes=${detalladoSelectedMonth.value}`
  else url += `&fecha=${detalladoSelectedDate.value}`
  return url
})
</script>

