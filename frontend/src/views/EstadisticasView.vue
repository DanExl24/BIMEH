<template>
  <div class="space-y-6">
    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-10 h-10 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
      <p class="text-slate-400 text-sm">Analizando estadísticas acumuladas...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Top Section: General Rankings -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Subnovedades Ranking Table -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[400px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Ranking Global de Subnovedades (Total Días Acumulados)
          </h3>
          <div class="flex-1 overflow-y-auto pr-2">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="border-b border-darkBorder text-[10px] text-slate-400 uppercase font-mono">
                  <th class="py-2">Puesto</th>
                  <th class="py-2">Subnovedad</th>
                  <th class="py-2 text-right">Total Días</th>
                </tr>
              </thead>
              <tbody class="text-xs">
                <tr 
                  v-for="(r, index) in rankings?.global_rank" 
                  :key="r.subnovedad"
                  class="border-b border-darkBorder/40 hover:bg-darkBorder/10 transition-colors"
                >
                  <td class="py-2.5 font-bold" :class="index < 3 ? 'text-cyan-400' : 'text-slate-400'">
                    #{{ index + 1 }}
                  </td>
                  <td class="py-2.5 font-semibold text-slate-200 uppercase">{{ r.subnovedad }}</td>
                  <td class="py-2.5 text-right font-mono text-slate-300">{{ r.dias_acumulados }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Personnel with most novelty days Table -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[400px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-amber-500 rounded-sm"></span> Integrantes con Mayor Cantidad de Días en Novedad
          </h3>
          <div class="flex-1 overflow-y-auto pr-2">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="border-b border-darkBorder text-[10px] text-slate-400 uppercase font-mono">
                  <th class="py-2">Cédula</th>
                  <th class="py-2">Nombre</th>
                  <th class="py-2 text-right">Días en Novedad</th>
                </tr>
              </thead>
              <tbody class="text-xs">
                <tr 
                  v-for="p in rankings?.most_novelties_people" 
                  :key="p.cedula"
                  class="border-b border-darkBorder/40 hover:bg-darkBorder/10 transition-colors"
                >
                  <td class="py-2.5 font-mono text-slate-400">{{ p.cedula }}</td>
                  <td class="py-2.5 uppercase font-bold text-slate-200 hover:text-cyan-400">
                    <router-link :to="`/personal/${p.cedula}`">{{ p.nombre }}</router-link>
                  </td>
                  <td class="py-2.5 text-right font-mono font-bold text-amber-500">{{ p.dias_novedad }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Lower Section: Monthly Distribution Chart -->
      <div class="grid grid-cols-1 gap-6">
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[420px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-teal-500 rounded-sm"></span> Distribución de Novedades del Mes Seleccionado
          </h3>
          <div class="flex-1 min-h-0">
            <div ref="monthlyNovedadesDom" class="chart-container"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import { useAppStore } from '../stores/appStore'
import * as echarts from 'echarts'

const appStore = useAppStore()

interface RankingItem {
  subnovedad: string
  dias_acumulados: number
}

interface PersonnelRankingItem {
  cedula: number
  nombre: string
  dias_novedad: number
}

interface RankingsData {
  global_rank: RankingItem[]
  most_novelties_people: PersonnelRankingItem[]
}

const loading = ref(true)
const rankings = ref<RankingsData | null>(null)

const monthlyNovedadesDom = ref<HTMLDivElement | null>(null)
let monthlyChart: echarts.ECharts | null = null

const loadStats = async () => {
  loading.value = true
  try {
    const res = await fetch(`${appStore.apiBase}/api/stats/ranking`)
    if (res.ok) {
      rankings.value = await res.json()
    }
    
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
  if (!monthlyNovedadesDom.value) return
  
  if (monthlyChart) {
    monthlyChart.dispose()
  }
  
  monthlyChart = echarts.init(monthlyNovedadesDom.value)
  
  try {
    const res = await fetch(`${appStore.apiBase}/api/dashboard/novedades-frecuentes?mes=${appStore.selectedMonth}`)
    if (res.ok) {
      const data = await res.json()
      
      const names = data.map((d: any) => d.novedad)
      const values = data.map((d: any) => d.cantidad)
      
      monthlyChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: '#151d30',
          borderColor: '#1f2b45',
          textStyle: { color: '#f1f5f9' }
        },
        grid: { top: 30, right: 30, bottom: 40, left: 100 },
        xAxis: {
          type: 'category',
          data: names,
          axisLine: { lineStyle: { color: '#1f2b45' } },
          axisLabel: { color: '#94a3b8', rotate: 15, fontSize: 10 },
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
          axisLine: { lineStyle: { color: '#1f2b45' } },
          axisLabel: { color: '#94a3b8' },
          splitLine: { lineStyle: { color: '#1f2b45' } }
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
              borderRadius: [4, 4, 0, 0]
            },
            label: {
              show: true,
              position: 'top',
              color: '#f1f5f9',
              fontSize: 10
            }
          }
        ]
      })
    }
  } catch (error) {
    console.error('Error fetching monthly charts data:', error)
  }
}

const handleResize = () => {
  monthlyChart?.resize()
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  monthlyChart?.dispose()
})

// Reload chart when month changes
watch(() => appStore.selectedMonth, () => {
  initMonthlyChart()
})
</script>
