<template>
  <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 border border-darkBorder shadow-xl">
    <div>
      <div class="flex items-center gap-2.5">
        <div class="w-2.5 h-6 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-sm"></div>
        <h3 class="text-base sm:text-lg font-black text-slate-100 uppercase tracking-tight">
          Carga & Sincronización de Reportes
        </h3>
      </div>
      <p class="text-xs text-slate-400 mt-1.5 font-medium leading-relaxed">
        Sube tus reportes diarios o mensuales en formato Excel o JSON para actualizar los datos operacionales de la base de datos.
      </p>
    </div>

    <!-- Template Download Buttons -->
    <div class="flex items-center gap-2.5 flex-wrap">
      <span class="text-xs uppercase font-bold text-slate-400 mr-1">Descargar Plantillas:</span>
      <a 
        :href="`${apiBase}/api/sincronizar/plantilla/excel`" 
        download
        class="px-3.5 py-2 bg-emerald-500/15 border border-emerald-500/30 hover:border-emerald-500/50 hover:bg-emerald-500/25 rounded-xl text-xs font-bold text-emerald-300 flex items-center gap-1.5 transition-all select-none cursor-pointer shadow-sm active:scale-95"
      >
        <FileSpreadsheet class="w-4 h-4" />
        <span>Plantilla Excel</span>
      </a>
      <a 
        :href="`${apiBase}/api/sincronizar/plantilla/json`" 
        download
        class="px-3.5 py-2 bg-darkBg border border-slate-700 hover:border-slate-500 hover:text-white rounded-xl text-xs font-bold text-slate-300 flex items-center gap-1.5 transition-all select-none cursor-pointer shadow-sm active:scale-95"
      >
        <FileCode class="w-4 h-4" />
        <span>Plantilla JSON</span>
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FileSpreadsheet, FileCode } from 'lucide-vue-next'

defineProps<{
  apiBase: string
}>()
</script>

