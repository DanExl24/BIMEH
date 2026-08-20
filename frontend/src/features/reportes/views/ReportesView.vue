<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Header Card -->
    <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 border border-darkBorder shadow-xl">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-6 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-sm"></div>
          <h3 class="text-base sm:text-lg font-black text-slate-100 uppercase tracking-tight">
            Centro de Reportes & Exportación Oficial
          </h3>
        </div>
        <p class="text-xs text-slate-400 mt-1.5 font-medium leading-relaxed">
          Genera y descarga informes operacionales en formatos Excel (.xlsx) y PDF de alta fidelidad.
        </p>
      </div>
    </div>

    <!-- Quick Download Card for Currently Selected Month -->
    <ReportDirectDownloadCard 
      :selected-month="selectedMonth" 
      :api-base="appStore.apiBase" 
    />

    <!-- Forms Grid: Specific Reports -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6">
      <!-- 1. Consolidado Mensual -->
      <ReportConsolidadoMensualForm 
        :api-base="appStore.apiBase" 
        :default-month="selectedMonth" 
      />

      <!-- 2. Resumen Anual -->
      <ReportResumenAnualForm 
        :api-base="appStore.apiBase" 
      />

      <!-- 3. Expediente Individual -->
      <ReportIndividualExpedienteForm 
        :api-base="appStore.apiBase" 
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@stores/appStore'
import { useDateStore } from '@stores/dateStore'

import ReportDirectDownloadCard from '../components/ReportDirectDownloadCard.vue'
import ReportConsolidadoMensualForm from '../components/ReportConsolidadoMensualForm.vue'
import ReportResumenAnualForm from '../components/ReportResumenAnualForm.vue'
import ReportIndividualExpedienteForm from '../components/ReportIndividualExpedienteForm.vue'

const appStore = useAppStore()
const dateStore = useDateStore()

const selectedMonth = computed(() => {
  return dateStore.selectedMonth || dateStore.latestMonth || 'MAYO'
})
</script>
