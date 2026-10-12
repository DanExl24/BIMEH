<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- 1. HEADER DE MANDO INSTITUCIONAL -->
    <div class="glass-panel p-5 sm:p-7 rounded-3xl border-cyan-500/30 bg-gradient-to-r from-slate-900/95 via-cyan-950/25 to-slate-900/95 shadow-xl shadow-cyan-950/20">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="flex items-start sm:items-center gap-3.5">
          <div class="w-12 h-12 rounded-2xl bg-cyan-500/15 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/15 shrink-0">
            <ShieldAlert class="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-black uppercase tracking-widest text-cyan-400 px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20">
                S-1 ESTADO MAYOR
              </span>
              <span class="text-xs text-slate-400 font-medium font-mono">BIMEJ 12 • QUINTA BRIGADA</span>
            </div>
            <h1 class="text-lg sm:text-2xl font-black text-slate-100 uppercase tracking-tight mt-1">
              Centro de Mando S-1 & Inteligencia Preventiva
            </h1>
            <p class="text-xs text-slate-400 mt-0.5 max-w-xl">
              Monitoreo continuo de fatiga en primera línea, sanidad militar, proyección de fuerza disponible y estado de fuerza diario oficial.
            </p>
          </div>
        </div>

        <!-- Acciones Rápidas -->
        <div class="flex flex-wrap items-center gap-2.5 shrink-0">
          <button 
            @click="showParteModal = true"
            class="px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black rounded-xl text-xs uppercase tracking-wider transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 cursor-pointer"
          >
            <FileText class="w-4 h-4 stroke-[2.5]" />
            <span>El Parte de las 06:00</span>
          </button>

          <a 
            :href="pdfUrl"
            target="_blank"
            class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-slate-600 text-slate-200 hover:text-white font-bold rounded-xl text-xs transition-all flex items-center gap-2 cursor-pointer shadow-sm"
          >
            <Download class="w-4 h-4 text-emerald-400" />
            <span>Descargar PDF</span>
          </a>
        </div>
      </div>

      <!-- Barra de Filtro de Fecha Activa -->
      <div class="mt-5 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div class="flex items-center gap-2 text-slate-300">
          <Calendar class="w-4 h-4 text-cyan-400" />
          <span class="text-slate-400 font-medium">Período Operativo Activo:</span>
          <span class="font-bold text-slate-100 font-mono bg-slate-950/80 px-2.5 py-1 rounded-lg border border-slate-800">
            {{ periodoEtiqueta }}
          </span>
          <span v-if="parteData?.fecha" class="text-[11px] text-cyan-400/90 font-mono">
            (Reporte: {{ parteData.fecha }})
          </span>
        </div>

        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">
            Sincronizado con Base de Datos
          </span>
        </div>
      </div>
    </div>

    <!-- 2. KPIs RESUMEN DE MANDO -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-5">
      <!-- Total Efectivo -->
      <div class="glass-panel p-4 rounded-2xl flex flex-col justify-between border-slate-700/60">
        <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Efectivo Total</span>
        <div class="mt-2">
          <span class="text-2xl sm:text-3xl font-black text-slate-100 font-mono">{{ parteData?.total_personal ?? '-' }}</span>
          <span class="text-[11px] text-slate-400 block mt-0.5">Fuerza registrada</span>
        </div>
      </div>

      <!-- Disponibles -->
      <div class="glass-panel p-4 rounded-2xl flex flex-col justify-between border-emerald-500/30 bg-emerald-500/5">
        <div class="flex justify-between items-center">
          <span class="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Disponibles</span>
          <span class="text-xs font-mono font-bold text-emerald-300">{{ parteData?.porcentaje_disponibilidad ?? 0 }}%</span>
        </div>
        <div class="mt-2">
          <span class="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">{{ parteData?.disponibles ?? '-' }}</span>
          <span class="text-[11px] text-emerald-300/80 block mt-0.5">En servicio activo</span>
        </div>
      </div>

      <!-- Novedades -->
      <div class="glass-panel p-4 rounded-2xl flex flex-col justify-between border-amber-500/30 bg-amber-500/5">
        <span class="text-[11px] font-semibold text-amber-400 uppercase tracking-wider">En Novedad</span>
        <div class="mt-2">
          <span class="text-2xl sm:text-3xl font-black text-amber-400 font-mono">{{ parteData?.novedades ?? '-' }}</span>
          <span class="text-[11px] text-amber-300/80 block mt-0.5">Permisos, Sanidad, Cursos</span>
        </div>
      </div>

      <!-- Alertas Críticas -->
      <div class="glass-panel p-4 rounded-2xl flex flex-col justify-between border-rose-500/30 bg-rose-500/5">
        <span class="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">Alertas S-1</span>
        <div class="mt-2">
          <span class="text-2xl sm:text-3xl font-black text-rose-400 font-mono">
            {{ (parteData?.alertas_resumen?.total_fatiga_critica ?? 0) + (parteData?.alertas_resumen?.total_sanidad_critica ?? 0) }}
          </span>
          <span class="text-[11px] text-rose-300/80 block mt-0.5">
            {{ parteData?.alertas_resumen?.total_fatiga_critica ?? 0 }} Fatiga • {{ parteData?.alertas_resumen?.total_sanidad_critica ?? 0 }} Sanidad
          </span>
        </div>
      </div>
    </div>

    <!-- 3. NAVEGACIÓN POR PESTAÑAS PRINCIPALES -->
    <div class="glass-panel p-1 rounded-2xl border-slate-800 bg-slate-900/80 flex flex-wrap gap-1">
      <button 
        @click="activeViewTab = 'fatiga'"
        class="px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer flex-1 sm:flex-none justify-center"
        :class="activeViewTab === 'fatiga' ? 'bg-rose-500 text-slate-950 shadow-md shadow-rose-500/20' : 'text-slate-400 hover:text-slate-200'"
      >
        <Flame class="w-4 h-4" />
        <span>Radar de Fatiga ({{ fatigaList.length }})</span>
      </button>

      <button 
        @click="activeViewTab = 'sanidad'"
        class="px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer flex-1 sm:flex-none justify-center"
        :class="activeViewTab === 'sanidad' ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20' : 'text-slate-400 hover:text-slate-200'"
      >
        <Stethoscope class="w-4 h-4" />
        <span>Sanidad & Junta Médica ({{ sanidadList.length }})</span>
      </button>

      <button 
        @click="activeViewTab = 'proyeccion'"
        class="px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer flex-1 sm:flex-none justify-center"
        :class="activeViewTab === 'proyeccion' ? 'bg-teal-500 text-slate-950 shadow-md shadow-teal-500/20' : 'text-slate-400 hover:text-slate-200'"
      >
        <TrendingUp class="w-4 h-4" />
        <span>Proyección a 15/30 Días</span>
      </button>

      <button 
        @click="activeViewTab = 'boletin'"
        class="px-4 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider transition-all flex items-center gap-2 cursor-pointer flex-1 sm:flex-none justify-center"
        :class="activeViewTab === 'boletin' ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
      >
        <Terminal class="w-4 h-4" />
        <span>El Parte Oficial & Radiograma</span>
      </button>
    </div>

    <!-- 4. CONTENIDO SEGÚN LA PESTAÑA SELECCIONADA -->
    <!-- Loader Global de Pestañas -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-24 space-y-3">
      <Loader2 class="w-10 h-10 text-cyan-400 animate-spin" />
      <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider">
        Sincronizando información de mando...
      </p>
    </div>

    <!-- TAB 1: RADAR DE FATIGA OPERACIONAL -->
    <div v-else-if="activeViewTab === 'fatiga'" class="space-y-4">
      <div class="glass-panel p-4 sm:p-6 rounded-2xl space-y-4">
        <!-- Filtros del Radar -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Umbral de días continuos:</span>
            <div class="flex gap-1">
              <button 
                v-for="u in [20, 30, 45, 60]" 
                :key="u"
                @click="umbralFatiga = u; cargarFatiga()"
                class="px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
                :class="umbralFatiga === u ? 'bg-rose-500 text-slate-950' : 'bg-slate-800 text-slate-400 hover:text-slate-200'"
              >
                {{ u }} Días
              </button>
            </div>
          </div>

          <!-- Buscador de Militar -->
          <div class="relative w-full sm:w-72">
            <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              v-model="filtroBuscarFatiga"
              type="text"
              placeholder="Buscar por nombre o cédula..."
              class="w-full pl-9 pr-3 py-1.5 bg-darkBg border border-slate-700 rounded-xl text-xs text-slate-200 placeholder:text-slate-500 outline-none focus:border-rose-400"
            />
          </div>
        </div>

        <!-- Lista de Tarjetas de Fatiga -->
        <div v-if="fatigaFiltrada.length === 0" class="text-center py-16 text-slate-400 text-xs">
          No hay efectivos que superen el umbral de {{ umbralFatiga }} días continuos de servicio en el período seleccionado.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <div 
            v-for="item in fatigaFiltrada" 
            :key="item.id_personal"
            class="p-4 rounded-2xl bg-darkBg/80 border border-slate-800 hover:border-slate-700 transition-all space-y-3 flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <router-link 
                    :to="`/personal/${item.cedula}`"
                    class="text-xs font-bold text-slate-100 hover:text-cyan-400 truncate block transition-colors"
                  >
                    {{ item.nombre }}
                  </router-link>
                  <span class="text-[11px] font-mono text-slate-400 block mt-0.5">
                    CC: {{ item.cedula }} • {{ item.estado_actual }}
                  </span>
                </div>

                <span 
                  class="px-2.5 py-1 rounded-lg text-xs font-mono font-black shrink-0"
                  :class="item.nivel_alerta === 'CRITICO' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'"
                >
                  {{ item.dias_continuos }} DÍAS
                </span>
              </div>

              <!-- Recomendación Castrense -->
              <div class="mt-3 text-[11px] text-slate-300 bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 space-y-1">
                <span class="text-[10px] font-bold text-rose-400 uppercase tracking-wider block">Recomendación S-1:</span>
                <p class="leading-relaxed">{{ item.recomendacion }}</p>
              </div>
            </div>

            <div class="pt-2 border-t border-slate-800/80 flex justify-between items-center text-[10px] text-slate-400">
              <span>Disposición: <b class="text-slate-200">{{ item.estado_actual }}</b></span>
              <router-link 
                :to="`/personal/${item.cedula}`"
                class="text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
              >
                <span>Ver Perfil</span>
                <ExternalLink class="w-3 h-3" />
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: SANIDAD MILITAR & JUNTA MÉDICA -->
    <div v-else-if="activeViewTab === 'sanidad'" class="space-y-4">
      <div class="glass-panel p-4 sm:p-6 rounded-2xl space-y-4">
        <!-- Filtros de Sanidad -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Días mínimos de sanidad:</span>
            <div class="flex gap-1">
              <button 
                v-for="d in [15, 30, 45]" 
                :key="d"
                @click="diasSanidad = d; cargarSanidad()"
                class="px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer"
                :class="diasSanidad === d ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-400 hover:text-slate-200'"
              >
                {{ d }} Días
              </button>
            </div>
          </div>

          <div class="relative w-full sm:w-72">
            <Search class="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              v-model="filtroBuscarSanidad"
              type="text"
              placeholder="Buscar por nombre o cédula..."
              class="w-full pl-9 pr-3 py-1.5 bg-darkBg border border-slate-700 rounded-xl text-xs text-slate-200 placeholder:text-slate-500 outline-none focus:border-amber-400"
            />
          </div>
        </div>

        <div v-if="sanidadFiltrada.length === 0" class="text-center py-16 text-slate-400 text-xs">
          No hay efectivos con más de {{ diasSanidad }} días acumulados de novedades médicas en el período.
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <div 
            v-for="item in sanidadFiltrada" 
            :key="item.id_personal"
            class="p-4 rounded-2xl bg-darkBg/80 border border-slate-800 hover:border-slate-700 transition-all space-y-3 flex flex-col justify-between"
          >
            <div>
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <router-link 
                    :to="`/personal/${item.cedula}`"
                    class="text-xs font-bold text-slate-100 hover:text-cyan-400 truncate block transition-colors"
                  >
                    {{ item.nombre }}
                  </router-link>
                  <span class="text-[11px] font-mono text-slate-400 block mt-0.5">
                    CC: {{ item.cedula }} • {{ item.episodios }} episodios
                  </span>
                </div>

                <span 
                  class="px-2.5 py-1 rounded-lg text-xs font-mono font-black shrink-0"
                  :class="item.clasificacion === 'JUNTA_MEDICA_SUGERIDA' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'"
                >
                  {{ item.total_dias_sanidad }}d Sanidad
                </span>
              </div>

              <!-- Tipo de Novedades Médicas -->
              <div class="text-[11px] text-slate-300 bg-slate-900/80 p-2.5 rounded-xl border border-slate-800 space-y-1 mt-2">
                <span class="text-[10px] font-bold text-amber-400 uppercase tracking-wider block">Diagnóstico / Novedades:</span>
                <p class="font-medium text-slate-200">{{ item.novedades }}</p>
                <p class="text-[10px] text-slate-400 mt-1">{{ item.recomendacion }}</p>
              </div>
            </div>

            <div class="pt-2 border-t border-slate-800/80 flex justify-between items-center text-[10px] text-slate-400">
              <span>Último: <b class="text-slate-300 font-mono">{{ item.ultima_fecha }}</b></span>
              <router-link 
                :to="`/personal/${item.cedula}`"
                class="text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
              >
                <span>Ver Historial</span>
                <ExternalLink class="w-3 h-3" />
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: PROYECCIÓN DE FUERZA DISPONIBLE -->
    <div v-else-if="activeViewTab === 'proyeccion'" class="space-y-4">
      <DashboardForceProjection 
        :month="appStore.selectedDashboardMonth"
        :day="appStore.selectedDashboardDay"
        :fecha="fechaEfectiva"
      />
    </div>

    <!-- TAB 4: BOLETÍN OFICIAL & RADIOGRAMA MILITAR -->
    <div v-else-if="activeViewTab === 'boletin' && parteData" class="space-y-6">
      <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
          <div>
            <h3 class="text-base font-bold text-slate-100 uppercase tracking-wide">
              Radiograma Oficial de Estado de Fuerza (06:00R)
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">
              Formato institucional estructurado listo para copiado directo a canales de transmisión de mando.
            </p>
          </div>

          <button 
            @click="copiarRadiograma"
            class="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl text-xs transition-all flex items-center gap-1.5 shadow-md shadow-cyan-500/20 cursor-pointer shrink-0"
          >
            <Check v-if="copiado" class="w-4 h-4 stroke-[3]" />
            <Copy v-else class="w-4 h-4" />
            <span>{{ copiado ? '¡Radiograma Copiado!' : 'Copiar Radiograma' }}</span>
          </button>
        </div>

        <div class="p-5 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-xs text-emerald-400/90 leading-relaxed overflow-x-auto whitespace-pre selection:bg-emerald-500 selection:text-slate-950 shadow-inner">
          {{ parteData.radiograma_texto }}
        </div>
      </div>
    </div>

    <!-- Modal "El Parte de las 06:00" -->
    <CommandBriefingModal 
      v-model:is-open="showParteModal" 
      :month="appStore.selectedDashboardMonth"
      :day="appStore.selectedDashboardDay"
      :fecha="fechaEfectiva" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { 
  ShieldAlert, 
  FileText, 
  Download, 
  Calendar, 
  Flame, 
  Stethoscope, 
  TrendingUp, 
  Terminal, 
  Loader2, 
  Search, 
  ExternalLink, 
  Copy, 
  Check 
} from 'lucide-vue-next'
import { useAppStore } from '@stores/appStore'
import { alertasService } from '@features/dashboard/services/alertas.service'
import type { 
  AlertaFatigaItem, 
  AlertaSanidadItem, 
  ParteDiarioData 
} from '@features/dashboard/types/alertas.types'

import DashboardForceProjection from '@features/dashboard/components/DashboardForceProjection.vue'
import CommandBriefingModal from '@features/dashboard/components/CommandBriefingModal.vue'

const appStore = useAppStore()

const activeViewTab = ref<'fatiga' | 'sanidad' | 'proyeccion' | 'boletin'>('fatiga')
const loading = ref(false)
const showParteModal = ref(false)
const copiado = ref(false)

const umbralFatiga = ref(30)
const diasSanidad = ref(15)
const filtroBuscarFatiga = ref('')
const filtroBuscarSanidad = ref('')

const fatigaList = ref<AlertaFatigaItem[]>([])
const sanidadList = ref<AlertaSanidadItem[]>([])
const parteData = ref<ParteDiarioData | null>(null)

const periodoEtiqueta = computed(() => {
  const m = appStore.selectedDashboardMonth
  const d = appStore.selectedDashboardDay
  if (m && d) return `${m} - Día ${d}`
  if (m) return `Mes de ${m}`
  if (d) return `Día ${d} (Anual)`
  return 'Consolidado General'
})

const fechaEfectiva = computed(() => {
  return undefined
})

const pdfUrl = computed(() => {
  return alertasService.descargarPdfParteDiario(
    appStore.selectedDashboardMonth,
    appStore.selectedDashboardDay,
    fechaEfectiva.value
  )
})

const fatigaFiltrada = computed(() => {
  const q = filtroBuscarFatiga.value.trim().toLowerCase()
  if (!q) return fatigaList.value
  return fatigaList.value.filter(
    item => item.nombre.toLowerCase().includes(q) || String(item.cedula).includes(q)
  )
})

const sanidadFiltrada = computed(() => {
  const q = filtroBuscarSanidad.value.trim().toLowerCase()
  if (!q) return sanidadList.value
  return sanidadList.value.filter(
    item => item.nombre.toLowerCase().includes(q) || String(item.cedula).includes(q)
  )
})

const cargarFatiga = async () => {
  try {
    fatigaList.value = await alertasService.getFatiga(
      umbralFatiga.value, 
      appStore.selectedDashboardMonth, 
      appStore.selectedDashboardDay, 
      fechaEfectiva.value
    )
  } catch (err) {
    console.error('Error cargando fatiga:', err)
  }
}

const cargarSanidad = async () => {
  try {
    sanidadList.value = await alertasService.getSanidad(
      diasSanidad.value, 
      appStore.selectedDashboardMonth, 
      appStore.selectedDashboardDay, 
      fechaEfectiva.value
    )
  } catch (err) {
    console.error('Error cargando sanidad:', err)
  }
}

const cargarParte = async () => {
  try {
    parteData.value = await alertasService.getParteDiario(
      appStore.selectedDashboardMonth, 
      appStore.selectedDashboardDay, 
      fechaEfectiva.value
    )
  } catch (err) {
    console.error('Error cargando parte diario:', err)
  }
}

const cargarTodo = async () => {
  loading.value = true
  try {
    await Promise.all([
      cargarFatiga(),
      cargarSanidad(),
      cargarParte()
    ])
  } finally {
    loading.value = false
  }
}

const copiarRadiograma = async () => {
  if (!parteData.value?.radiograma_texto) return
  try {
    await navigator.clipboard.writeText(parteData.value.radiograma_texto)
    copiado.value = true
    setTimeout(() => {
      copiado.value = false
    }, 2500)
  } catch (err) {
    console.error('Error al copiar radiograma:', err)
  }
}

onMounted(() => {
  cargarTodo()
})

watch(
  () => [appStore.selectedDashboardMonth, appStore.selectedDashboardDay],
  () => {
    cargarTodo()
  }
)
</script>
