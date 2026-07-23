<template>
  <div class="space-y-6">
    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-12 h-12 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
      <p class="text-slate-400 text-sm font-medium">Cargando datos operacionales...</p>
    </div>

    <!-- Error / Day without records -->
    <div v-else-if="hasError" class="glass-panel p-12 rounded-2xl text-center space-y-4 border-amber-500/30">
      <div class="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mx-auto shadow-lg">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <div>
        <h3 class="text-base font-bold text-slate-100 uppercase tracking-wider">Día Sin Registro de Datos</h3>
        <p class="text-xs text-slate-400 max-w-md mx-auto mt-1 font-sans">
          El día seleccionado ({{ appStore.selectedDashboardDay }} de {{ appStore.selectedDashboardMonth || 'Todos los meses' }}) aún no ha sido cargado o sincronizado en la base de datos.
        </p>
      </div>
      <div class="pt-2 flex justify-center gap-3">
        <button 
          @click="appStore.selectedDashboardDay = ''"
          class="px-4 py-2 bg-darkBg border border-darkBorder hover:border-slate-500 rounded-xl text-xs font-bold text-slate-300 transition-all cursor-pointer"
        >
          Ver Todo el Mes ({{ appStore.selectedDashboardMonth }})
        </button>
      </div>
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
                :key="c.cedula + '-' + c.fecha"
                class="flex items-center justify-between p-3 rounded-xl bg-darkBg/40 border border-darkBorder/40 hover:border-darkBorder"
              >
                <div>
                  <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-200 hover:text-cyan-400 block uppercase">
                    {{ c.nombre }}
                  </router-link>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-[10px] text-slate-500 font-mono">C.C. {{ c.cedula }}</span>
                    <span v-if="c.fecha" class="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/10">
                      {{ c.fecha }}
                    </span>
                  </div>
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
                :key="c.cedula + '-' + c.fecha"
                class="flex items-center justify-between p-3 rounded-xl bg-darkBg/40 border border-darkBorder/40 hover:border-darkBorder"
              >
                <div>
                  <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-200 hover:text-cyan-400 block uppercase">
                    {{ c.nombre }}
                  </router-link>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-[10px] text-slate-500 font-mono">C.C. {{ c.cedula }}</span>
                    <span v-if="c.fecha" class="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/10">
                      {{ c.fecha }}
                    </span>
                  </div>
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
                :key="c.cedula + '-' + c.fecha"
                class="flex items-center justify-between p-3 rounded-xl bg-darkBg/40 border border-darkBorder/40 hover:border-darkBorder"
              >
                <div>
                  <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-200 hover:text-cyan-400 block uppercase">
                    {{ c.nombre }}
                  </router-link>
                  <div class="flex items-center gap-2 mt-0.5">
                    <span class="text-[10px] text-slate-500 font-mono">C.C. {{ c.cedula }}</span>
                    <span v-if="c.fecha" class="text-[9px] font-mono font-bold text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/10">
                      {{ c.fecha }}
                    </span>
                  </div>
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
import { fetchKPIs, fetchCambios, fetchEvolucion, fetchNovedadesFrecuentes, fetchDistribucion } from '../services/api'
import type { KPIData, CambiosResponse } from '../types'

const appStore = useAppStore()

const loading = ref(true)
const hasError = ref(false)
const kpis = ref<KPIData | null>(null)
const cambios = ref<CambiosResponse | null>(null)
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
  hasError.value = false
  try {
    const mes = appStore.selectedDashboardMonth
    const dia = appStore.selectedDashboardDay
    
    // Fetch KPIs & Cambios in parallel
    const [kpisData, cambiosData] = await Promise.all([
      fetchKPIs(mes, dia),
      fetchCambios(mes, dia)
    ])
    
    kpis.value = kpisData
    cambios.value = cambiosData
    
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
    hasError.value = true
  }
}


// Chart Initializations
const initEvolutionChart = async () => {
  if (!evolutionChartDom.value) return
  
  if (evolutionChart) {
    evolutionChart.dispose()
  }
  
  evolutionChart = echarts.init(evolutionChartDom.value)
  
  try {
    const mes = appStore.selectedDashboardMonth
    const dia = appStore.selectedDashboardDay
    const data = await fetchEvolucion(mes, dia)
    
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
    const data = await fetchNovedadesFrecuentes(mes, dia)
    
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
    const data = await fetchDistribucion(mes, dia)
    
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
          radius: ['35%', '60%'],
          center: ['50%', '42%'],
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
