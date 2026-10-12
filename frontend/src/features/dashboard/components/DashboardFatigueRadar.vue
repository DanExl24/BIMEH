<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[460px] max-w-full overflow-hidden">
    <!-- Header del Componente -->
    <div class="flex items-center justify-between gap-2 mb-3 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-2 h-4 bg-rose-500 rounded-sm"></div>
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Alertas de Mando S-1 & Sanidad Preventiva
        </h3>
      </div>

      <!-- Badge de Estado de Alertas -->
      <span 
        v-if="activeTab === 'fatiga'" 
        class="text-xs bg-rose-500/15 text-rose-300 font-bold px-2.5 py-1 rounded-lg border border-rose-500/30 whitespace-nowrap"
      >
        {{ fatigaList.length }} en Límite Operacional
      </span>
      <span 
        v-else 
        class="text-xs bg-amber-500/15 text-amber-300 font-bold px-2.5 py-1 rounded-lg border border-amber-500/30 whitespace-nowrap"
      >
        {{ sanidadList.length }} Casos Médicos
      </span>
    </div>

    <!-- Pestañas Conmutables -->
    <div class="flex border-b border-darkBorder mb-3 overflow-x-auto no-scrollbar whitespace-nowrap gap-1 pb-0.5 max-w-full shrink-0">
      <button 
        type="button"
        @click="activeTab = 'fatiga'"
        class="px-3.5 py-2 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 whitespace-nowrap flex items-center gap-1.5 cursor-pointer"
        :class="activeTab === 'fatiga' ? 'border-rose-400 text-rose-300 font-bold bg-rose-500/5' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        <Flame class="w-3.5 h-3.5" />
        <span>Radar de Fatiga ({{ fatigaList.length }})</span>
      </button>

      <button 
        type="button"
        @click="activeTab = 'sanidad'"
        class="px-3.5 py-2 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 whitespace-nowrap flex items-center gap-1.5 cursor-pointer"
        :class="activeTab === 'sanidad' ? 'border-amber-400 text-amber-300 font-bold bg-amber-500/5' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        <Stethoscope class="w-3.5 h-3.5" />
        <span>Sanidad & Junta Médica ({{ sanidadList.length }})</span>
      </button>
    </div>

    <!-- Sub-filtros por Pestaña -->
    <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800/80 text-[11px] shrink-0">
      <div v-if="activeTab === 'fatiga'" class="flex items-center gap-1.5">
        <span class="text-slate-400 font-medium">Umbral continuo:</span>
        <div class="flex gap-1">
          <button 
            v-for="u in [20, 30, 45]" 
            :key="u"
            @click="cambiarUmbralFatiga(u)"
            class="px-2 py-0.5 rounded-md font-bold transition-colors cursor-pointer"
            :class="umbralFatiga === u ? 'bg-rose-500 text-slate-950' : 'bg-slate-800 text-slate-400 hover:text-slate-200'"
          >
            {{ u }}d
          </button>
        </div>
      </div>

      <div v-else class="flex items-center gap-1.5">
        <span class="text-slate-400 font-medium">Acumulación mínima:</span>
        <div class="flex gap-1">
          <button 
            v-for="d in [15, 30]" 
            :key="d"
            @click="cambiarDiasSanidad(d)"
            class="px-2 py-0.5 rounded-md font-bold transition-colors cursor-pointer"
            :class="diasSanidad === d ? 'bg-amber-500 text-slate-950' : 'bg-slate-800 text-slate-400 hover:text-slate-200'"
          >
            {{ d }}d
          </button>
        </div>
      </div>

      <span class="text-[10px] text-slate-400 font-mono">
        Ordenado por criticidad
      </span>
    </div>

    <!-- Contenido Scrollable -->
    <div class="flex-1 overflow-y-auto pr-1 space-y-2 select-none">
      <!-- Loader -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-16 space-y-2">
        <Loader2 class="w-7 h-7 text-rose-400 animate-spin" />
        <span class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">Analizando registros de servicio...</span>
      </div>

      <!-- Tab 1: Fatiga -->
      <div v-else-if="activeTab === 'fatiga'">
        <div v-if="fatigaList.length === 0" class="text-center py-14 text-slate-400 text-xs">
          No hay efectivos que superen el umbral de {{ umbralFatiga }} días continuos de servicio.
        </div>

        <div 
          v-for="item in fatigaList" 
          :key="item.id_personal"
          class="p-3 rounded-xl bg-darkBg/60 border border-darkBorder/60 hover:border-slate-700 transition-all flex flex-col gap-1.5"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="min-w-0">
              <span class="text-xs font-bold text-slate-100 truncate block">{{ item.nombre }}</span>
              <span class="text-[10px] font-mono text-slate-400">CC: {{ item.cedula }} • {{ item.estado_actual }}</span>
            </div>

            <!-- Badge de Fatiga -->
            <div class="flex items-center gap-1.5 shrink-0">
              <span 
                class="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold"
                :class="item.nivel_alerta === 'CRITICO' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'"
              >
                {{ item.dias_continuos }} DÍAS
              </span>
            </div>
          </div>

          <div class="text-[10px] text-slate-400 bg-slate-900/60 px-2 py-1 rounded-lg border border-slate-800/80 flex items-center gap-1.5">
            <span class="font-bold text-rose-400 shrink-0">S-1:</span>
            <span class="truncate">{{ item.recomendacion }}</span>
          </div>
        </div>
      </div>

      <!-- Tab 2: Sanidad -->
      <div v-else-if="activeTab === 'sanidad'">
        <div v-if="sanidadList.length === 0" class="text-center py-14 text-slate-400 text-xs">
          No hay registros de sanidad acumulada que superen los {{ diasSanidad }} días.
        </div>

        <div 
          v-for="item in sanidadList" 
          :key="item.id_personal"
          class="p-3 rounded-xl bg-darkBg/60 border border-darkBorder/60 hover:border-slate-700 transition-all flex flex-col gap-1.5"
        >
          <div class="flex items-center justify-between gap-2">
            <div class="min-w-0">
              <span class="text-xs font-bold text-slate-100 truncate block">{{ item.nombre }}</span>
              <span class="text-[10px] font-mono text-slate-400">CC: {{ item.cedula }} • {{ item.novedades }}</span>
            </div>

            <!-- Badge de Sanidad -->
            <div class="flex items-center gap-1.5 shrink-0">
              <span 
                class="px-2 py-0.5 rounded-md text-[10px] font-mono font-bold"
                :class="item.clasificacion === 'JUNTA_MEDICA_SUGERIDA' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'"
              >
                {{ item.total_dias_sanidad }}d Sanidad
              </span>
            </div>
          </div>

          <div class="text-[10px] text-slate-400 bg-slate-900/60 px-2 py-1 rounded-lg border border-slate-800/80 flex items-center gap-1.5">
            <span 
              class="font-bold shrink-0"
              :class="item.clasificacion === 'JUNTA_MEDICA_SUGERIDA' ? 'text-rose-400' : 'text-amber-400'"
            >
              {{ item.clasificacion === 'JUNTA_MEDICA_SUGERIDA' ? 'JUNTA MÉDICA:' : 'SEGUIMIENTO:' }}
            </span>
            <span class="truncate">{{ item.recomendacion }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Flame, Stethoscope, Loader2 } from 'lucide-vue-next'
import { alertasService } from '../services/alertas.service'
import type { AlertaFatigaItem, AlertaSanidadItem } from '../types/alertas.types'

const props = defineProps<{
  month?: string
  day?: string
  fecha?: string
}>()

const activeTab = ref<'fatiga' | 'sanidad'>('fatiga')
const loading = ref(false)
const umbralFatiga = ref(30)
const diasSanidad = ref(15)

const fatigaList = ref<AlertaFatigaItem[]>([])
const sanidadList = ref<AlertaSanidadItem[]>([])

const cargarDatos = async () => {
  loading.value = true
  try {
    const [fatigaData, sanidadData] = await Promise.all([
      alertasService.getFatiga(umbralFatiga.value, props.month, props.day, props.fecha),
      alertasService.getSanidad(diasSanidad.value, props.month, props.day, props.fecha)
    ])
    fatigaList.value = fatigaData
    sanidadList.value = sanidadData
  } catch (error) {
    console.error('Error al cargar alertas de fatiga y sanidad:', error)
  } finally {
    loading.value = false
  }
}

const cambiarUmbralFatiga = (u: number) => {
  umbralFatiga.value = u
  cargarDatos()
}

const cambiarDiasSanidad = (d: number) => {
  diasSanidad.value = d
  cargarDatos()
}

onMounted(() => {
  cargarDatos()
})

watch(
  () => [props.month, props.day, props.fecha],
  () => {
    cargarDatos()
  }
)
</script>
