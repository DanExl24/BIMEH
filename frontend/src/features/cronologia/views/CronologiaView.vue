<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Row 1: Calendar and Monthly Quick Metrics -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
      <CronologiaActivityCalendar 
        class="lg:col-span-2"
        :selected-month="appStore.selectedMonth"
        :active-date="activeDate"
        :calendar-data="calendarData"
        :loading-calendar="loadingCalendar"
        @select-date="selectDate"
      />

      <CronologiaMonthlyMetrics 
        :loading-calendar="loadingCalendar"
        :avg-monthly-dispo="avgMonthlyDispo"
        :max-dispo-day="maxDispoDay"
        :min-dispo-day="minDispoDay"
      />
    </div>

    <!-- Toggle sub-views: Detailed Daily Report OR Heatmap Matrix -->
    <div class="flex bg-darkBg border border-darkBorder p-1 rounded-2xl w-fit">
      <button 
        type="button"
        @click="activeSubView = 'reporte'"
        class="px-4 py-2.5 text-xs font-bold uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-2 select-none"
        :class="activeSubView === 'reporte' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
      >
        <FileText class="w-4 h-4" />
        <span>Reporte Diario: {{ activeDate }}</span>
      </button>
      <button 
        type="button"
        @click="activeSubView = 'heatmap'"
        class="px-4 py-2.5 text-xs font-bold uppercase tracking-wider rounded-xl transition-all cursor-pointer flex items-center gap-2 select-none"
        :class="activeSubView === 'heatmap' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
      >
        <Layers class="w-4 h-4" />
        <span>Matriz Heatmap Mensual</span>
      </button>
    </div>

    <!-- VIEW 1: DETAILED DAILY REPORT -->
    <CronologiaDailyReportTable 
      v-if="activeSubView === 'reporte'"
      :active-date="activeDate"
      :daily-report="dailyReport"
      :filtered-daily-report="filteredDailyReport"
      v-model:daily-search="dailySearch"
      :loading-daily="loadingDaily"
      :api-base="appStore.apiBase"
    />

    <!-- VIEW 2: HEATMAP MATRIX -->
    <CronologiaMonthlyHeatmapMatrix 
      v-if="activeSubView === 'heatmap'"
      :heatmap-data="heatmapData"
      :filtered-heatmap="filteredHeatmap"
      :paginated-heatmap="paginatedHeatmap"
      v-model:heatmap-search="heatmapSearch"
      :loading-heatmap="loadingHeatmap"
      v-model:heatmap-page="heatmapPage"
      :heatmap-limit="heatmapLimit"
      :max-heatmap-page="maxHeatmapPage"
    />
  </div>
</template>

<script setup lang="ts">
import { FileText, Layers } from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'
import { useCronologiaData } from '../composables/useCronologiaData'

import CronologiaActivityCalendar from '../components/CronologiaActivityCalendar.vue'
import CronologiaMonthlyMetrics from '../components/CronologiaMonthlyMetrics.vue'
import CronologiaDailyReportTable from '../components/CronologiaDailyReportTable.vue'
import CronologiaMonthlyHeatmapMatrix from '../components/CronologiaMonthlyHeatmapMatrix.vue'

const appStore = useAppStore()

const {
  activeSubView,
  activeDate,
  dailySearch,
  heatmapSearch,
  loadingCalendar,
  loadingDaily,
  loadingHeatmap,
  calendarData,
  dailyReport,
  heatmapData,
  heatmapPage,
  heatmapLimit,
  maxHeatmapPage,
  avgMonthlyDispo,
  maxDispoDay,
  minDispoDay,
  filteredDailyReport,
  filteredHeatmap,
  paginatedHeatmap,
  selectDate
} = useCronologiaData()
</script>
