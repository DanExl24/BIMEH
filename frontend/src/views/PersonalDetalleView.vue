<template>
  <div class="space-y-6">
    <!-- Back Button -->
    <div>
      <router-link 
        to="/personal" 
        class="text-xs text-slate-400 font-semibold hover:text-cyan-400 flex items-center gap-1.5 transition-colors"
      >
        &larr; Volver al Buscador
      </router-link>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-10 h-10 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
      <p class="text-slate-400 text-sm">Cargando expediente personal...</p>
    </div>

    <!-- Profile content -->
    <div v-else-if="profile" class="space-y-6">
      
      <!-- 1. Header Info Card -->
      <div class="glass-panel p-6 rounded-3xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div class="flex items-start gap-4">
          <!-- Profile Icon / Badge -->
          <div class="w-16 h-16 bg-cyan-500/10 border border-cyan-500/25 rounded-2xl flex items-center justify-center text-cyan-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-3 flex-wrap">
              <h2 class="text-lg font-bold text-slate-100 uppercase tracking-tight">{{ profile.nombre }}</h2>
              <span 
                class="text-[9px] font-extrabold tracking-wider px-2.5 py-0.5 rounded border uppercase"
                :class="profile.estado === 'ACTIVO' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'"
              >
                {{ profile.estado }}
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-1 font-mono">
              Cédula de Ciudadanía: <span class="text-slate-200 font-bold">{{ profile.cedula }}</span>
            </p>
            <p v-if="profile.fecha_retiro" class="text-xs text-red-400 mt-1 font-mono font-semibold">
              Fecha de Retiro: {{ profile.fecha_retiro }}
            </p>
          </div>
        </div>

        <!-- Export Buttons -->
        <div class="flex items-center gap-3 self-stretch md:self-auto justify-end">
          <a 
            :href="`${appStore.apiBase}/api/exportar/csv?tipo=personal&cedula=${profile.cedula}`"
            download
            class="px-3.5 py-2 bg-darkBg border border-darkBorder hover:border-slate-600 rounded-xl text-xs font-semibold text-slate-300 flex items-center gap-2 transition-all"
          >
            Descargar CSV
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/excel?tipo=personal&cedula=${profile.cedula}`"
            download
            class="px-3.5 py-2 bg-emerald-500/10 border border-emerald-500/20 hover:border-emerald-500/40 rounded-xl text-xs font-semibold text-emerald-400 flex items-center gap-2 transition-all"
          >
            Descargar Excel
          </a>
          <a 
            :href="`${appStore.apiBase}/api/exportar/pdf?tipo=personal&cedula=${profile.cedula}`"
            download
            class="px-3.5 py-2 bg-cyan-500/10 border border-cyan-500/20 hover:border-cyan-500/40 rounded-xl text-xs font-semibold text-cyan-400 flex items-center gap-2 transition-all"
          >
            Descargar PDF
          </a>
        </div>
      </div>

      <!-- 2. Statistics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Tarjeta Tiempo Disponible -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">📈 Tasa Disponibilidad</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-cyan-400">{{ profile.tiempo_disponible_pct }}%</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Porcentaje de días en servicio disponible</p>
        </div>

        <!-- Tarjeta Tiempo en Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">🏥 Tasa Novedades</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-amber-500">{{ profile.tiempo_novedades_pct }}%</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Porcentaje de días fuera de servicio</p>
        </div>

        <!-- Tarjeta Total Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">📝 Novedades Registradas</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-slate-200">{{ profile.total_novedades }}</span>
            <span class="text-xs text-slate-400">días</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Días totales reportados con novedad</p>
        </div>

        <!-- Promedio Duración Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">⏱️ Duración Promedio</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-slate-200">{{ profile.promedio_duracion_novedades }}</span>
            <span class="text-xs text-slate-400">días consecutivos</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Promedio de duración por evento de novedad</p>
        </div>
      </div>

      <!-- 3. Chart and Details -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Tiempo acumulado subnovedad chart -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[400px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Distribución de Novedades (Días)
          </h3>
          <div class="flex-1 min-h-0">
            <div ref="acumuladoChartDom" class="chart-container"></div>
          </div>
        </div>

        <!-- Línea de tiempo individual -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-2 flex flex-col h-[400px]">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 border-b border-darkBorder/40 pb-3">
            <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <span class="w-2 h-4 bg-teal-500 rounded-sm"></span> Línea de Tiempo de Novedades e Historial
            </h3>
            <!-- Selectores de Filtro -->
            <div class="flex items-center gap-2">
              <select 
                v-model="filtroMes"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1 text-[11px] text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todos los Meses</option>
                <option value="01">Enero</option>
                <option value="02">Febrero</option>
                <option value="03">Marzo</option>
                <option value="04">Abril</option>
                <option value="05">Mayo</option>
                <option value="06">Junio</option>
                <option value="07">Julio</option>
              </select>
              <select 
                v-model="filtroDia"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1 text-[11px] text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todos los Días</option>
                <option v-for="d in diasDelMes" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>
          
          <div class="flex-1 overflow-y-auto pr-2 space-y-4">
            <div v-if="filteredHistorial.length === 0" class="text-center py-20 text-slate-500 text-xs">
              No se encontraron registros para los filtros seleccionados.
            </div>
            <div 
              v-else
              v-for="h in filteredHistorial" 
              :key="h.fecha"
              class="relative pl-6 border-l-2 border-darkBorder hover:border-cyan-500/30 transition-colors pb-4 last:pb-0"
            >
              <!-- Timeline node -->
              <div 
                class="absolute -left-[6px] top-1.5 w-2.5 h-2.5 rounded-full border border-darkBg"
                :class="isAvailable(h.subnovedad) ? 'bg-emerald-500' : 'bg-amber-500'"
              ></div>

              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold font-mono text-cyan-400 bg-cyan-500/5 border border-cyan-500/10 px-2 py-0.5 rounded">
                  {{ h.fecha }}
                </span>
                <span 
                  class="text-[9px] font-bold px-2 py-0.5 rounded border uppercase"
                  :class="isAvailable(h.subnovedad) ? 'bg-emerald-500/10 border-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 border-amber-500/10 text-amber-500'"
                >
                  {{ h.subnovedad }}
                </span>
              </div>
              <div class="mt-1.5 space-y-1">
                <p class="text-xs text-slate-300 font-semibold uppercase">{{ h.descripcion || 'Sin descripción oficial' }}</p>
                <p v-if="h.desde || h.hasta" class="text-[10px] text-slate-500 font-mono">
                  Rango novedad: {{ h.desde || 'N/A' }} al {{ h.hasta || 'N/A' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../stores/appStore'
import * as echarts from 'echarts'

const route = useRoute()
const appStore = useAppStore()

interface Profile {
  cedula: number
  nombre: string
  estado: string
  fecha_retiro: string | null
  primer_registro_fecha: string | null
  ultimo_registro_fecha: string | null
  total_dias: number
  tiempo_disponible_pct: number
  tiempo_novedades_pct: number
  total_novedades: number
  promedio_duracion_novedades: number
  ultima_novedad: string | null
}

interface HistorialEntry {
  fecha: string
  subnovedad: string
  descripcion: string
  desde: string | null
  hasta: string | null
}

const loading = ref(true)
const profile = ref<Profile | null>(null)
const historial = ref<HistorialEntry[]>([])

const acumuladoChartDom = ref<HTMLDivElement | null>(null)
let acumuladoChart: echarts.ECharts | null = null

// Filtros de fecha individuales
const filtroMes = ref('')
const filtroDia = ref('')

const diasDelMes = Array.from({ length: 31 }, (_, i) => String(i + 1).padStart(2, '0'))

const filteredHistorial = computed(() => {
  return historial.value.filter(h => {
    const parts = h.fecha.split('-')
    const month = parts[1]
    const day = parts[2]
    
    const matchMonth = !filtroMes.value || month === filtroMes.value
    const matchDay = !filtroDia.value || day === filtroDia.value
    
    return matchMonth && matchDay
  })
})

const DISPONIBLE_STATUSES = ["CDO UNIDAD", "AREA OPERACIONES"]
const isAvailable = (subnovedad: string) => {
  return DISPONIBLE_STATUSES.includes(subnovedad)
}

const loadProfile = async () => {
  loading.value = true
  const cedula = route.params.cedula
  try {
    const res = await fetch(`${appStore.apiBase}/api/personal/${cedula}`)
    if (res.ok) {
      profile.value = await res.json()
    }
    
    const histRes = await fetch(`${appStore.apiBase}/api/personal/${cedula}/historial`)
    if (histRes.ok) {
      historial.value = await histRes.json()
    }
    
    loading.value = false
    
    setTimeout(() => {
      initAcumuladoChart()
    }, 50)
  } catch (error) {
    console.error('Error fetching profile:', error)
    loading.value = false
  }
}

const initAcumuladoChart = async () => {
  if (!acumuladoChartDom.value || !profile.value) return
  
  if (acumuladoChart) {
    acumuladoChart.dispose()
  }
  
  acumuladoChart = echarts.init(acumuladoChartDom.value)
  
  try {
    const res = await fetch(`${appStore.apiBase}/api/personal/${profile.value.cedula}/acumulado`)
    if (res.ok) {
      const data = await res.json()
      
      const chartData = data.map((d: any) => ({
        name: d.subnovedad,
        value: d.dias
      }))
      
      acumuladoChart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: '#151d30',
          borderColor: '#1f2b45',
          textStyle: { color: '#f1f5f9' },
          formatter: '{b}: <b>{c} días</b> ({d}%)'
        },
        series: [
          {
            type: 'pie',
            radius: '65%',
            center: ['50%', '50%'],
            roseType: 'area', // Premium look
            itemStyle: {
              borderRadius: 5,
              borderColor: '#151d30',
              borderWidth: 1.5
            },
            data: chartData,
            color: ['#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#6366f1', '#a855f7'],
            label: {
              color: '#94a3b8',
              fontSize: 10,
              formatter: '{b}'
            }
          }
        ]
      })
    }
  } catch (error) {
    console.error('Error generating accumulated chart:', error)
  }
}

const handleResize = () => {
  acumuladoChart?.resize()
}

onMounted(() => {
  loadProfile()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  acumuladoChart?.dispose()
})
</script>
