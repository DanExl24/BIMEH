<template>
  <div class="space-y-6 min-w-0 max-w-full pb-10">
    <!-- 1. Header & Hero Selector de Novedad -->
    <div class="glass-panel p-4 sm:p-6 rounded-3xl border border-darkBorder/80 bg-gradient-to-br from-darkCard/95 via-darkCard/80 to-slate-900/60 shadow-xl relative overflow-hidden">
      <div class="absolute -right-12 -top-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-5 relative z-10">
        <div class="space-y-1.5">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              Módulo de Auditoría
            </span>
            <span class="text-xs text-slate-400 font-mono">Solo Lectura</span>
          </div>
          <h2 class="text-xl sm:text-2xl font-black text-slate-100 tracking-tight flex items-center gap-2.5">
            <Tag class="w-6 h-6 text-cyan-400" />
            Gestión y Búsqueda de Novedades
          </h2>
          <p class="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
            Consulte y audite de forma instantánea qué personal contó con determinada novedad, en qué fechas y cuántos días acumuló, con filtros cruzados y exportación oficial.
          </p>
        </div>

        <!-- Botones de Exportación Rápida -->
        <div class="flex items-center gap-2.5 shrink-0">
          <button
            @click="handleExportar('excel')"
            :disabled="isDownloadingExcel || isLoading"
            class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-400 border border-emerald-500/30 hover:border-emerald-500/50 text-xs font-bold transition-all shadow-sm hover:shadow-emerald-500/10 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            title="Descargar reporte en Excel (.xlsx)"
          >
            <Loader2 v-if="isDownloadingExcel" class="w-4 h-4 animate-spin text-emerald-400" />
            <FileSpreadsheet v-else class="w-4 h-4 text-emerald-400" />
            <span>{{ isDownloadingExcel ? 'Generando...' : 'Exportar Excel' }}</span>
          </button>

          <button
            @click="handleExportar('pdf')"
            :disabled="isDownloadingPdf || isLoading"
            class="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 text-rose-400 border border-rose-500/30 hover:border-rose-500/50 text-xs font-bold transition-all shadow-sm hover:shadow-rose-500/10 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            title="Descargar reporte oficial en PDF"
          >
            <Loader2 v-if="isDownloadingPdf" class="w-4 h-4 animate-spin text-rose-400" />
            <FileText v-else class="w-4 h-4 text-rose-400" />
            <span>{{ isDownloadingPdf ? 'Generando...' : 'Exportar PDF' }}</span>
          </button>
        </div>
      </div>

      <!-- Selector Principal de Novedad -->
      <div class="mt-6 pt-5 border-t border-darkBorder/60">
        <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2.5">
          Seleccionar Novedad a Auditar:
        </label>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <!-- Dropdown con búsqueda para catálogo completo -->
          <div class="sm:col-span-2 lg:col-span-1 relative">
            <select
              v-model="filtros.id_sub_novedad"
              @change="onNovedadChange"
              class="w-full bg-slate-900/90 border border-darkBorder hover:border-cyan-500/50 focus:border-cyan-400 text-slate-100 rounded-xl px-3.5 py-2.5 text-xs font-semibold focus:outline-none transition-all cursor-pointer"
            >
              <option :value="null">-- TODAS LAS NOVEDADES --</option>
              <option 
                v-for="nov in catalogo" 
                :key="nov.id" 
                :value="nov.id"
              >
                {{ nov.nombre }} ({{ nov.total_registros.toLocaleString() }} días / {{ nov.total_personal }} pers.)
              </option>
            </select>
          </div>

          <!-- Badges de acceso rápido a las novedades más comunes -->
          <div class="sm:col-span-2 flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
            <button
              @click="seleccionarNovedadRapida(null)"
              class="px-2.5 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer border"
              :class="filtros.id_sub_novedad === null 
                ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-md shadow-cyan-500/20' 
                : 'bg-darkCard/60 hover:bg-slate-800 text-slate-400 border-darkBorder/80'"
            >
              Todas
            </button>
            <button
              v-for="nov in catalogoTop"
              :key="nov.id"
              @click="seleccionarNovedadRapida(nov.id)"
              class="px-2.5 py-1.5 rounded-lg text-[11px] font-bold uppercase tracking-wider transition-all whitespace-nowrap cursor-pointer border"
              :class="filtros.id_sub_novedad === nov.id 
                ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-md shadow-cyan-500/20' 
                : 'bg-darkCard/60 hover:bg-slate-800 text-slate-300 border-darkBorder/80 hover:border-cyan-500/40'"
            >
              {{ nov.nombre }}
              <span class="text-[10px] ml-1 opacity-70 font-mono">({{ nov.total_registros }})</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. Tarjetas de Métricas KPI en Tiempo Real -->
    <NovedadKpis :kpis="kpis" />

    <!-- 3. Barra de Filtros Interactivos -->
    <div class="glass-panel p-4 sm:p-5 rounded-2xl border border-darkBorder/80 bg-darkCard/90 space-y-4">
      <div class="flex items-center justify-between border-b border-darkBorder/50 pb-3">
        <div class="flex items-center gap-2">
          <Filter class="w-4 h-4 text-cyan-400" />
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200">
            Filtros Dinámicos
          </h3>
        </div>
        <button
          v-if="tieneFiltrosActivos"
          @click="limpiarFiltros"
          class="text-[11px] font-semibold text-rose-400 hover:text-rose-300 flex items-center gap-1 cursor-pointer transition-colors"
        >
          <RotateCcw class="w-3 h-3" />
          Restablecer Filtros
        </button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Filtro por Mes -->
        <div>
          <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Mes Operacional
          </label>
          <select
            v-model="filtros.mes"
            @change="onMesChange"
            class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
          >
            <option value="TODOS">TODOS LOS MESES</option>
            <option v-for="m in mesesDisponibles" :key="m" :value="m">
              {{ m }}
            </option>
          </select>
        </div>

        <!-- Rango de Fechas / Días: Desde -->
        <div>
          <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
            <span>{{ filtros.mes !== 'TODOS' ? 'Día Desde' : 'Fecha Desde' }}</span>
            <span v-if="filtros.mes !== 'TODOS'" class="text-[10px] text-cyan-400 font-mono font-bold lowercase">
              ({{ filtros.mes }})
            </span>
          </label>

          <!-- Si seleccionó un mes específico, solo permite elegir días de ese mes -->
          <select
            v-if="filtros.mes !== 'TODOS'"
            v-model="diaInicio"
            @change="onDiaChange"
            class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
          >
            <option value="">Todo el mes (Desde día 01)</option>
            <option v-for="d in diasDelMes" :key="d" :value="d">
              Día {{ d }} de {{ filtros.mes }}
            </option>
          </select>

          <!-- Si mes es TODOS, permite selector libre de fecha -->
          <input
            v-else
            v-model="filtros.fecha_inicio"
            @change="triggerSearch"
            type="date"
            class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all"
          />
        </div>

        <!-- Rango de Fechas / Días: Hasta -->
        <div>
          <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
            <span>{{ filtros.mes !== 'TODOS' ? 'Día Hasta' : 'Fecha Hasta' }}</span>
            <span v-if="filtros.mes !== 'TODOS'" class="text-[10px] text-cyan-400 font-mono font-bold lowercase">
              ({{ filtros.mes }})
            </span>
          </label>

          <!-- Si seleccionó un mes específico, solo permite elegir días de ese mes -->
          <select
            v-if="filtros.mes !== 'TODOS'"
            v-model="diaFin"
            @change="onDiaChange"
            class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
          >
            <option value="">Todo el mes (Hasta día {{ totalDiasMes }})</option>
            <option v-for="d in diasDelMes" :key="d" :value="d">
              Día {{ d }} de {{ filtros.mes }}
            </option>
          </select>

          <!-- Si mes es TODOS, permite selector libre de fecha -->
          <input
            v-else
            v-model="filtros.fecha_fin"
            @change="triggerSearch"
            type="date"
            class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all"
          />
        </div>

        <!-- Filtro por Estado de Personal -->
        <div>
          <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Estado de Personal
          </label>
          <select
            v-model="filtros.estado"
            @change="triggerSearch"
            class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
          >
            <option value="TODOS">TODOS (ACTIVOS Y RETIRADOS)</option>
            <option value="ACTIVO">SOLO ACTIVOS</option>
            <option value="RETIRADO">SOLO RETIRADOS</option>
          </select>
        </div>

        <!-- Búsqueda por Cédula o Nombre -->
        <div class="sm:col-span-2 lg:col-span-4">
          <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Buscar por Nombre o Cédula
          </label>
          <div class="relative">
            <Search class="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              v-model="filtros.q"
              @input="onSearchInput"
              type="text"
              placeholder="Escriba número de documento o apellidos/nombres..."
              class="w-full bg-slate-900 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-100 rounded-xl pl-10 pr-10 py-2.5 text-xs font-medium focus:outline-none transition-all placeholder:text-slate-600"
            />
            <button
              v-if="filtros.q"
              @click="filtros.q = ''; triggerSearch()"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 p-1 rounded-md"
            >
              <X class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. Tabla de Resultados Paginados -->
    <div class="glass-panel rounded-2xl border border-darkBorder/80 bg-darkCard/90 overflow-hidden shadow-lg">
      <!-- Encabezado de la tabla con contador -->
      <div class="px-5 py-4 border-b border-darkBorder/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-darkCard/95">
        <div class="flex items-center gap-2.5">
          <ClipboardList class="w-4 h-4 text-cyan-400" />
          <h3 class="text-xs sm:text-sm font-bold text-slate-200 uppercase tracking-wide">
            Registros Encontrados
          </h3>
          <span class="px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 text-[11px] font-mono font-bold border border-cyan-500/20">
            {{ totalRegistros.toLocaleString() }}
          </span>
        </div>

        <div class="flex items-center gap-3">
          <!-- Selector de Límite por página -->
          <div class="flex items-center gap-2 text-xs text-slate-400">
            <span class="text-[11px]">Mostrar:</span>
            <select
              v-model="filtros.limit"
              @change="onLimitChange"
              class="bg-slate-900 border border-darkBorder text-slate-300 rounded-lg px-2 py-1 text-xs focus:outline-none focus:border-cyan-400 cursor-pointer"
            >
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Spinner de Carga -->
      <div v-if="isLoading" class="py-20 flex flex-col items-center justify-center gap-3 text-slate-400">
        <Loader2 class="w-8 h-8 text-cyan-400 animate-spin" />
        <p class="text-xs font-medium">Buscando registros en la base de datos...</p>
      </div>

      <!-- Estado Vacío -->
      <div v-else-if="registros.length === 0" class="py-20 flex flex-col items-center justify-center gap-3 text-center px-4">
        <div class="w-12 h-12 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-400">
          <AlertCircle class="w-6 h-6 text-slate-500" />
        </div>
        <p class="text-sm font-bold text-slate-300">No se encontraron registros</p>
        <p class="text-xs text-slate-500 max-w-sm">
          No hay novedades coincidentes con los filtros seleccionados. Intente ajustar el mes, novedad o término de búsqueda.
        </p>
        <button
          @click="limpiarFiltros"
          class="mt-2 px-3.5 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-semibold transition-all cursor-pointer"
        >
          Ver todas las novedades
        </button>
      </div>

      <!-- Tabla de Datos -->
      <div v-else class="overflow-x-auto scrollbar-thin">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-darkBorder/80 bg-slate-900/80 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <th class="py-3 px-4 text-center w-12">#</th>
              <th class="py-3 px-4">Cédula</th>
              <th class="py-3 px-4">Apellidos y Nombres</th>
              <th class="py-3 px-4 text-center">Estado</th>
              <th class="py-3 px-4">Novedad</th>
              <th class="py-3 px-4 text-center">Fecha Reporte</th>
              <th class="py-3 px-4 text-center">Periodo Novedad</th>
              <th class="py-3 px-4">Observación</th>
              <th class="py-3 px-4 text-center w-20">Acción</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-darkBorder/40 text-xs text-slate-300">
            <tr
              v-for="(item, idx) in registros"
              :key="item.id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="py-3 px-4 text-center font-mono text-slate-500 text-[11px]">
                {{ (filtros.page! - 1) * filtros.limit! + idx + 1 }}
              </td>
              <td class="py-3 px-4 font-mono font-semibold text-slate-200">
                {{ item.cedula }}
              </td>
              <td class="py-3 px-4 font-bold text-slate-100">
                {{ item.nombre }}
              </td>
              <td class="py-3 px-4 text-center">
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider inline-block"
                  :class="item.estado === 'ACTIVO' 
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' 
                    : 'bg-slate-700/40 text-slate-400 border border-slate-600/40'"
                >
                  {{ item.estado }}
                </span>
              </td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-300 text-[11px] font-semibold border border-cyan-500/20">
                  {{ item.sub_novedad }}
                </span>
              </td>
              <td class="py-3 px-4 text-center font-mono text-slate-300">
                {{ item.fecha_reporte }}
              </td>
              <td class="py-3 px-4 text-center font-mono text-slate-400 text-[11px]">
                <span v-if="item.fecha_inicio || item.fecha_final">
                  {{ item.fecha_inicio || '-' }} <span class="text-slate-600">→</span> {{ item.fecha_final || '-' }}
                </span>
                <span v-else class="text-slate-600">-</span>
              </td>
              <td class="py-3 px-4 max-w-xs text-slate-400 truncate text-[11px]" :title="item.descripcion">
                {{ item.descripcion || '-' }}
              </td>
              <td class="py-3 px-4 text-center">
                <router-link
                  :to="`/personal/${item.cedula}`"
                  class="p-1.5 rounded-lg bg-darkBorder/50 hover:bg-cyan-500/20 text-slate-400 hover:text-cyan-400 inline-flex items-center justify-center transition-colors"
                  title="Ver expediente completo del integrante"
                >
                  <ExternalLink class="w-4 h-4" />
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Barra de Paginación -->
      <div 
        v-if="totalPages > 1" 
        class="px-5 py-3.5 border-t border-darkBorder/60 bg-darkCard/95 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
      >
        <p class="text-slate-400 text-[11px]">
          Mostrando página <span class="font-bold text-slate-200">{{ filtros.page }}</span> de <span class="font-bold text-slate-200">{{ totalPages }}</span>
        </p>

        <div class="flex items-center gap-1.5 self-center">
          <button
            @click="cambiarPagina(filtros.page! - 1)"
            :disabled="filtros.page === 1 || isLoading"
            class="px-2.5 py-1 rounded-lg bg-darkCard border border-darkBorder text-slate-300 hover:text-slate-100 hover:border-cyan-500/50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Anterior
          </button>

          <!-- Indicadores de página -->
          <button
            v-for="p in paginasVisibles"
            :key="p"
            @click="cambiarPagina(p)"
            class="w-7 h-7 rounded-lg text-xs font-bold transition-all border"
            :class="p === filtros.page 
              ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-sm' 
              : 'bg-darkCard border-darkBorder text-slate-400 hover:text-slate-200 hover:border-slate-700'"
          >
            {{ p }}
          </button>

          <button
            @click="cambiarPagina(filtros.page! + 1)"
            :disabled="filtros.page === totalPages || isLoading"
            class="px-2.5 py-1 rounded-lg bg-darkCard border border-darkBorder text-slate-300 hover:text-slate-100 hover:border-cyan-500/50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Siguiente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  Tag, 
  Search, 
  Filter, 
  RotateCcw, 
  ClipboardList, 
  FileSpreadsheet, 
  FileText, 
  ExternalLink, 
  Loader2, 
  AlertCircle, 
  X 
} from 'lucide-vue-next'

import NovedadKpis from '../components/NovedadKpis.vue'
import { novedadesService } from '../services/novedades.service'
import type { 
  NovedadCatalogoItem, 
  NovedadRegistroItem, 
  NovedadesKpis as NovedadesKpisType, 
  NovedadesConsultaFiltros 
} from '../types/novedades.types'
import { useAppStore } from '@stores/appStore'
import { MONTH_TO_NUMBER, getDaysInMonth } from '@/utils/date'

const appStore = useAppStore()

const catalogo = ref<NovedadCatalogoItem[]>([])
const registros = ref<NovedadRegistroItem[]>([])
const totalRegistros = ref(0)
const totalPages = ref(1)
const isLoading = ref(false)
const isDownloadingExcel = ref(false)
const isDownloadingPdf = ref(false)

const kpis = ref<NovedadesKpisType>({
  total_registros: 0,
  personal_unico: 0,
  activos_unicos: 0,
  retirados_unicos: 0,
  primera_fecha: null,
  ultima_fecha: null
})

const filtros = ref<NovedadesConsultaFiltros>({
  id_sub_novedad: null,
  mes: 'TODOS',
  fecha_inicio: '',
  fecha_fin: '',
  q: '',
  estado: 'TODOS',
  page: 1,
  limit: 50
})

let searchDebounceTimer: any = null

const mesesDisponibles = computed(() => {
  if (appStore.months && appStore.months.length > 0) {
    return appStore.months
  }
  return [
    'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
    'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
  ]
})

const catalogoTop = computed(() => {
  return [...catalogo.value]
    .sort((a, b) => b.total_registros - a.total_registros)
    .slice(0, 6)
})

const diaInicio = ref('')
const diaFin = ref('')

const anioOperacional = computed(() => {
  return 2026
})

const mesNumero = computed(() => {
  if (!filtros.value.mes || filtros.value.mes === 'TODOS') return ''
  return MONTH_TO_NUMBER[filtros.value.mes.toUpperCase()] || ''
})

const totalDiasMes = computed(() => {
  if (!filtros.value.mes || filtros.value.mes === 'TODOS') return 31
  return getDaysInMonth(filtros.value.mes, anioOperacional.value)
})

const diasDelMes = computed(() => {
  return Array.from({ length: totalDiasMes.value }, (_, i) => String(i + 1).padStart(2, '0'))
})

const onMesChange = () => {
  diaInicio.value = ''
  diaFin.value = ''
  filtros.value.fecha_inicio = ''
  filtros.value.fecha_fin = ''
  triggerSearch()
}

const onDiaChange = () => {
  if (filtros.value.mes && filtros.value.mes !== 'TODOS') {
    const y = anioOperacional.value
    const m = mesNumero.value

    if (diaInicio.value && diaFin.value && diaFin.value < diaInicio.value) {
      diaFin.value = diaInicio.value
    }

    filtros.value.fecha_inicio = diaInicio.value ? `${y}-${m}-${diaInicio.value}` : ''
    filtros.value.fecha_fin = diaFin.value ? `${y}-${m}-${diaFin.value}` : ''
  }
  triggerSearch()
}

const tieneFiltrosActivos = computed(() => {
  return (
    filtros.value.id_sub_novedad !== null ||
    filtros.value.mes !== 'TODOS' ||
    Boolean(filtros.value.fecha_inicio) ||
    Boolean(filtros.value.fecha_fin) ||
    Boolean(diaInicio.value) ||
    Boolean(diaFin.value) ||
    Boolean(filtros.value.q) ||
    filtros.value.estado !== 'TODOS'
  )
})

const paginasVisibles = computed(() => {
  const current = filtros.value.page || 1
  const total = totalPages.value
  const delta = 2
  const pages: number[] = []

  for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
    pages.push(i)
  }
  return pages
})

const ejecutarConsulta = async () => {
  isLoading.value = true
  try {
    const res = await novedadesService.consultar(filtros.value)
    registros.value = res.registros
    kpis.value = res.kpis
    totalRegistros.value = res.total
    totalPages.value = res.total_pages
  } catch (error) {
    console.error('Error al consultar novedades:', error)
  } finally {
    isLoading.value = false
  }
}

const triggerSearch = () => {
  filtros.value.page = 1
  ejecutarConsulta()
}

const onSearchInput = () => {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    triggerSearch()
  }, 350)
}

const onNovedadChange = () => {
  triggerSearch()
}

const seleccionarNovedadRapida = (id: number | null) => {
  filtros.value.id_sub_novedad = id
  triggerSearch()
}

const onLimitChange = () => {
  filtros.value.page = 1
  ejecutarConsulta()
}

const cambiarPagina = (nuevaPagina: number) => {
  if (nuevaPagina < 1 || nuevaPagina > totalPages.value) return
  filtros.value.page = nuevaPagina
  ejecutarConsulta()
  window.scrollTo({ top: 200, behavior: 'smooth' })
}

const limpiarFiltros = () => {
  diaInicio.value = ''
  diaFin.value = ''
  filtros.value = {
    id_sub_novedad: null,
    mes: 'TODOS',
    fecha_inicio: '',
    fecha_fin: '',
    q: '',
    estado: 'TODOS',
    page: 1,
    limit: 50
  }
  ejecutarConsulta()
}

const handleExportar = async (formato: 'excel' | 'pdf') => {
  if (formato === 'excel') isDownloadingExcel.value = true
  else isDownloadingPdf.value = true

  try {
    await novedadesService.descargarReporte(formato, filtros.value)
  } catch (err: any) {
    alert(err?.message || 'Error al exportar reporte')
  } finally {
    if (formato === 'excel') isDownloadingExcel.value = false
    else isDownloadingPdf.value = false
  }
}

onMounted(async () => {
  try {
    catalogo.value = await novedadesService.getCatalogo()
  } catch (e) {
    console.error('Error al cargar catálogo de novedades:', e)
  }
  await ejecutarConsulta()
})
</script>
