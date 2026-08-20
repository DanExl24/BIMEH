<template>
  <div 
    class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[440px] max-w-full overflow-hidden"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <div class="flex items-center justify-between gap-2 mb-3">
      <div class="flex items-center gap-2">
        <div class="w-2 h-4 bg-purple-500 rounded-sm"></div>
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Transiciones de Estado {{ month ? `(${month})` : 'del Año' }}
        </h3>
      </div>
      <span class="text-xs bg-purple-500/15 text-purple-300 font-bold px-2.5 py-1 rounded-lg border border-purple-500/30 whitespace-nowrap">
        {{ totalCambios || 0 }} Cambios
      </span>
    </div>

    <!-- Tabs for changes (horizontally scrollable on mobile) -->
    <div class="flex border-b border-darkBorder mb-3 overflow-x-auto no-scrollbar whitespace-nowrap gap-1 pb-0.5 max-w-full">
      <button 
        type="button"
        @click="activeChangeTab = 'entraron'"
        class="px-3.5 py-2 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 whitespace-nowrap flex-shrink-0 cursor-pointer flex items-center gap-1.5"
        :class="activeChangeTab === 'entraron' ? 'border-cyan-400 text-cyan-300 font-bold bg-cyan-500/5' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        <AlertTriangle class="w-3.5 h-3.5" />
        Entraron a Novedad ({{ cambios?.entraron_novedades.length || 0 }})
      </button>
      <button 
        type="button"
        @click="activeChangeTab = 'volvieron'"
        class="px-3.5 py-2 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 whitespace-nowrap flex-shrink-0 cursor-pointer flex items-center gap-1.5"
        :class="activeChangeTab === 'volvieron' ? 'border-cyan-400 text-cyan-300 font-bold bg-cyan-500/5' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        <CheckCircle2 class="w-3.5 h-3.5" />
        Volvieron Disponibles ({{ cambios?.volvieron_disponibles.length || 0 }})
      </button>
      <button 
        type="button"
        @click="activeChangeTab = 'otros'"
        class="px-3.5 py-2 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 whitespace-nowrap flex-shrink-0 cursor-pointer flex items-center gap-1.5"
        :class="activeChangeTab === 'otros' ? 'border-cyan-400 text-cyan-300 font-bold bg-cyan-500/5' : 'border-transparent text-slate-400 hover:text-slate-200'"
      >
        <RefreshCw class="w-3.5 h-3.5" />
        Otros Cambios ({{ cambios?.otros_cambios.length || 0 }})
      </button>
    </div>

    <!-- Content of tab -->
    <div class="flex-1 overflow-y-auto pr-1 space-y-2.5 select-none">
      <!-- Entraron Novedades -->
      <div v-if="activeChangeTab === 'entraron'" class="space-y-2">
        <div v-if="!cambios?.entraron_novedades.length" class="text-center py-12 text-slate-400 text-xs font-medium">
          Ningún integrante entró a novedad en este período.
        </div>
        <div 
          v-for="c in cambios?.entraron_novedades" 
          :key="c.cedula + '-' + c.fecha"
          class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-3 rounded-xl bg-darkBg/60 border border-darkBorder/60 hover:border-slate-700 max-w-full transition-colors"
        >
          <div class="min-w-0 flex-1">
            <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-100 hover:text-cyan-400 block uppercase truncate">
              {{ c.nombre }}
            </router-link>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span class="text-xs text-slate-400 font-mono">C.C. {{ c.cedula }}</span>
              <span v-if="c.fecha" class="text-xs font-mono font-bold text-cyan-300 bg-cyan-500/15 px-2 py-0.5 rounded border border-cyan-500/20">
                {{ c.fecha }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-1.5 sm:gap-2 text-[11px] sm:text-xs flex-wrap">
            <span class="text-emerald-400 bg-emerald-500/10 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg border border-emerald-500/20 font-medium">
              {{ c.novedad_anterior }}
            </span>
            <ArrowRight class="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span class="text-amber-400 bg-amber-500/10 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg border border-amber-500/20 font-semibold">
              {{ c.novedad_nueva }}
            </span>
          </div>
        </div>
      </div>

      <!-- Volvieron Disponibles -->
      <div v-if="activeChangeTab === 'volvieron'" class="space-y-2">
        <div v-if="!cambios?.volvieron_disponibles.length" class="text-center py-12 text-slate-400 text-xs font-medium">
          Ningún integrante volvió a disponible en este período.
        </div>
        <div 
          v-for="c in cambios?.volvieron_disponibles" 
          :key="c.cedula + '-' + c.fecha"
          class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-3 rounded-xl bg-darkBg/60 border border-darkBorder/60 hover:border-slate-700 max-w-full transition-colors"
        >
          <div class="min-w-0 flex-1">
            <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-100 hover:text-cyan-400 block uppercase truncate">
              {{ c.nombre }}
            </router-link>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span class="text-xs text-slate-400 font-mono">C.C. {{ c.cedula }}</span>
              <span v-if="c.fecha" class="text-xs font-mono font-bold text-cyan-300 bg-cyan-500/15 px-2 py-0.5 rounded border border-cyan-500/20">
                {{ c.fecha }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-1.5 sm:gap-2 text-[11px] sm:text-xs flex-wrap">
            <span class="text-amber-400 bg-amber-500/10 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg border border-amber-500/20 font-medium">
              {{ c.novedad_anterior }}
            </span>
            <ArrowRight class="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span class="text-emerald-400 bg-emerald-500/10 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg border border-emerald-500/20 font-semibold">
              {{ c.novedad_nueva }}
            </span>
          </div>
        </div>
      </div>

      <!-- Otros Cambios -->
      <div v-if="activeChangeTab === 'otros'" class="space-y-2">
        <div v-if="!cambios?.otros_cambios.length" class="text-center py-12 text-slate-400 text-xs font-medium">
          Ningún otro cambio detectado en este período.
        </div>
        <div 
          v-for="c in cambios?.otros_cambios" 
          :key="c.cedula + '-' + c.fecha"
          class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 p-3 rounded-xl bg-darkBg/60 border border-darkBorder/60 hover:border-slate-700 max-w-full transition-colors"
        >
          <div class="min-w-0 flex-1">
            <router-link :to="`/personal/${c.cedula}`" class="text-xs font-bold text-slate-100 hover:text-cyan-400 block uppercase truncate">
              {{ c.nombre }}
            </router-link>
            <div class="flex items-center gap-2 mt-1 flex-wrap">
              <span class="text-xs text-slate-400 font-mono">C.C. {{ c.cedula }}</span>
              <span v-if="c.fecha" class="text-xs font-mono font-bold text-cyan-300 bg-cyan-500/15 px-2 py-0.5 rounded border border-cyan-500/20">
                {{ c.fecha }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-1.5 sm:gap-2 text-[11px] sm:text-xs flex-wrap">
            <span class="text-slate-300 bg-slate-800 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg border border-slate-700 font-medium">
              {{ c.novedad_anterior }}
            </span>
            <ArrowRight class="w-3.5 h-3.5 text-slate-500 shrink-0" />
            <span class="text-cyan-400 bg-cyan-500/10 px-2 sm:px-2.5 py-0.5 sm:py-1 rounded-lg border border-cyan-500/20 font-semibold">
              {{ c.novedad_nueva }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw, 
  ArrowRight 
} from 'lucide-vue-next'
import type { CambiosResponse } from '@types'
import { useTouchSwipe } from '@composables/useTouchSwipe'

defineProps<{
  cambios: CambiosResponse | null
  totalCambios?: number
  month?: string
}>()

const activeChangeTab = ref<'entraron' | 'volvieron' | 'otros'>('entraron')

const { handleTouchStart, handleTouchEnd } = useTouchSwipe({
  tabs: ['entraron', 'volvieron', 'otros'],
  currentTab: activeChangeTab
})
</script>
