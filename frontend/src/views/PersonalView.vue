<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Search Bar & Controls Card -->
    <div class="glass-panel p-5 sm:p-6 rounded-3xl space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <div class="w-2 h-5 bg-cyan-400 rounded-sm"></div>
          <h3 class="text-sm font-bold text-slate-100 uppercase tracking-wider">
            Buscador del Personal Militar
          </h3>
        </div>

        <!-- View Switcher (Cards / Table) -->
        <div class="flex items-center bg-darkBg border border-darkBorder p-1 rounded-xl self-start sm:self-auto">
          <button 
            type="button"
            @click="viewMode = 'cards'"
            class="p-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 text-xs font-semibold select-none"
            :class="viewMode === 'cards' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
            title="Vista de Cuadrícula"
          >
            <LayoutGrid class="w-4 h-4" />
            <span class="hidden sm:inline">Tarjetas</span>
          </button>
          <button 
            type="button"
            @click="viewMode = 'table'"
            class="p-1.5 rounded-lg transition-all cursor-pointer flex items-center gap-1.5 text-xs font-semibold select-none"
            :class="viewMode === 'table' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'"
            title="Vista de Tabla"
          >
            <List class="w-4 h-4" />
            <span class="hidden sm:inline">Tabla</span>
          </button>
        </div>
      </div>

      <!-- Search Input -->
      <div class="relative">
        <input 
          type="text" 
          v-model="searchQuery" 
          @input="handleSearch"
          placeholder="Escribe apellidos, nombres o número de cédula (ej. Ramírez o 1015413550)..."
          class="w-full bg-darkBg border border-darkBorder rounded-2xl pl-12 pr-10 py-3.5 text-xs sm:text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/60 transition-all font-sans shadow-inner"
        />
        <Search class="w-5 h-5 absolute left-4 top-3.5 text-slate-400 pointer-events-none" />
        <button 
          v-if="searchQuery" 
          @click="searchQuery = ''; handleSearch()"
          class="absolute right-3.5 top-3.5 text-slate-400 hover:text-slate-200 p-0.5 rounded-md cursor-pointer"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- Helper / Suggestions -->
      <div class="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs text-slate-400 font-medium">
        <span>Búsqueda en tiempo real (mínimo 2 caracteres).</span>
        <div v-if="searchQuery.length < 2" class="flex items-center gap-1.5 flex-wrap">
          <span class="text-slate-500">Ejemplos:</span>
          <button 
            v-for="sug in sugerencias" 
            :key="sug" 
            type="button"
            @click="selectSuggestion(sug)"
            class="px-2.5 py-0.5 bg-darkBg border border-slate-700 hover:border-cyan-500/50 hover:text-cyan-300 rounded-full text-xs text-slate-300 transition-colors cursor-pointer"
          >
            {{ sug }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-3">
      <Loader2 class="w-8 h-8 text-cyan-400 animate-spin" />
      <p class="text-slate-400 text-xs font-semibold uppercase tracking-wider">Buscando en base de datos...</p>
    </div>

    <!-- Search Results -->
    <div v-else>
      <div v-if="results.length > 0">
        <!-- Result count badge -->
        <div class="flex items-center justify-between mb-4 px-1">
          <span class="text-xs text-slate-400 font-medium">
            Se encontraron <strong class="text-slate-100 font-bold">{{ results.length }}</strong> integrantes
          </span>
        </div>

        <!-- 1. CARDS VIEW -->
        <div v-if="viewMode === 'cards'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
          <div 
            v-for="p in results" 
            :key="p.cedula" 
            class="glass-panel-interactive p-5 rounded-2xl flex flex-col justify-between group"
          >
            <div>
              <div class="flex items-start justify-between gap-2">
                <span class="text-xs font-mono font-bold text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
                  C.C. {{ p.cedula }}
                </span>
                <span 
                  class="text-xs font-bold tracking-wider px-2.5 py-0.5 rounded-md border uppercase flex items-center gap-1.5"
                  :class="getStatusBadgeClass(p.estado)"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="p.estado === 'ACTIVO' ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'"></span>
                  {{ p.estado }}
                </span>
              </div>
              
              <h4 class="text-sm font-bold text-slate-100 mt-3 group-hover:text-cyan-300 uppercase tracking-tight line-clamp-1 transition-colors">
                <router-link :to="`/personal/${p.cedula}`">{{ p.nombre }}</router-link>
              </h4>
            </div>

            <div class="mt-4 pt-3.5 border-t border-darkBorder/60 flex items-center justify-between">
              <span v-if="p.fecha_retiro" class="text-xs text-red-400 font-medium flex items-center gap-1">
                <UserX class="w-3.5 h-3.5 shrink-0" />
                Retirado: <span class="font-mono font-bold">{{ p.fecha_retiro }}</span>
              </span>
              <span v-else class="text-xs text-emerald-400 font-medium flex items-center gap-1">
                <UserCheck class="w-3.5 h-3.5 shrink-0" />
                Personal Activo
              </span>
              
              <router-link 
                :to="`/personal/${p.cedula}`" 
                class="text-xs text-cyan-400 font-bold flex items-center gap-1 hover:text-cyan-300 transition-colors group-hover:translate-x-0.5"
              >
                <span>Expediente</span>
                <ArrowRight class="w-3.5 h-3.5" />
              </router-link>
            </div>
          </div>
        </div>

        <!-- 2. TABLE VIEW -->
        <div v-else class="glass-panel rounded-2xl border border-darkBorder overflow-hidden shadow-xl">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse min-w-[650px]">
              <thead>
                <tr class="border-b border-darkBorder text-xs text-slate-400 uppercase font-semibold bg-darkBg/60">
                  <th class="py-3 px-4">Cédula</th>
                  <th class="py-3 px-4">Apellidos y Nombres</th>
                  <th class="py-3 px-4 text-center">Estado</th>
                  <th class="py-3 px-4">Fecha Retiro</th>
                  <th class="py-3 px-4 text-right">Acción</th>
                </tr>
              </thead>
              <tbody class="text-xs">
                <tr 
                  v-for="p in results" 
                  :key="p.cedula"
                  class="border-b border-darkBorder/40 hover:bg-slate-800/30 transition-colors"
                >
                  <td class="py-3 px-4 font-mono font-bold text-slate-300">{{ p.cedula }}</td>
                  <td class="py-3 px-4 font-bold text-slate-100 uppercase hover:text-cyan-400">
                    <router-link :to="`/personal/${p.cedula}`">{{ p.nombre }}</router-link>
                  </td>
                  <td class="py-3 px-4 text-center">
                    <span 
                      class="text-xs font-bold px-2.5 py-0.5 rounded-md border uppercase inline-flex items-center gap-1"
                      :class="getStatusBadgeClass(p.estado)"
                    >
                      <span class="w-1.5 h-1.5 rounded-full" :class="p.estado === 'ACTIVO' ? 'bg-emerald-400' : 'bg-red-400'"></span>
                      {{ p.estado }}
                    </span>
                  </td>
                  <td class="py-3 px-4 font-mono text-slate-400">
                    {{ p.fecha_retiro || '-' }}
                  </td>
                  <td class="py-3 px-4 text-right">
                    <router-link 
                      :to="`/personal/${p.cedula}`" 
                      class="inline-flex items-center gap-1 text-xs font-bold text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/20 px-3 py-1 rounded-lg border border-cyan-500/20 transition-all"
                    >
                      <span>Ver Expediente</span>
                      <ArrowRight class="w-3 h-3" />
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- No Results / Empty State -->
      <div v-else class="glass-panel p-8 sm:p-14 rounded-3xl text-center space-y-4">
        <div class="w-16 h-16 bg-darkBg border border-slate-700 rounded-2xl flex items-center justify-center mx-auto text-slate-400 shadow-inner">
          <Users class="w-8 h-8 stroke-[1.5]" />
        </div>
        <div class="max-w-md mx-auto space-y-2">
          <h4 class="text-base font-bold text-slate-200">
            {{ searchQuery.length >= 2 ? 'No se encontraron resultados' : 'Buscador de Historial y Expedientes' }}
          </h4>
          <p class="text-xs text-slate-400 leading-relaxed">
            {{ searchQuery.length >= 2 ? 'Verifica el número de cédula o los apellidos ingresados. Asegúrate de escribir al menos 2 caracteres.' : 'Ingresa la cédula o apellidos de un oficial, suboficial o soldado para consultar su hoja de ruta, mapa de calor y registro diario.' }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  Search, 
  LayoutGrid, 
  List, 
  X, 
  Loader2, 
  UserCheck, 
  UserX, 
  ArrowRight, 
  Users 
} from 'lucide-vue-next'
import { usePersonalAutocomplete } from '../composables/usePersonalAutocomplete'
import { getStatusBadgeClass } from '../utils/personal.utils'

const { searchQuery, loading, results, handleSearch, selectSuggestion } = usePersonalAutocomplete()

const viewMode = ref<'cards' | 'table'>('cards')

const sugerencias = [
  'LIZARAZO',
  'SANTODOMINGO',
  'RAMIREZ',
  '74754804',
  '1015413550'
]
</script>

