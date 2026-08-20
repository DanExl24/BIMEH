<template>
  <div class="space-y-8 min-w-0 max-w-full pb-10">
    <!-- Header Card -->
    <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col md:flex-row md:items-center justify-between gap-4 border border-darkBorder shadow-xl">
      <div>
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-6 bg-gradient-to-b from-cyan-400 to-blue-600 rounded-sm"></div>
          <h2 class="text-base sm:text-lg font-black text-slate-100 uppercase tracking-tight">
            Centro de Descargas & Reportes Oficiales
          </h2>
        </div>
        <p class="text-xs text-slate-400 mt-1.5 font-medium leading-relaxed">
          Exporta la información operacional de la unidad en formatos estandarizados Excel (.xlsx), PDF vectorial de alta fidelidad y CSV (.csv).
        </p>
      </div>
      <div class="flex items-center gap-2 text-xs bg-darkBg px-4 py-2 rounded-xl border border-darkBorder self-start md:self-auto shadow-sm">
        <span class="text-slate-400">Motor de Base de Datos:</span>
        <span class="font-mono text-cyan-400 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">PostgreSQL</span>
      </div>
    </div>

    <!-- SECCIÓN 1: ACCESO RÁPIDO -->
    <section class="space-y-3">
      <div class="flex items-center gap-2 px-1">
        <Zap class="w-4 h-4 text-cyan-400" />
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">
          Descarga Inmediata del Mes Activo
        </h3>
      </div>
      <ReportDirectDownloadCard 
        :selected-month="selectedMonth" 
        :api-base="appStore.apiBase" 
      />
    </section>

    <!-- SECCIÓN 2: REPORTES OPERACIONALES Y DE FUERZA -->
    <section class="space-y-4">
      <div class="flex items-center gap-2 px-1">
        <FileSpreadsheet class="w-4 h-4 text-emerald-400" />
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">
          Reportes Operacionales & Consolidación de Fuerza
        </h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6">
        <!-- 1. Consolidado Mensual (Matriz Heatmap) -->
        <ReportConsolidadoMensualForm 
          :api-base="appStore.apiBase" 
          :active-months="activeMonths"
          :default-month="selectedMonth" 
        />

        <!-- 2. Exportación Ágil de Novedades (Rangos Condensados) -->
        <ReportAgilForm 
          :api-base="appStore.apiBase" 
          :active-months="activeMonths"
          :sorted-dates="sortedDates"
          :default-month="selectedMonth"
        />

        <!-- 3. Reporte Detallado de Personal (Parte Oficial Completo - Span 2) -->
        <div class="md:col-span-2">
          <ReportDetalladoForm 
            :api-base="appStore.apiBase" 
            :active-months="activeMonths"
            :sorted-dates="sortedDates"
            :default-month="selectedMonth"
          />
        </div>
      </div>
    </section>

    <!-- SECCIÓN 3: EXPEDIENTES, PERSONAL Y CATÁLOGOS -->
    <section class="space-y-4">
      <div class="flex items-center gap-2 px-1">
        <Users class="w-4 h-4 text-purple-400" />
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300">
          Expedientes Individuales & Catálogos de Base de Datos
        </h3>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
        <!-- 4. Expediente Individual por Cédula -->
        <ReportIndividualExpedienteForm 
          :api-base="appStore.apiBase" 
          :active-months="activeMonths"
        />

        <!-- 5. Base de Datos de Personal de la Unidad -->
        <ReportCatalogoCard 
          title="Base de Datos de Personal"
          description="Listado maestro de todo el personal de la unidad (cédulas, nombres, estado y fecha de retiro)."
          :excel-url="`${appStore.apiBase}/api/exportar/excel?tipo=personal_db`"
          :pdf-url="`${appStore.apiBase}/api/exportar/pdf?tipo=personal_db`"
          :csv-url="`${appStore.apiBase}/api/exportar/csv?tipo=personal_db`"
          icon-bg-class="bg-cyan-500/15 border border-cyan-500/30 text-cyan-400"
        >
          <template #icon>
            <Users class="w-5 h-5 stroke-[2]" />
          </template>
        </ReportCatalogoCard>

        <!-- 6. Catálogo General de Novedades -->
        <ReportCatalogoCard 
          title="Catálogo de Novedades"
          description="Diccionario oficial de subnovedades y clasificaciones configuradas en el sistema para auditoría."
          :excel-url="`${appStore.apiBase}/api/exportar/excel?tipo=subnovedades`"
          :pdf-url="`${appStore.apiBase}/api/exportar/pdf?tipo=subnovedades`"
          :csv-url="`${appStore.apiBase}/api/exportar/csv?tipo=subnovedades`"
          icon-bg-class="bg-purple-500/15 border border-purple-500/30 text-purple-400"
        >
          <template #icon>
            <BookOpen class="w-5 h-5 stroke-[2]" />
          </template>
        </ReportCatalogoCard>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Zap, FileSpreadsheet, Users, BookOpen } from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'
import { useDateStore } from '@stores/dateStore'

import ReportDirectDownloadCard from '../components/ReportDirectDownloadCard.vue'
import ReportConsolidadoMensualForm from '../components/ReportConsolidadoMensualForm.vue'
import ReportAgilForm from '../components/ReportAgilForm.vue'
import ReportDetalladoForm from '../components/ReportDetalladoForm.vue'
import ReportIndividualExpedienteForm from '../components/ReportIndividualExpedienteForm.vue'
import ReportCatalogoCard from '../components/ReportCatalogoCard.vue'

const appStore = useAppStore()
const dateStore = useDateStore()

const activeMonths = computed(() => dateStore.availableMonths)
const selectedMonth = computed(() => dateStore.selectedMonth || dateStore.latestMonth || 'MAYO')
const sortedDates = computed(() => dateStore.sortedDatesDesc)

onMounted(() => {
  if (dateStore.availableDates.length === 0) {
    dateStore.fetchAvailableDates()
  }
})
</script>
