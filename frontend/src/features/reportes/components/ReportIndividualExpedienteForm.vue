<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl space-y-4 border border-darkBorder shadow-xl flex flex-col justify-between">
    <div class="space-y-3">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center font-black text-xs shrink-0">
          03
        </div>
        <div>
          <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
            Expediente Individual
          </h4>
          <span class="text-xs text-slate-400">Historial completo por número de cédula</span>
        </div>
      </div>

      <div class="space-y-2 pt-2">
        <label class="text-xs uppercase font-bold text-slate-300">Cédula del Integrante:</label>
        <input 
          type="number" 
          v-model="cedulaInput" 
          placeholder="Ingresa número de cédula..."
          class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 shadow-sm"
        />
      </div>
    </div>

    <!-- Download Buttons -->
    <div class="grid grid-cols-2 gap-2 pt-4 border-t border-darkBorder/60">
      <button 
        type="button"
        @click="downloadIndividual('excel')"
        :disabled="!cedulaInput"
        class="py-2.5 bg-emerald-500/15 hover:bg-emerald-500/25 disabled:opacity-40 disabled:pointer-events-none border border-emerald-500/30 rounded-xl text-xs font-bold text-emerald-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Excel</span>
      </button>
      <button 
        type="button"
        @click="downloadIndividual('pdf')"
        :disabled="!cedulaInput"
        class="py-2.5 bg-cyan-500/15 hover:bg-cyan-500/25 disabled:opacity-40 disabled:pointer-events-none border border-cyan-500/30 rounded-xl text-xs font-bold text-cyan-300 flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95 select-none"
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
import { useReportDownloadStore } from '@stores/reportDownloadStore'

const props = defineProps<{
  apiBase: string
}>()

const cedulaInput = ref<number | ''>('')
const reportStore = useReportDownloadStore()

const downloadIndividual = (format: 'excel' | 'pdf') => {
  if (!cedulaInput.value) return
  const url = `${props.apiBase}/api/exportar/${format}?tipo=personal&cedula=${cedulaInput.value}`
  reportStore.downloadReport(url, `Expediente Individual (${cedulaInput.value})`, format)
}
</script>
