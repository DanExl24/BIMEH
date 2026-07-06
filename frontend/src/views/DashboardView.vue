<template>
  <div class="space-y-6">
    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-12 h-12 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
      <p class="text-slate-400 text-sm font-medium">Cargando datos operacionales...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- 1. KPIs Section -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <!-- Tarjeta Fecha -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">📅 Fecha Reporte</span>
          <div class="mt-2">
            <span class="text-2xl font-bold font-mono text-cyan-400">{{ kpis?.fecha }}</span>
          </div>
          <span class="text-[10px] text-slate-500 mt-2 block">Día de operaciones</span>
        </div>

        <!-- Tarjeta Personal Registrado -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">👥 Personal Registrado</span>
          <div class="mt-2">
            <span class="text-3xl font-extrabold text-slate-100">{{ kpis?.total_personal }}</span>
          </div>
          <span class="text-[10px] text-slate-500 mt-2 block">Total en reportes</span>
        </div>

        <!-- Tarjeta Disponibles -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">✅ Disponibles</span>
          <div class="mt-2">
            <span class="text-3xl font-extrabold text-emerald-400">{{ kpis?.disponibles }}</span>
          </div>
          <span class="text-[10px] text-emerald-400/80 mt-2 block">En servicio activo</span>
        </div>

        <!-- Tarjeta En Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">🏥 En Novedades</span>
          <div class="mt-2">
            <span class="text-3xl font-extrabold text-amber-500">{{ kpis?.novedades }}</span>
          </div>
          <span class="text-[10px] text-amber-500/80 mt-2 block">Fuera de disponibilidad</span>
        </div>

        <!-- Tarjeta Disponibilidad % -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">📈 Disponibilidad</span>
          <div class="mt-2">
            <span class="text-3xl font-extrabold text-cyan-400">{{ kpis?.disponibilidad }}%</span>
          </div>
          <!-- Bar indicator -->
          <div class="w-full bg-darkBg/60 rounded-full h-1.5 mt-2 overflow-hidden">
            <div class="bg-cyan-500 h-full rounded-full transition-all duration-500" :style="{ width: `${kpis?.disponibilidad}%` }"></div>
          </div>
        </div>
      </div>

      <!-- 2. Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Evolución diaria Line Chart -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-2 flex flex-col h-[400px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Evolución de Disponibilidad Diaria {{ appStore.selectedDashboardMonth ? `(${appStore.selectedDashboardMonth})` : '(Anual)' }}
          </h3>
          <div class="flex-1 min-h-0">
            <div ref="evolutionChartDom" class="chart-container"></div>
          </div>
        </div>

        <!-- Novedades más frecuentes Bar Chart -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[400px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-amber-500 rounded-sm"></span> Novedades más Frecuentes {{ appStore.selectedDashboardMonth ? `(${appStore.selectedDashboardMonth})` : '(Anual)' }}
          </h3>
          <div class="flex-1 min-h-0">
            <div ref="novedadesChartDom" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 3. Lower Section: Distribution and Changes -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Personal por estado horizontal bars -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[420px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-teal-500 rounded-sm"></span> Distribución del Personal por Estado
          </h3>
          <div class="flex-1 min-h-0">
            <div ref="distribucionChartDom" class="chart-container"></div>
          </div>
        </div>

        <!-- Cambios respecto a ayer list -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-2 flex flex-col h-[420px]">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <span class="w-2 h-4 bg-purple-500 rounded-sm"></span> Cambios de Estado {{ appStore.selectedDashboardMonth ? `(${appStore.selectedDashboardMonth})` : 'del Año' }}
            </h3>
            <span class="text-xs bg-purple-500/10 text-purple-400 font-semibold px-2 py-1 rounded-md border border-purple-500/20">
              {{ kpis?.cambios_vs_ayer }} Cambios detectados
            </span>
          </div>

          <!-- Tabs for changes -->
          <div class="flex border-b border-darkBorder mb-4">
            <button 
              @click="activeChangeTab = 'entraron'"
              class="px-4 py-2 text-xs font-semibold uppercase tracking-wider transition-colors border-b-2"
              :class="activeChangeTab === 'entraron' ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'"
            >
              Entraron Novedades ({{ cambios?.entraron_novedades.length || 0 }})
            </button>
            <button 
              @click="activeChangeTab = 'volvieron'"
              class="px-4 py-2 text-xs font-semibold uppercase tracking-wider transition-colors border-b-2"
              :class="activeChangeTab === 'volvieron' ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'"
            >
              Volvieron Disponibles ({{ cambios?.volvieron_disponibles.length || 0 }})
            </button>
            <button 
              @click="activeChangeTab = 'otros'"
              class="px-4 py-2 text-xs font-semibold uppercase tracking-wider transition-colors border-b-2"
              :class="activeChangeTab === 'otros' ? 'border-cyan-500 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'"
            >
              Otros Cambios ({{ cambios?.otros_cambios.length || 0 }})
            </button>
          </div>

          <!-- Changes list container -->
          <div class="flex-1 overflow-y-auto pr-2">
            <!-- Entraron Novedades -->
            <div v-if="activeChangeTab === 'entraron'" class="space-y-2">
              <div v-if="!cambios?.entraron_novedades.length" class="text-center py-10 text-slate-500 text-sm">
                Ningún integrante entró a novedades en este período.
              </div>
              <div 
                v-for="c in cambios?.entraron_novedades" 
                :key="c.cedula"
                class="flex items-center justify-between p-3 rounded-xl bg-darkBg/40 border border-darkBorder/40 hover:border-darkBorder"
              >
                <div>
                  <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-200 hover:text-cyan-400 block uppercase">
                    {{ c.nombre }}
                  </router-link>
                  <span class="text-[10px] text-slate-500 font-mono">C.C. {{ c.cedula }}</span>
                </div>
                <div class="flex items-center gap-2 text-xs">
                  <span class="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/10 font-medium">
                    {{ c.novedad_anterior }}
                  </span>
                  <span class="text-slate-500">&rarr;</span>
                  <span class="text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/10 font-medium">
                    {{ c.novedad_nueva }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Volvieron Disponibles -->
            <div v-if="activeChangeTab === 'volvieron'" class="space-y-2">
              <div v-if="!cambios?.volvieron_disponibles.length" class="text-center py-10 text-slate-500 text-sm">
                Ningún integrante volvió a disponible en este período.
              </div>
              <div 
                v-for="c in cambios?.volvieron_disponibles" 
                :key="c.cedula"
                class="flex items-center justify-between p-3 rounded-xl bg-darkBg/40 border border-darkBorder/40 hover:border-darkBorder"
              >
                <div>
                  <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-200 hover:text-cyan-400 block uppercase">
                    {{ c.nombre }}
                  </router-link>
                  <span class="text-[10px] text-slate-500 font-mono">C.C. {{ c.cedula }}</span>
                </div>
                <div class="flex items-center gap-2 text-xs">
                  <span class="text-amber-500 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/10 font-medium">
                    {{ c.novedad_anterior }}
                  </span>
                  <span class="text-slate-500">&rarr;</span>
                  <span class="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/10 font-medium">
                    {{ c.novedad_nueva }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Otros Cambios -->
            <div v-if="activeChangeTab === 'otros'" class="space-y-2">
              <div v-if="!cambios?.otros_cambios.length" class="text-center py-10 text-slate-500 text-sm">
                Ningún otro cambio detectado en este período.
              </div>
              <div 
                v-for="c in cambios?.otros_cambios" 
                :key="c.cedula"
                class="flex items-center justify-between p-3 rounded-xl bg-darkBg/40 border border-darkBorder/40 hover:border-darkBorder"
              >
                <div>
                  <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-200 hover:text-cyan-400 block uppercase">
                    {{ c.nombre }}
                  </router-link>
                  <span class="text-[10px] text-slate-500 font-mono">C.C. {{ c.cedula }}</span>
                </div>
                <div class="flex items-center gap-2 text-xs">
                  <span class="text-slate-400 bg-slate-500/10 px-2 py-0.5 rounded border border-slate-500/10">
                    {{ c.novedad_anterior }}
                  </span>
                  <span class="text-slate-500">&rarr;</span>
                  <span class="text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/10 font-medium">
                    {{ c.novedad_nueva }}
                  </span>
                </div>
              </div>
            </div>
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

interface KPI {
  fecha: string
  total_personal: number
  disponibles: number
  novedades: number
  disponibilidad: number
  cambios_vs_ayer: number
}

interface Cambio {
  cedula: number
  nombre: string
  novedad_anterior: string
  novedad_nueva: string
}

interface CambiosData {
  entraron_novedades: Cambio[]
  volvieron_disponibles: Cambio[]
  otros_cambios: Cambio[]
}

const loading = ref(true)
const kpis = ref<KPI | null>(null)
const cambios = ref<CambiosData | null>(null)
const activeChangeTab = ref<'entraron' | 'volvieron' | 'otros'>('entraron')

// Chart DOM elements
const evolutionChartDom = ref<HTMLDivElement | null>(null)
const novedadesChartDom = ref<HTMLDivElement | null>(null)
const distribucionChartDom = ref<HTMLDivElement | null>(null)

// Chart instances
let evolutionChart: echarts.ECharts | null = null
let novedadesChart: echarts.ECharts | null = null
let distribucionChart: echarts.ECharts | null = null

// Fetch API
const loadDashboardData = async () => {
  loading.value = true
  try {
    const apiBase = appStore.apiBase
    const mes = appStore.selectedDashboardMonth
    const dia = appStore.selectedDashboardDay
    
    // Fetch KPIs
    const kpisResponse = await fetch(`${apiBase}/api/dashboard/kpis?mes=${mes}&dia=${dia}`)
    if (kpisResponse.ok) {
      kpis.value = await kpisResponse.json()
    }
    
    // Fetch Cambios
    const cambiosResponse = await fetch(`${apiBase}/api/dashboard/cambios?mes=${mes}&dia=${dia}`)
    if (cambiosResponse.ok) {
      cambios.value = await cambiosResponse.json()
    }
    
    loading.value = false
    
    // Render charts after DOM updates
    setTimeout(() => {
      initEvolutionChart()
      initNovedadesChart()
      initDistribucionChart()
    }, 50)
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    loading.value = false
  }
}

// Chart Initializations
const initEvolutionChart = async () => {
  if (!evolutionChartDom.value) return
  
  if (evolutionChart) {
    evolutionChart.dispose()
  }
  
  evolutionChart = echarts.init(evolutionChartDom.value)
  
  // Fetch data
  try {
    const mes = appStore.selectedDashboardMonth
    const dia = appStore.selectedDashboardDay
    const res = await fetch(`${appStore.apiBase}/api/dashboard/evolucion?mes=${mes}&dia=${dia}`)
    if (res.ok) {
      const data = await res.json()
      
      const dates = data.map((d: any) => d.fecha)
      const disponibilidades = data.map((d: any) => d.disponibilidad)
      const disponibles = data.map((d: any) => d.disponibles)
      
      evolutionChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'line' },
          backgroundColor: '#151d30',
          borderColor: '#1f2b45',
          textStyle: { color: '#f1f5f9' }
        },
        grid: { top: 30, right: 20, bottom: 40, left: 50 },
        xAxis: {
          type: 'category',
          data: dates,
          axisLine: { lineStyle: { color: '#1f2b45' } },
          axisLabel: { color: '#94a3b8', fontSize: 10, rotate: 30 },
          splitLine: { show: false }
        },
        yAxis: [
          {
            type: 'value',
            name: 'Disp. %',
            min: 0,
            max: 100,
            axisLabel: { color: '#94a3b8', formatter: '{value}%' },
            splitLine: { lineStyle: { color: '#1f2b45' } }
          },
          {
            type: 'value',
            name: 'Disponibles',
            axisLabel: { color: '#94a3b8' },
            splitLine: { show: false }
          }
        ],
        series: [
          {
            name: 'Disponibilidad %',
            type: 'line',
            data: disponibilidades,
            smooth: true,
            lineStyle: { width: 3, color: '#06b6d4' },
            itemStyle: { color: '#06b6d4' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(6, 182, 212, 0.25)' },
                { offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
              ])
            }
          },
          {
            name: 'Pers. Disponible',
            type: 'bar',
            yAxisIndex: 1,
            data: disponibles,
            itemStyle: { color: 'rgba(16, 185, 129, 0.2)' }
          }
        ]
      })
    }
  } catch (error) {
    console.error('Error fetching evolution data:', error)
  }
}

const initNovedadesChart = async () => {
  if (!novedadesChartDom.value) return
  
  if (novedadesChart) {
    novedadesChart.dispose()
  }
  
  novedadesChart = echarts.init(novedadesChartDom.value)
  
  try {
    const mes = appStore.selectedDashboardMonth
    const dia = appStore.selectedDashboardDay
    const res = await fetch(`${appStore.apiBase}/api/dashboard/novedades-frecuentes?mes=${mes}&dia=${dia}`)
    if (res.ok) {
      const data = await res.json()
      
      const names = data.slice(0, 5).map((d: any) => d.novedad)
      const values = data.slice(0, 5).map((d: any) => d.cantidad)
      
      novedadesChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: '#151d30',
          borderColor: '#1f2b45',
          textStyle: { color: '#f1f5f9' }
        },
        grid: { top: 20, right: 10, bottom: 30, left: 80 },
        xAxis: {
          type: 'value',
          axisLine: { lineStyle: { color: '#1f2b45' } },
          axisLabel: { color: '#94a3b8' },
          splitLine: { lineStyle: { color: '#1f2b45' } }
        },
        yAxis: {
          type: 'category',
          data: names.reverse(),
          axisLine: { lineStyle: { color: '#1f2b45' } },
          axisLabel: { color: '#f1f5f9', fontSize: 10 }
        },
        series: [
          {
            type: 'bar',
            data: values.reverse(),
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#f59e0b' },
                { offset: 1, color: '#ef4444' }
              ]),
              borderRadius: [0, 4, 4, 0]
            },
            label: {
              show: true,
              position: 'right',
              color: '#f1f5f9',
              fontSize: 10
            }
          }
        ]
      })
    }
  } catch (error) {
    console.error('Error fetching frequency data:', error)
  }
}

const initDistribucionChart = async () => {
  if (!distribucionChartDom.value) return
  
  if (distribucionChart) {
    distribucionChart.dispose()
  }
  
  distribucionChart = echarts.init(distribucionChartDom.value)
  
  try {
    const mes = appStore.selectedDashboardMonth
    const dia = appStore.selectedDashboardDay
    const res = await fetch(`${appStore.apiBase}/api/dashboard/distribucion?mes=${mes}&dia=${dia}`)
    if (res.ok) {
      const data = await res.json()
      
      // Format top 6 + other
      const sorted = [...data].sort((a: any, b: any) => b.cantidad - a.cantidad)
      const topItems = sorted.slice(0, 5)
      const others = sorted.slice(5)
      
      const chartData = topItems.map((item: any) => ({
        name: item.subnovedad,
        value: item.cantidad
      }))
      
      if (others.length > 0) {
        const othersCount = others.reduce((sum: number, item: any) => sum + item.cantidad, 0)
        chartData.push({
          name: 'OTROS',
          value: othersCount
        })
      }
      
      distribucionChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: '#151d30',
          borderColor: '#1f2b45',
          textStyle: { color: '#f1f5f9' },
          formatter: '{b}: <b>{c}</b> ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 0,
          textStyle: { color: '#94a3b8', fontSize: 9 }
        },
        series: [
          {
            name: 'Distribución',
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 6,
              borderColor: '#151d30',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 14,
                fontWeight: 'bold',
                color: '#f1f5f9'
              }
            },
            labelLine: {
              show: false
            },
            data: chartData,
            color: ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#6366f1', '#a855f7']
          }
        ]
      })
    }
  } catch (error) {
    console.error('Error fetching distribution data:', error)
  }
}

// Window resizing
const handleResize = () => {
  evolutionChart?.resize()
  novedadesChart?.resize()
  distribucionChart?.resize()
}

onMounted(() => {
  loadDashboardData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  evolutionChart?.dispose()
  novedadesChart?.dispose()
  distribucionChart?.dispose()
})

// Reload when filters change
watch(
  () => [appStore.selectedDashboardMonth, appStore.selectedDashboardDay],
  () => {
    loadDashboardData()
  }
)
</script>
