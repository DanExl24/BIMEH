<template>
  <div class="space-y-6">
    <!-- Search Bar & Controls -->
    <div class="glass-panel p-6 rounded-2xl space-y-4">
      <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
        <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Buscar Integrante del Personal
      </h3>
      <div class="flex gap-4">
        <div class="flex-1 relative">
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="handleSearch"
            placeholder="Escribe el nombre o número de cédula del personal (ej. Ramírez o 1015413550)..."
            class="w-full bg-darkBg border border-darkBorder rounded-xl pl-12 pr-4 py-3 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
          />
          <div class="absolute left-4 top-3.5 text-slate-500">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="2 2 20 20" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
      </div>
      <p class="text-xs text-slate-500 font-mono">Búsqueda rápida en base de datos. Se requiere un mínimo de 2 caracteres.</p>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-10 h-10 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
      <p class="text-slate-400 text-sm">Buscando en personal...</p>
    </div>

    <!-- Search Results -->
    <div v-else>
      <div v-if="results.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="p in results" 
          :key="p.cedula" 
          class="glass-panel-interactive p-5 rounded-2xl flex flex-col justify-between"
        >
          <div>
            <div class="flex items-start justify-between">
              <span class="text-[10px] font-mono text-slate-500">C.C. {{ p.cedula }}</span>
              <span 
                class="text-[9px] font-bold tracking-wider px-2 py-0.5 rounded border uppercase"
                :class="p.estado === 'ACTIVO' ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400' : 'bg-red-500/10 border-red-500/25 text-red-400'"
              >
                {{ p.estado }}
              </span>
            </div>
            
            <h4 class="text-sm font-bold text-slate-200 mt-2 hover:text-cyan-400 uppercase tracking-tight line-clamp-1">
              <router-link :to="`/personal/${p.cedula}`">{{ p.nombre }}</router-link>
            </h4>
          </div>

          <div class="mt-4 pt-4 border-t border-darkBorder/40 flex items-center justify-between">
            <span v-if="p.fecha_retiro" class="text-[10px] text-slate-500">
              Retirado: <span class="font-mono text-red-400">{{ p.fecha_retiro }}</span>
            </span>
            <span v-else class="text-[10px] text-emerald-400 flex items-center gap-1">
              <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span> Integrante Activo
            </span>
            
            <router-link 
              :to="`/personal/${p.cedula}`" 
              class="text-xs text-cyan-400 font-semibold flex items-center gap-1 hover:text-cyan-300 transition-colors"
            >
              Ver Historial &rarr;
            </router-link>
          </div>
        </div>
      </div>

      <!-- No Results/Default view -->
      <div v-else class="glass-panel p-12 rounded-2xl text-center space-y-4">
        <div class="w-16 h-16 bg-darkBg/60 rounded-full flex items-center justify-center mx-auto text-slate-500 border border-darkBorder">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div class="max-w-md mx-auto space-y-2">
          <h4 class="text-md font-bold text-slate-300">
            {{ searchQuery.length >= 2 ? 'No se encontraron resultados' : 'Buscador de Historial Personal' }}
          </h4>
          <p class="text-sm text-slate-500">
            {{ searchQuery.length >= 2 ? 'Verifica el número de cédula o los apellidos escritos. Asegúrate de escribir al menos 2 letras o números.' : 'Ingresa la cédula o apellidos de un oficial, suboficial o soldado para ver su hoja de ruta de disponibilidad, estadísticas acumuladas y reporte de novedades durante el año.' }}
          </p>
        </div>
        
        <!-- Suggestions -->
        <div v-if="searchQuery.length < 2" class="pt-4 border-t border-darkBorder/40 max-w-lg mx-auto">
          <span class="text-[10px] text-slate-500 uppercase tracking-wider block mb-2">Búsquedas sugeridas:</span>
          <div class="flex flex-wrap justify-center gap-2">
            <button 
              v-for="sug in sugerencias" 
              :key="sug" 
              @click="selectSugerencia(sug)"
              class="px-3 py-1 bg-darkBg border border-darkBorder rounded-full text-xs text-slate-400 hover:border-cyan-500/50 hover:text-cyan-400 transition-colors"
            >
              {{ sug }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { buscarPersonal } from '../services/api'
import type { PersonalSearchResult } from '../types'

const searchQuery = ref('')
const loading = ref(false)
const results = ref<PersonalSearchResult[]>([])

const sugerencias = [
  'LIZARAZO',
  'SANTODOMINGO',
  'RAMIREZ',
  '74754804',
  '1015413550',
  '1007404782'
]

let timeout: number | null = null

const handleSearch = () => {
  if (timeout) clearTimeout(timeout)
  
  if (searchQuery.value.trim().length < 2) {
    results.value = []
    return
  }
  
  loading.value = true
  timeout = window.setTimeout(async () => {
    try {
      results.value = await buscarPersonal(searchQuery.value)
      loading.value = false
    } catch (e) {
      console.error('Error fetching personnel:', e)
      loading.value = false
    }
  }, 350)
}

const selectSugerencia = (sug: string) => {
  searchQuery.value = sug
  handleSearch()
}
</script>
