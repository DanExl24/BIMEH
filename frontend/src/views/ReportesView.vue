<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Header -->
    <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 border border-darkBorder shadow-xl">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-6 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-sm"></div>
          <h2 class="text-base sm:text-lg font-black text-slate-100 uppercase tracking-tight">
            Centro de Descargas & Reportes Oficiales
          </h2>
        </div>
        <p class="text-xs text-slate-400 mt-1.5 font-medium leading-relaxed">
          Exporta la información operacional de la unidad en formatos estandarizados Excel, CSV y PDF de alta fidelidad.
        </p>
      </div>
      <div class="flex items-center gap-2 text-xs bg-darkBg px-4 py-2 rounded-xl border border-darkBorder self-start md:self-auto shadow-sm">
        <span class="text-slate-400">Motor de Base de Datos:</span>
        <span class="font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">PostgreSQL</span>
      </div>
    </div>

    <!-- Reports Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6">
      <!-- Card 1: Base de Datos de Personal -->
      <ReportDirectDownloadCard 
        title="Base de Datos de Personal"
        description="Listado general de todo el personal registrado en la unidad, incluyendo su cédula, nombres completos, estado actual (activo/retirado) y fecha de retiro si aplica."
        :excel-url="`${appStore.apiBase}/api/exportar/excel?tipo=personal_db`"
        :csv-url="`${appStore.apiBase}/api/exportar/csv?tipo=personal_db`"
        :pdf-url="`${appStore.apiBase}/api/exportar/pdf?tipo=personal_db`"
        icon-bg-class="bg-cyan-500/15 border border-cyan-500/30 text-cyan-400"
      >
        <template #icon>
          <Users class="w-6 h-6 stroke-[2]" />
        </template>
      </ReportDirectDownloadCard>

      <!-- Card 2: Catálogo de Subnovedades -->
      <ReportDirectDownloadCard 
        title="Catálogo de Novedades"
        description="Exporta el diccionario general de novedades y clasificaciones configuradas en el sistema, ideal para auditorías de nomenclaturas operacionales."
        :excel-url="`${appStore.apiBase}/api/exportar/excel?tipo=subnovedades`"
        :csv-url="`${appStore.apiBase}/api/exportar/csv?tipo=subnovedades`"
        :pdf-url="`${appStore.apiBase}/api/exportar/pdf?tipo=subnovedades`"
        icon-bg-class="bg-purple-500/15 border border-purple-500/30 text-purple-400"
      >
        <template #icon>
          <BookOpen class="w-6 h-6 stroke-[2]" />
        </template>
      </ReportDirectDownloadCard>

      <!-- Card 3: Consolidado Diario Mensual (Heatmap) -->
      <ReportConsolidadoMensualForm 
        :api-base="appStore.apiBase"
        :active-months="activeMonths"
        :sorted-dates="sortedDates"
        :month-to-number="MONTH_TO_NUMBER"
        :default-month="defaultMonth"
      />

      <!-- Card 4: Reporte Detallado de Personal -->
      <ReportResumenAnualForm 
        :api-base="appStore.apiBase"
        :active-months="activeMonths"
        :sorted-dates="sortedDates"
        :month-to-number="MONTH_TO_NUMBER"
        :default-month="defaultMonth"
      />

      <!-- Card 5: Exportación Ágil de Novedades -->
      <ReportIndividualExpedienteForm 
        :api-base="appStore.apiBase"
        :active-months="activeMonths"
        :sorted-dates="sortedDates"
        :month-to-number="MONTH_TO_NUMBER"
        :default-month="defaultMonth"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Users, BookOpen } from 'lucide-vue-next'
import { useAppStore } from '../stores/appStore'
import { useDateStore } from '../stores/dateStore'
import { MONTH_TO_NUMBER } from '../utils/date'

import ReportDirectDownloadCard from '../components/reportes/ReportDirectDownloadCard.vue'
import ReportConsolidadoMensualForm from '../components/reportes/ReportConsolidadoMensualForm.vue'
import ReportResumenAnualForm from '../components/reportes/ReportResumenAnualForm.vue'
import ReportIndividualExpedienteForm from '../components/reportes/ReportIndividualExpedienteForm.vue'

const appStore = useAppStore()
const dateStore = useDateStore()

const activeMonths = computed(() => dateStore.availableMonths)
const defaultMonth = computed(() => dateStore.selectedMonth || dateStore.latestMonth || '')
const sortedDates = computed(() => dateStore.sortedDatesDesc)

onMounted(() => {
  if (dateStore.availableDates.length === 0) {
    dateStore.fetchAvailableDates()
  }
})
</script>


