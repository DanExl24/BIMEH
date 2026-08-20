<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
    <div class="glass-panel max-w-md w-full p-5 sm:p-7 rounded-3xl space-y-5 sm:space-y-6 shadow-2xl border border-darkBorder max-h-[calc(100dvh-2rem)] overflow-y-auto">
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-darkBorder/60 pb-4">
        <div class="flex items-center gap-2.5">
          <div class="w-2 h-5 bg-cyan-400 rounded-sm"></div>
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">
            {{ title || 'Generar Reporte Oficial' }}
          </h3>
        </div>
        <button 
          @click="$emit('close')" 
          class="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Form fields -->
      <div class="space-y-4">
        <!-- Formato selector -->
        <div class="space-y-1.5">
          <label class="text-xs uppercase font-bold text-slate-300">Formato de Exportación:</label>
          <div class="grid grid-cols-3 gap-2">
            <button 
              type="button"
              @click="format = 'excel'"
              class="py-2.5 text-xs font-bold rounded-xl transition-all border cursor-pointer flex items-center justify-center gap-1.5 select-none"
              :class="format === 'excel' ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300 shadow-sm' : 'bg-darkBg border-darkBorder text-slate-400 hover:text-slate-200'"
            >
              <FileSpreadsheet class="w-3.5 h-3.5" />
              <span>Excel</span>
            </button>
            <button 
              type="button"
              @click="format = 'csv'"
              class="py-2.5 text-xs font-bold rounded-xl transition-all border cursor-pointer flex items-center justify-center gap-1.5 select-none"
              :class="format === 'csv' ? 'bg-slate-700/40 border-slate-600 text-slate-200 shadow-sm' : 'bg-darkBg border-darkBorder text-slate-400 hover:text-slate-200'"
            >
              <FileCode class="w-3.5 h-3.5" />
              <span>CSV</span>
            </button>
            <button 
              type="button"
              @click="format = 'pdf'"
              class="py-2.5 text-xs font-bold rounded-xl transition-all border cursor-pointer flex items-center justify-center gap-1.5 select-none"
              :class="format === 'pdf' ? 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300 shadow-sm' : 'bg-darkBg border-darkBorder text-slate-400 hover:text-slate-200'"
            >
              <FileText class="w-3.5 h-3.5" />
              <span>PDF</span>
            </button>
          </div>
        </div>

        <!-- Tipo / Rango selector -->
        <div class="space-y-1.5">
          <label class="text-xs uppercase font-bold text-slate-300">Tipo de Reporte:</label>
          <select 
            v-model="reportType"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option value="personal">Historial Completo (Listado Cronológico)</option>
            <option value="consolidado_mensual">Heatmap Matriz (Mensual o Anual)</option>
            <option value="agil">Exportación Ágil (Novedades Simplificadas)</option>
          </select>
        </div>

        <!-- Mes selector -->
        <div v-if="reportType === 'consolidado_mensual' || reportType === 'personal' || reportType === 'agil'" class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-xs uppercase font-bold text-slate-300">Mes del Reporte:</label>
            <span class="text-[11px] text-slate-500 font-medium">(Opcional)</span>
          </div>
          <select 
            v-model="selectedMonth"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option value="">Todos los Meses (Consolidado Anual)</option>
            <option v-for="m in effectiveAvailableMonths" :key="m" :value="m">{{ m }}</option>
          </select>

        </div>

        <!-- Modo selector (solo para consolidado_mensual) -->
        <div v-if="reportType === 'consolidado_mensual'" class="space-y-1.5">
          <label class="text-xs uppercase font-bold text-slate-300">Modo de Celdas:</label>
          <select 
            v-model="mode"
            :disabled="!selectedMonth || selectedMonth === ''"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm disabled:opacity-40"
          >
            <option value="letras">LETRAS DEFINIDAS (D, N, R)</option>
            <option value="detalle">DETALLE DE NOVEDAD</option>
          </select>
        </div>

        <!-- Subnovedad selector (Opcional) -->
        <div v-if="subnovedades && subnovedades.length > 0" class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-xs uppercase font-bold text-slate-300">Filtrar por Subnovedad:</label>
            <span class="text-[11px] text-slate-500 font-medium">(Opcional)</span>
          </div>
          <select 
            v-model="selectedSubnovedad"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
          >
            <option value="">Todas las Subnovedades</option>
            <option v-for="s in subnovedades" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-3 pt-4 border-t border-darkBorder/60">
        <button 
          type="button"
          @click="$emit('close')"
          class="flex-1 px-4 py-2.5 border border-darkBorder hover:bg-darkBg rounded-xl text-xs font-bold text-slate-400 hover:text-slate-200 transition-all cursor-pointer select-none"
        >
          Cancelar
        </button>
        <button 
          type="button"
          @click="handleExport"
          class="flex-1 px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl text-xs font-bold text-white text-center transition-all cursor-pointer shadow-md select-none flex items-center justify-center gap-1.5 active:scale-95"
        >
          <Download class="w-4 h-4 stroke-[2.5]" />
          <span>Descargar</span>
        </button>
      </div>
    </div>
  </div>

</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  X, 
  Download, 
  FileSpreadsheet, 
  FileCode, 
  FileText 
} from 'lucide-vue-next'
import { useAppStore } from '../../stores/appStore'
import { useDateStore } from '../../stores/dateStore'
import { useReportDownloadStore } from '../../stores/reportDownloadStore'

const props = withDefaults(
  defineProps<{
    isOpen: boolean
    title?: string
    cedula?: number | string
    defaultReportType?: 'personal' | 'consolidado_mensual' | 'agil'
    defaultMonth?: string
    availableMonths?: string[]
    subnovedades?: string[]
  }>(),
  {
    title: 'Generar Reporte Oficial',
    defaultReportType: 'personal',
    defaultMonth: '',
    availableMonths: () => [],
    subnovedades: () => []
  }
)

const emit = defineEmits<{
  (e: 'close'): void
}>()

const appStore = useAppStore()
const dateStore = useDateStore()
const reportStore = useReportDownloadStore()


const format = ref<'excel' | 'csv' | 'pdf'>('excel')
const reportType = ref<'personal' | 'consolidado_mensual' | 'agil'>(props.defaultReportType)
const selectedMonth = ref(props.defaultMonth || dateStore.selectedMonth || dateStore.latestMonth || '')
const selectedSubnovedad = ref('')
const mode = ref<'letras' | 'detalle'>('letras')

const effectiveAvailableMonths = computed(() => {
  if (props.availableMonths && props.availableMonths.length > 0) {
    return props.availableMonths
  }
  return dateStore.availableMonths
})

watch(
  () => props.defaultReportType,
  (newType) => {
    if (newType) reportType.value = newType
  }
)

watch(
  () => props.defaultMonth,
  (newMonth) => {
    if (newMonth) selectedMonth.value = newMonth
  }
)

watch(
  effectiveAvailableMonths,
  (newMonths) => {
    if (newMonths && newMonths.length > 0 && selectedMonth.value && !newMonths.includes(selectedMonth.value)) {
      selectedMonth.value = newMonths[newMonths.length - 1]
    }
  },
  { immediate: true }
)


const downloadUrl = computed(() => {
  const cedulaParam = props.cedula ? `&cedula=${props.cedula}` : ''
  let url = `${appStore.apiBase}/api/exportar/${format.value}?tipo=${reportType.value}${cedulaParam}`

  if (reportType.value === 'consolidado_mensual' || reportType.value === 'agil') {
    url += `&mes=${selectedMonth.value}&modo=${mode.value}`
  } else if (reportType.value === 'personal' && selectedMonth.value) {
    url += `&mes=${selectedMonth.value}`
  }

  if (selectedSubnovedad.value) {
    url += `&subnovedad=${encodeURIComponent(selectedSubnovedad.value)}`
  }

  return url
})

const handleExport = () => {
  const typeLabelMap: Record<string, string> = {
    personal: 'Historial de Personal',
    consolidado_mensual: 'Consolidado Mensual',
    agil: 'Exportación Ágil'
  }
  const title = `${typeLabelMap[reportType.value] || 'Reporte'} (${selectedMonth.value || 'Anual'})`
  emit('close')
  reportStore.downloadReport(downloadUrl.value, title, format.value)
}
</script>


