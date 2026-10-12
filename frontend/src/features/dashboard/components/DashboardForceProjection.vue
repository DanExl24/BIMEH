<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[460px] max-w-full overflow-hidden">
    <!-- Header -->
    <div class="flex items-center justify-between gap-2 mb-3 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-2 h-4 bg-teal-500 rounded-sm"></div>
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Proyección de Fuerza Disponible (15 / 30 Días)
        </h3>
      </div>
      <span class="text-xs bg-teal-500/15 text-teal-300 font-bold px-2.5 py-1 rounded-lg border border-teal-500/30 whitespace-nowrap">
        {{ proyeccion?.detalle_movimientos.length || 0 }} Reincorporaciones Previstas
      </span>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-2 flex-1">
      <Loader2 class="w-7 h-7 text-teal-400 animate-spin" />
      <span class="text-[11px] text-slate-400 font-semibold uppercase tracking-wider">Calculando horizonte de fuerza...</span>
    </div>

    <!-- Contenido -->
    <div v-else-if="proyeccion" class="flex flex-col flex-1 overflow-hidden space-y-4">
      <!-- Tarjetas de Horizonte Proyectado (7, 15 y 30 días) -->
      <div class="grid grid-cols-3 gap-2.5 shrink-0">
        <!-- +7 Días -->
        <div class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-center space-y-1">
          <span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block">+7 Días</span>
          <span class="text-base sm:text-lg font-black text-slate-100 font-mono block">
            {{ proyeccion.proyeccion_7_dias.estimados_disponibles }}
          </span>
          <span class="text-[10px] text-emerald-400 font-bold block">
            +{{ proyeccion.proyeccion_7_dias.reincorporaciones }} hombres
          </span>
          <span class="text-[9px] text-slate-400 font-mono block">
            {{ proyeccion.proyeccion_7_dias.porcentaje }}% disp.
          </span>
        </div>

        <!-- +15 Días -->
        <div class="p-3 rounded-xl bg-slate-900/60 border border-teal-500/30 bg-teal-500/5 text-center space-y-1">
          <span class="text-[10px] text-teal-300 font-semibold uppercase tracking-wider block">+15 Días</span>
          <span class="text-base sm:text-lg font-black text-teal-300 font-mono block">
            {{ proyeccion.proyeccion_15_dias.estimados_disponibles }}
          </span>
          <span class="text-[10px] text-teal-400 font-bold block">
            +{{ proyeccion.proyeccion_15_dias.reincorporaciones }} hombres
          </span>
          <span class="text-[9px] text-slate-400 font-mono block">
            {{ proyeccion.proyeccion_15_dias.porcentaje }}% disp.
          </span>
        </div>

        <!-- +30 Días -->
        <div class="p-3 rounded-xl bg-slate-900/60 border border-cyan-500/30 bg-cyan-500/5 text-center space-y-1">
          <span class="text-[10px] text-cyan-300 font-semibold uppercase tracking-wider block">+30 Días</span>
          <span class="text-base sm:text-lg font-black text-cyan-300 font-mono block">
            {{ proyeccion.proyeccion_30_dias.estimados_disponibles }}
          </span>
          <span class="text-[10px] text-cyan-400 font-bold block">
            +{{ proyeccion.proyeccion_30_dias.reincorporaciones }} hombres
          </span>
          <span class="text-[9px] text-slate-400 font-mono block">
            {{ proyeccion.proyeccion_30_dias.porcentaje }}% disp.
          </span>
        </div>
      </div>

      <!-- Barra Comparativa Actual vs +30 Días -->
      <div class="p-3 rounded-xl bg-slate-950/60 border border-slate-800 shrink-0 space-y-1.5">
        <div class="flex justify-between items-center text-[11px]">
          <span class="text-slate-400">Actual: <b class="text-slate-200 font-mono">{{ proyeccion.efectivo_actual.porcentaje }}%</b></span>
          <span class="text-teal-400 font-bold">Proyección a 30 días: <b class="font-mono">{{ proyeccion.proyeccion_30_dias.porcentaje }}%</b></span>
        </div>
        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden flex">
          <div 
            class="bg-slate-400 h-full transition-all duration-500" 
            :style="{ width: `${proyeccion.efectivo_actual.porcentaje}%` }"
          ></div>
          <div 
            class="bg-teal-400 h-full transition-all duration-500 shadow-sm shadow-teal-500/50" 
            :style="{ width: `${Math.max(0, proyeccion.proyeccion_30_dias.porcentaje - proyeccion.efectivo_actual.porcentaje)}%` }"
          ></div>
        </div>
      </div>

      <!-- Lista de Próximas Reincorporaciones -->
      <div class="flex-1 overflow-hidden flex flex-col min-h-0">
        <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 block shrink-0">
          Cronograma de Retorno a la Disponibilidad
        </span>

        <div class="flex-1 overflow-y-auto pr-1 space-y-2 select-none">
          <div v-if="proyeccion.detalle_movimientos.length === 0" class="text-center py-8 text-slate-400 text-xs">
            No se registran novedades con vencimiento próximo en el horizonte.
          </div>

          <div 
            v-for="m in proyeccion.detalle_movimientos" 
            :key="m.id_personal + '-' + m.fecha_fin"
            class="p-2.5 rounded-xl bg-darkBg/60 border border-darkBorder/60 hover:border-slate-700 transition-colors flex items-center justify-between gap-2"
          >
            <div class="min-w-0">
              <span class="text-xs font-bold text-slate-200 truncate block">{{ m.nombre }}</span>
              <span class="text-[10px] text-slate-400">Retorna de: <b class="text-slate-300">{{ m.novedad }}</b></span>
            </div>

            <div class="text-right shrink-0">
              <span class="text-xs font-mono font-bold text-teal-400 block">
                {{ m.dias_restantes === 0 ? 'Hoy' : `en ${m.dias_restantes}d` }}
              </span>
              <span class="text-[9px] text-slate-500 font-mono">{{ m.fecha_fin }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Loader2 } from 'lucide-vue-next'
import { alertasService } from '../services/alertas.service'
import type { ProyeccionFuerzaData } from '../types/alertas.types'

const props = defineProps<{
  fecha?: string
}>()

const loading = ref(false)
const proyeccion = ref<ProyeccionFuerzaData | null>(null)

const cargarProyeccion = async () => {
  loading.value = true
  try {
    const data = await alertasService.getProyeccion(30, props.fecha)
    proyeccion.value = data
  } catch (error) {
    console.error('Error al cargar proyeccion de fuerza:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  cargarProyeccion()
})

watch(
  () => props.fecha,
  () => {
    cargarProyeccion()
  }
)
</script>
