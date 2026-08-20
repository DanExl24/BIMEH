<template>
  <div class="space-y-6">
    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24 space-y-3">
      <Loader2 class="w-10 h-10 text-cyan-400 animate-spin" />
      <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Analizando estadísticas acumuladas...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Top Section: General Rankings -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 sm:gap-6">
        <!-- 1. Subnovedades Ranking Card -->
        <div class="glass-panel p-5 sm:p-6 rounded-3xl flex flex-col h-[460px] border border-darkBorder shadow-xl">
          <div class="flex items-center justify-between gap-2 mb-4 border-b border-darkBorder/60 pb-3">
            <div class="flex items-center gap-2">
              <BarChart2 class="w-5 h-5 text-cyan-400" />
              <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
                Ranking Global de Subnovedades
              </h3>
            </div>
            <span class="text-xs text-slate-400 font-semibold uppercase">Total Días</span>
          </div>

          <div class="flex-1 overflow-y-auto pr-2 space-y-3">
            <div 
              v-for="(r, index) in rankings?.global_rank" 
              :key="r.subnovedad"
              class="p-3 bg-darkBg/60 rounded-2xl border border-darkBorder/60 hover:border-slate-700 transition-all space-y-2 group"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2.5 min-w-0">
                  <span 
                    class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-black shrink-0 shadow-sm"
                    :class="index === 0 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 
                            index === 1 ? 'bg-slate-300/20 text-slate-200 border border-slate-400/30' : 
                            index === 2 ? 'bg-amber-700/20 text-amber-400 border border-amber-600/30' : 'bg-slate-800 text-slate-400'"
                  >
                    {{ index + 1 }}
                  </span>
                  <span class="text-xs font-bold text-slate-100 uppercase truncate">{{ r.subnovedad }}</span>
                </div>
                <span class="text-xs font-mono font-bold text-cyan-300 bg-cyan-500/10 px-2.5 py-0.5 rounded-md border border-cyan-500/20 shrink-0">
                  {{ r.dias_acumulados }} d
                </span>
              </div>
              
              <!-- Relative Progress Bar -->
              <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div 
                  class="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full transition-all duration-500"
                  :style="{ width: `${rankings?.global_rank?.[0]?.dias_acumulados ? (r.dias_acumulados / rankings.global_rank[0].dias_acumulados) * 100 : 0}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Integrantes con mayor cantidad de días en novedad -->
        <div class="glass-panel p-5 sm:p-6 rounded-3xl flex flex-col h-[460px] border border-darkBorder shadow-xl">
          <div class="flex items-center justify-between gap-2 mb-4 border-b border-darkBorder/60 pb-3">
            <div class="flex items-center gap-2">
              <Users class="w-5 h-5 text-amber-400" />
              <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
                Mayor Tiempo Acumulado en Novedad
              </h3>
            </div>
            <span class="text-xs text-slate-400 font-semibold uppercase">Días</span>
          </div>

          <div class="flex-1 overflow-y-auto pr-2 space-y-3">
            <div 
              v-for="(p, index) in rankings?.most_novelties_people" 
              :key="p.cedula"
              class="p-3 bg-darkBg/60 rounded-2xl border border-darkBorder/60 hover:border-slate-700 transition-all flex items-center justify-between gap-3 group"
            >
              <div class="flex items-center gap-3 min-w-0">
                <span 
                  class="w-6 h-6 rounded-lg flex items-center justify-center text-xs font-black shrink-0 shadow-sm"
                  :class="index === 0 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 
                          index === 1 ? 'bg-slate-300/20 text-slate-200 border border-slate-400/30' : 
                          index === 2 ? 'bg-amber-700/20 text-amber-400 border border-amber-600/30' : 'bg-slate-800 text-slate-400'"
                >
                  {{ index + 1 }}
                </span>
                <div class="min-w-0">
                  <router-link 
                    :to="`/personal/${p.cedula}`" 
                    class="text-xs font-bold text-slate-100 hover:text-cyan-300 uppercase truncate block transition-colors"
                  >
                    {{ p.nombre }}
                  </router-link>
                  <span class="text-xs font-mono text-slate-400">C.C. {{ p.cedula }}</span>
                </div>
              </div>

              <div class="flex items-center gap-2 shrink-0">
                <span class="text-xs font-mono font-bold text-amber-400 bg-amber-500/15 px-2.5 py-1 rounded-lg border border-amber-500/30">
                  {{ p.dias_novedad }} días
                </span>
                <router-link 
                  :to="`/personal/${p.cedula}`" 
                  class="p-1 text-slate-400 hover:text-cyan-300 transition-colors"
                  title="Ver Expediente"
                >
                  <ArrowRight class="w-4 h-4" />
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Lower Section: Monthly Distribution Chart -->
      <div class="glass-panel p-5 sm:p-7 rounded-3xl flex flex-col h-[440px] border border-darkBorder shadow-xl">
        <div class="flex items-center justify-between gap-2 mb-4 border-b border-darkBorder/60 pb-3">
          <div class="flex items-center gap-2">
            <TrendingUp class="w-5 h-5 text-teal-400" />
            <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
              Distribución de Novedades del Mes ({{ appStore.selectedMonth }})
            </h3>
          </div>
        </div>
        <div class="flex-1 min-h-0">
          <div ref="monthlyNovedadesDom" class="chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { 
  BarChart2, 
  Users, 
  TrendingUp, 
  ArrowRight, 
  Loader2 
} from 'lucide-vue-next'
import { useAppStore } from '../stores/appStore'
import * as echarts from 'echarts'
import { fetchStatsRanking, fetchNovedadesFrecuentes } from '../services/api'
import type { RankingsData } from '../types'
import { useECharts } from '../composables/useECharts'

const appStore = useAppStore()

const loading = ref(true)
const rankings = ref<RankingsData | null>(null)

const { chartDom: monthlyNovedadesDom, setOption: setMonthlyOption } = useECharts()

const loadStats = async () => {
  loading.value = true
  try {
    rankings.value = await fetchStatsRanking()
    loading.value = false
    
    setTimeout(() => {
      initMonthlyChart()
    }, 50)
  } catch (error) {
    console.error('Error fetching statistics rankings:', error)
    loading.value = false
  }
}

const initMonthlyChart = async () => {
  try {
    const data = await fetchNovedadesFrecuentes(appStore.selectedMonth)
    
    const names = data.map((d: { novedad: string }) => d.novedad)
    const values = data.map((d: { cantidad: number }) => d.cantidad)
    
    setMonthlyOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#121827',
        borderColor: '#1e293b',
        textStyle: { color: '#f8fafc', fontSize: 12 }
      },
      grid: { top: 30, right: 30, bottom: 50, left: 60, containLabel: true },
      xAxis: {
        type: 'category',
        data: names,
        axisLine: { lineStyle: { color: '#1e293b' } },
        axisLabel: { color: '#94a3b8', rotate: 20, fontSize: 11, interval: 0 },
        splitLine: { show: false }
      },
      yAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#1e293b' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        splitLine: { lineStyle: { color: '#1e293b' } }
      },
      series: [
        {
          type: 'bar',
          data: values,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#06b6d4' },
              { offset: 1, color: '#14b8a6' }
            ]),
            borderRadius: [6, 6, 0, 0]
          },
          label: {
            show: true,
            position: 'top',
            color: '#f8fafc',
            fontSize: 11,
            fontWeight: 'bold'
          }
        }
      ]
    })
  } catch (error) {
    console.error('Error fetching monthly charts data:', error)
  }
}

onMounted(() => {
  loadStats()
})

watch(() => appStore.selectedMonth, () => {
  initMonthlyChart()
})
</script>

