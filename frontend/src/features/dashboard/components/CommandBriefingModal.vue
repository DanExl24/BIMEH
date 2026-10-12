<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
    <!-- Backdrop con desenfoque militar -->
    <div 
      class="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity" 
      @click="closeModal"
    ></div>

    <!-- Modal Content -->
    <div 
      class="relative w-full max-w-4xl bg-darkCard border border-slate-700/80 rounded-3xl shadow-2xl shadow-cyan-950/20 overflow-hidden flex flex-col max-h-[90vh] z-10 animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- Cabecera Institucional del Modal -->
      <div class="px-5 py-4 sm:px-8 sm:py-5 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-md shadow-cyan-500/10">
            <Shield class="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-[10px] font-black uppercase tracking-widest text-cyan-400 px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20">
                S-1 MANDO TÁCTICO
              </span>
              <span class="text-xs text-slate-400 font-medium">BIMEJ 12</span>
            </div>
            <h2 class="text-sm sm:text-base font-bold text-slate-100 uppercase tracking-wide mt-0.5">
              El Parte de las 06:00 — Estado de Fuerza
            </h2>
          </div>
        </div>

        <button 
          @click="closeModal"
          class="w-8 h-8 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-100 flex items-center justify-center transition-colors border border-slate-700"
          title="Cerrar"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Barra de navegación y Selector de Vista -->
      <div class="px-5 py-2.5 sm:px-8 bg-slate-900/60 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div class="flex items-center gap-2 text-xs text-slate-300">
          <Calendar class="w-4 h-4 text-cyan-400" />
          <span class="font-semibold text-slate-400">Fecha del Parte:</span>
          <span class="font-bold text-slate-100 font-mono">{{ parte?.fecha || fecha || 'En proceso...' }}</span>
        </div>

        <!-- Selector de Pestaña -->
        <div class="flex bg-slate-950/80 p-1 rounded-xl border border-slate-800 text-xs">
          <button 
            @click="activeTab = 'ejecutiva'"
            class="px-3.5 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5"
            :class="activeTab === 'ejecutiva' ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
          >
            <Activity class="w-3.5 h-3.5" />
            <span>Boletín Ejecutivo</span>
          </button>
          <button 
            @click="activeTab = 'radiograma'"
            class="px-3.5 py-1.5 rounded-lg font-bold transition-all flex items-center gap-1.5"
            :class="activeTab === 'radiograma' ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
          >
            <Terminal class="w-3.5 h-3.5" />
            <span>Radiograma Castrense</span>
          </button>
        </div>
      </div>

      <!-- Cuerpo del Modal (Scrollable) -->
      <div class="p-5 sm:p-8 overflow-y-auto space-y-6 flex-1">
        <!-- Loader -->
        <div v-if="loading" class="flex flex-col items-center justify-center py-16 space-y-3">
          <Loader2 class="w-9 h-9 text-cyan-400 animate-spin" />
          <p class="text-xs text-slate-400 font-semibold tracking-wider uppercase">
            Consolidando Estado de Fuerza Oficial...
          </p>
        </div>

        <!-- Vista 1: Boletín Ejecutivo Visual -->
        <div v-else-if="activeTab === 'ejecutiva' && parte" class="space-y-6">
          <!-- 4 KPIs de Fuerza -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <div class="glass-panel p-4 rounded-2xl border-slate-700/60">
              <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Efectivo Total</span>
              <span class="text-2xl font-black text-slate-100 font-mono mt-1 block">{{ parte.total_personal }}</span>
              <span class="text-[10px] text-slate-400 mt-0.5 block">Hombres en Unidad</span>
            </div>

            <div class="glass-panel p-4 rounded-2xl border-emerald-500/30 bg-emerald-500/5">
              <span class="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider block">Disponibles</span>
              <span class="text-2xl font-black text-emerald-400 font-mono mt-1 block">{{ parte.disponibles }}</span>
              <span class="text-[10px] text-emerald-300/80 mt-0.5 block">En Línea de Operación</span>
            </div>

            <div class="glass-panel p-4 rounded-2xl border-amber-500/30 bg-amber-500/5">
              <span class="text-[11px] font-semibold text-amber-400 uppercase tracking-wider block">En Novedad</span>
              <span class="text-2xl font-black text-amber-400 font-mono mt-1 block">{{ parte.novedades }}</span>
              <span class="text-[10px] text-amber-300/80 mt-0.5 block">Excusas, Permisos, etc.</span>
            </div>

            <div class="glass-panel p-4 rounded-2xl border-cyan-500/30 bg-cyan-500/5">
              <span class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider block">% Operatividad</span>
              <span class="text-2xl font-black text-cyan-400 font-mono mt-1 block">{{ parte.porcentaje_disponibilidad }}%</span>
              <span class="text-[10px] text-cyan-300/80 mt-0.5 block">Efectividad Combate</span>
            </div>
          </div>

          <!-- Disposición vs Categorías -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Disposición Operacional -->
            <div class="glass-panel p-4 sm:p-5 rounded-2xl border-slate-700/60 space-y-3">
              <div class="flex items-center gap-2 pb-2 border-b border-slate-800">
                <ShieldCheck class="w-4 h-4 text-emerald-400" />
                <h4 class="text-xs font-bold text-slate-200 uppercase tracking-wider">
                  I. Disposición de Efectivos Disponibles
                </h4>
              </div>
              <div class="space-y-2 text-xs">
                <div class="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span class="text-slate-300">Área de Operaciones</span>
                  <span class="font-mono font-bold text-emerald-400 text-sm">{{ parte.disposicion.area_operaciones }}</span>
                </div>
                <div class="flex justify-between items-center p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span class="text-slate-300">Comando de Unidad (CDO)</span>
                  <span class="font-mono font-bold text-cyan-400 text-sm">{{ parte.disposicion.cdo_unidad }}</span>
                </div>
              </div>
            </div>

            <!-- Categorías de Novedades -->
            <div class="glass-panel p-4 sm:p-5 rounded-2xl border-slate-700/60 space-y-3">
              <div class="flex items-center gap-2 pb-2 border-b border-slate-800">
                <AlertTriangle class="w-4 h-4 text-amber-400" />
                <h4 class="text-xs font-bold text-slate-200 uppercase tracking-wider">
                  II. Clasificación de Novedades
                </h4>
              </div>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span class="text-[11px] text-slate-400 block">Sanidad Militar</span>
                  <span class="font-mono font-bold text-rose-400 text-sm mt-0.5 block">{{ parte.desglose_categorias.sanidad }}</span>
                </div>
                <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span class="text-[11px] text-slate-400 block">Descanso / Permisos</span>
                  <span class="font-mono font-bold text-amber-400 text-sm mt-0.5 block">{{ parte.desglose_categorias.descanso }}</span>
                </div>
                <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span class="text-[11px] text-slate-400 block">Servicio / Cursos</span>
                  <span class="font-mono font-bold text-blue-400 text-sm mt-0.5 block">{{ parte.desglose_categorias.servicio }}</span>
                </div>
                <div class="p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                  <span class="text-[11px] text-slate-400 block">Administrativas</span>
                  <span class="font-mono font-bold text-purple-400 text-sm mt-0.5 block">{{ parte.desglose_categorias.administrativas }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Alertas Críticas de Mando S-1 -->
          <div class="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 space-y-2">
            <div class="flex items-center gap-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
              <AlertCircle class="w-4 h-4" />
              <span>Alertas Preventivas S-1 para la Comandancia</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs text-slate-300">
              <div class="p-3 rounded-xl bg-slate-950/60 border border-amber-500/20">
                <span class="font-bold text-amber-300 block">Radar de Fatiga:</span>
                <p class="text-[11px] text-slate-300 mt-1">
                  <b class="text-amber-400">{{ parte.alertas_resumen.total_fatiga_critica }}</b> efectivos superan los 30 días continuos en servicio sin descanso.
                </p>
              </div>
              <div class="p-3 rounded-xl bg-slate-950/60 border border-amber-500/20">
                <span class="font-bold text-rose-300 block">Sanidad y Junta Médica:</span>
                <p class="text-[11px] text-slate-300 mt-1">
                  <b class="text-rose-400">{{ parte.alertas_resumen.total_sanidad_critica }}</b> efectivos acumulan más de 15 días en incapacidad/hospitalización.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Vista 2: Radiograma Castrense en Texto Plano -->
        <div v-else-if="activeTab === 'radiograma' && parte" class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Texto Oficial Estructurado (Listo para Transmisión)
            </span>
            <button 
              @click="copiarRadiograma"
              class="px-3.5 py-1.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl text-xs transition-all flex items-center gap-1.5 shadow-sm shadow-cyan-500/20 cursor-pointer"
            >
              <Check v-if="copiado" class="w-3.5 h-3.5 stroke-[3]" />
              <Copy v-else class="w-3.5 h-3.5" />
              <span>{{ copiado ? '¡Copiado!' : 'Copiar Radiograma' }}</span>
            </button>
          </div>

          <div class="p-4 rounded-2xl bg-slate-950 border border-slate-800 font-mono text-[11px] sm:text-xs text-emerald-400/90 leading-relaxed overflow-x-auto whitespace-pre selection:bg-emerald-500 selection:text-slate-950 shadow-inner">
            {{ parte.radiograma_texto }}
          </div>
        </div>
      </div>

      <!-- Pie de Acción del Modal -->
      <div class="px-5 py-4 sm:px-8 bg-slate-900 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div class="flex items-center gap-2">
          <button 
            @click="copiarRadiograma"
            class="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer"
          >
            <Check v-if="copiado" class="w-4 h-4 text-emerald-400 stroke-[3]" />
            <Copy v-else class="w-4 h-4 text-cyan-400" />
            <span>{{ copiado ? 'Radiograma Copiado' : 'Copiar Texto al Portapapeles' }}</span>
          </button>
        </div>

        <div class="flex items-center gap-3">
          <button 
            @click="closeModal"
            class="px-4 py-2.5 bg-transparent hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-xl text-xs font-semibold transition-all cursor-pointer"
          >
            Cerrar
          </button>

          <a 
            :href="pdfUrl"
            target="_blank"
            class="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-emerald-950/40 cursor-pointer"
          >
            <Download class="w-4 h-4" />
            <span>Descargar PDF Oficial</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { 
  Shield, 
  X, 
  Calendar, 
  Activity, 
  Terminal, 
  Loader2, 
  ShieldCheck, 
  AlertTriangle, 
  AlertCircle, 
  Copy, 
  Check, 
  Download 
} from 'lucide-vue-next'
import { alertasService } from '../services/alertas.service'
import type { ParteDiarioData } from '../types/alertas.types'

const props = defineProps<{
  isOpen: boolean
  fecha?: string
}>()

const emit = defineEmits<{
  (e: 'update:isOpen', value: boolean): void
  (e: 'close'): void
}>()

const activeTab = ref<'ejecutiva' | 'radiograma'>('ejecutiva')
const loading = ref(false)
const parte = ref<ParteDiarioData | null>(null)
const copiado = ref(false)

const pdfUrl = computed(() => {
  return alertasService.descargarPdfParteDiario(parte.value?.fecha || props.fecha)
})

const closeModal = () => {
  emit('update:isOpen', false)
  emit('close')
}

const cargarParteDiario = async () => {
  loading.value = true
  try {
    const data = await alertasService.getParteDiario(props.fecha)
    parte.value = data
  } catch (error) {
    console.error('Error al cargar parte diario:', error)
  } finally {
    loading.value = false
  }
}

const copiarRadiograma = async () => {
  if (!parte.value?.radiograma_texto) return
  try {
    await navigator.clipboard.writeText(parte.value.radiograma_texto)
    copiado.value = true
    setTimeout(() => {
      copiado.value = false
    }, 2500)
  } catch (err) {
    console.error('Error al copiar radiograma:', err)
  }
}

watch(
  () => [props.isOpen, props.fecha],
  ([newOpen]) => {
    if (newOpen) {
      cargarParteDiario()
    }
  },
  { immediate: true }
)
</script>
