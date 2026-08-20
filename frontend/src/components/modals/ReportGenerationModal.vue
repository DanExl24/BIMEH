<template>
  <Teleport to="body">
    <div 
      v-if="reportStore.isModalOpen" 
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md transition-all duration-300 animate-in fade-in"
    >
      <div 
        class="glass-panel max-w-md w-full p-6 sm:p-7 rounded-3xl space-y-6 shadow-2xl border border-darkBorder font-sans relative overflow-hidden"
        :class="{
          'border-cyan-500/40 shadow-cyan-500/10': reportStore.status === 'generating',
          'border-emerald-500/40 shadow-emerald-500/10': reportStore.status === 'success',
          'border-red-500/40 shadow-red-500/10': reportStore.status === 'error'
        }"
      >
        <!-- Modal Header -->
        <div class="flex items-center justify-between border-b border-darkBorder/60 pb-4">
          <div class="flex items-center gap-2.5">
            <div 
              class="w-2.5 h-5 rounded-sm"
              :class="{
                'bg-cyan-400': reportStore.status === 'generating',
                'bg-emerald-400': reportStore.status === 'success',
                'bg-red-400': reportStore.status === 'error'
              }"
            ></div>
            <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wide">
              {{ modalHeaderTitle }}
            </h3>
          </div>
          <button 
            v-if="!reportStore.isGenerating"
            @click="reportStore.closeModal" 
            class="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
            title="Cerrar ventana"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <!-- 1. Estado: GENERANDO -->
        <div v-if="reportStore.status === 'generating'" class="py-4 text-center space-y-5">
          <!-- Animated rotating sync icon -->
          <div class="relative w-20 h-20 mx-auto flex items-center justify-center">
            <div class="absolute inset-0 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin"></div>
            <div class="w-14 h-14 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-300 shadow-inner">
              <RefreshCw class="w-6 h-6 animate-spin" style="animation-duration: 3s;" />
            </div>
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-center gap-2">
              <span class="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-md border" :class="formatBadgeClass">
                {{ (reportStore.reportFormat || 'DOC').toUpperCase() }}
              </span>
              <h4 class="text-sm font-bold text-slate-100 max-w-xs mx-auto truncate">
                {{ reportStore.reportTitle }}
              </h4>
            </div>
            <p class="text-xs text-cyan-300 font-medium animate-pulse">
              {{ reportStore.statusMessage }}
            </p>
            <p class="text-[11px] text-slate-400 font-mono">
              Tiempo transcurrido: <span class="text-slate-200 font-bold">{{ reportStore.secondsElapsed }}s</span>
            </p>
          </div>

          <!-- Pulsing Progress bar -->
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div class="h-full bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500 w-full animate-pulse"></div>
          </div>

          <!-- Cancel button -->
          <div class="pt-2">
            <button 
              type="button"
              @click="reportStore.cancelGeneration" 
              class="px-4 py-2 border border-slate-700 hover:border-slate-500 hover:bg-darkBg rounded-xl text-xs font-bold text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
            >
              Cancelar Generación
            </button>
          </div>
        </div>

        <!-- 2. Estado: ÉXITO -->
        <div v-else-if="reportStore.status === 'success'" class="py-4 text-center space-y-5">
          <div class="w-16 h-16 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto shadow-lg shadow-emerald-500/10 animate-in zoom-in-75">
            <CheckCircle2 class="w-8 h-8 stroke-[2.5]" />
          </div>

          <div class="space-y-2">
            <h4 class="text-sm font-bold text-emerald-300 uppercase tracking-wide">
              ¡Reporte Generado con Éxito!
            </h4>
            <p class="text-xs text-slate-300 font-medium">
              El archivo se ha compilado y la descarga se inició automáticamente.
            </p>
            <div v-if="reportStore.downloadedFilename" class="inline-flex items-center gap-2 bg-darkBg border border-darkBorder px-3.5 py-1.5 rounded-xl text-xs font-mono text-cyan-300 shadow-inner">
              <FileSpreadsheet v-if="reportStore.reportFormat === 'excel'" class="w-4 h-4 text-emerald-400" />
              <FileText v-else-if="reportStore.reportFormat === 'pdf'" class="w-4 h-4 text-cyan-400" />
              <FileCode v-else class="w-4 h-4 text-slate-400" />
              <span class="truncate max-w-[240px]">{{ reportStore.downloadedFilename }}</span>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center gap-3 pt-3 border-t border-darkBorder/60">
            <button 
              type="button"
              @click="reportStore.retryDownload"
              class="flex-1 px-4 py-2.5 bg-darkBg border border-slate-700 hover:border-slate-500 hover:text-white rounded-xl text-xs font-bold text-slate-300 transition-all cursor-pointer shadow-sm flex items-center justify-center gap-1.5"
            >
              <Download class="w-4 h-4" />
              <span>Descargar de Nuevo</span>
            </button>
            <button 
              type="button"
              @click="reportStore.closeModal"
              class="flex-1 px-4 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 rounded-xl text-xs font-bold text-white transition-all cursor-pointer shadow-md"
            >
              Listo
            </button>
          </div>
        </div>

        <!-- 3. Estado: ERROR -->
        <div v-else-if="reportStore.status === 'error'" class="py-4 text-center space-y-5">
          <div class="w-16 h-16 rounded-2xl bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400 mx-auto shadow-lg shadow-red-500/10 animate-in zoom-in-75">
            <AlertCircle class="w-8 h-8 stroke-[2.5]" />
          </div>

          <div class="space-y-2">
            <h4 class="text-sm font-bold text-red-300 uppercase tracking-wide">
              Problema al Generar el Reporte
            </h4>
            <p class="text-xs text-red-200/90 font-medium bg-red-500/10 border border-red-500/20 p-3 rounded-xl leading-relaxed max-w-sm mx-auto">
              {{ reportStore.errorMessage || 'No fue posible completar la exportación de los datos.' }}
            </p>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center gap-3 pt-3 border-t border-darkBorder/60">
            <button 
              type="button"
              @click="reportStore.retryDownload"
              class="flex-1 px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-xl text-xs font-bold text-white transition-all cursor-pointer shadow-md flex items-center justify-center gap-1.5"
            >
              <RefreshCw class="w-4 h-4" />
              <span>Reintentar</span>
            </button>
            <button 
              type="button"
              @click="reportStore.closeModal"
              class="flex-1 px-4 py-2.5 bg-darkBg border border-slate-700 hover:border-slate-500 rounded-xl text-xs font-bold text-slate-300 hover:text-white transition-all cursor-pointer"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  X, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  Download, 
  FileSpreadsheet, 
  FileCode, 
  FileText 
} from 'lucide-vue-next'
import { useReportDownloadStore } from '../../stores/reportDownloadStore'

const reportStore = useReportDownloadStore()

const modalHeaderTitle = computed(() => {
  if (reportStore.status === 'generating') return 'Generando Reporte Oficial'
  if (reportStore.status === 'success') return 'Descarga Completada'
  if (reportStore.status === 'error') return 'Error en Generación'
  return 'Centro de Exportaciones'
})

const formatBadgeClass = computed(() => {
  const f = reportStore.reportFormat?.toLowerCase()
  if (f === 'excel') return 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300'
  if (f === 'pdf') return 'bg-cyan-500/20 border-cyan-500/30 text-cyan-300'
  return 'bg-slate-700/40 border-slate-600 text-slate-300'
})
</script>
