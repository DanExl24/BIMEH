<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Back Button -->
    <div>
      <router-link 
        to="/personal" 
        class="text-xs text-slate-400 font-bold hover:text-cyan-300 inline-flex items-center gap-2 transition-all group py-1 select-none"
      >
        <ArrowLeft class="w-4 h-4 transition-transform group-hover:-translate-x-1" />
        <span>Volver al Buscador de Personal</span>
      </router-link>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24 space-y-3">
      <Loader2 class="w-10 h-10 text-cyan-400 animate-spin" />
      <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Cargando expediente personal...</p>
    </div>

    <!-- Profile content -->
    <div v-else-if="profile" class="space-y-6 min-w-0 max-w-full">
      <!-- 1. Header Info Card -->
      <PersonalHeaderCard 
        :profile="profile" 
        @export="triggerExportModal('personal')" 
      />

      <!-- 2. Statistics Grid -->
      <PersonalKpiGrid :profile="profile" />

      <!-- 3. Chart and Details -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6 min-w-0">
        <!-- Tiempo acumulado subnovedad chart -->
        <PersonalNovedadesChart 
          class="min-w-0"
          :filtered-historial="filteredHistorial"
          :filter-subtitle="filterSubtitle"
          v-model:selected-subnovedad="filtroSubnovedad"
        />

        <!-- Línea de tiempo individual -->
        <PersonalTimeline 
          class="lg:col-span-2 min-w-0"
          v-model:filtro-mes="filtroMes"
          v-model:filtro-dia="filtroDia"
          v-model:filtro-subnovedad="filtroSubnovedad"
          :meses-disponibles="mesesDisponibles"
          :subnovedades-list="subnovedadesList"
          :dias-del-mes="diasDelMes"
          :filtered-historial="filteredHistorial"
        />
      </div>

      <!-- 4. Individual Heatmap and Daily Detail Card -->
      <PersonalHeatmapMatrix 
        :profile="profile"
        :historial="historial"
        :active-months="activeMonths"
        :current-year="currentYear"
        :subnovedades-list="subnovedadesList"
        @export-month="month => triggerExportModal('consolidado_mensual', month)"
      />
    </div>

    <!-- Reusable Export Modal -->
    <ExportModal
      :isOpen="openExportModal"
      :cedula="profile?.cedula"
      :defaultReportType="modalReportType"
      :defaultMonth="modalMonth"
      :availableMonths="activeMonths"
      :subnovedades="subnovedadesList"
      @close="openExportModal = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Loader2 } from 'lucide-vue-next'
import { usePersonalProfile } from '../composables/usePersonalProfile'
import { usePersonalTimelineFilters } from '../composables/usePersonalTimelineFilters'

import PersonalHeaderCard from '../components/PersonalHeaderCard.vue'
import PersonalKpiGrid from '../components/PersonalKpiGrid.vue'
import PersonalNovedadesChart from '../components/PersonalNovedadesChart.vue'
import PersonalTimeline from '../components/PersonalTimeline.vue'
import PersonalHeatmapMatrix from '../components/PersonalHeatmapMatrix.vue'
import ExportModal from '@components/modals/ExportModal.vue'

const route = useRoute()

// Composable de perfil y datos del funcionario
const { loading, profile, historial, activeMonths, currentYear, loadProfile } = usePersonalProfile()

// Composable de filtros de la línea de tiempo
const {
  filtroMes,
  filtroDia,
  filtroSubnovedad,
  mesesDisponibles,
  diasDelMes,
  subnovedadesList,
  filteredHistorial,
  filterSubtitle
} = usePersonalTimelineFilters(historial)

// Modal de exportación
const openExportModal = ref(false)
const modalReportType = ref<'personal' | 'consolidado_mensual' | 'agil'>('personal')
const modalMonth = ref('JULIO')

const triggerExportModal = (tipo: 'personal' | 'consolidado_mensual' | 'agil', defaultMonth?: string) => {
  modalReportType.value = tipo
  if (defaultMonth) {
    modalMonth.value = defaultMonth
  }
  openExportModal.value = true
}

watch(activeMonths, (newMonths) => {
  if (newMonths && newMonths.length > 0 && modalMonth.value && !newMonths.includes(modalMonth.value)) {
    modalMonth.value = newMonths[newMonths.length - 1]
  }
}, { immediate: true })

onMounted(() => {
  const cedula = Number(route.params.cedula)
  if (cedula) {
    loadProfile(cedula)
  }
})
</script>
