<template>
  <div class="space-y-4">
    <!-- Progress Indicator -->
    <div v-if="isSyncing" class="bg-cyan-500/10 border border-cyan-500/25 p-4 rounded-xl space-y-2 text-cyan-400 font-sans animate-pulse">
      <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
        <div class="w-4 h-4 border-2 border-cyan-400/25 border-t-cyan-400 rounded-full animate-spin"></div>
        Sincronizando desde Google Drive...
      </div>
      <p class="text-xs leading-relaxed text-cyan-300/90 font-medium">
        Descargando y actualizando reportes desde la nube. Por favor espere.
      </p>
      <div class="text-[10px] font-mono text-cyan-400 bg-cyan-500/15 px-2 py-1 rounded-md inline-block font-bold mt-2">
        Tiempo transcurrido: {{ Math.floor(syncSecondsElapsed / 60) }}m {{ syncSecondsElapsed % 60 }}s
      </div>
    </div>

    <!-- Success -->
    <div v-else-if="syncStatus === 'success'" class="space-y-3">
      <div class="bg-emerald-500/10 border border-emerald-500/25 p-4 rounded-xl space-y-2 text-emerald-400 font-sans">
        <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Sincronización de Drive Completada
        </div>
        <p class="text-xs leading-relaxed text-emerald-300/90 font-medium">
          {{ syncMessage }}
        </p>
      </div>

      <!-- Sync Log -->
      <div v-if="syncLogs.length > 0" class="space-y-3 pt-2">
        <div class="flex items-center justify-between">
          <span class="text-[10px] uppercase font-bold text-slate-400 font-sans tracking-wide">Registro de la Sincronización:</span>
          <!-- Download Log Button -->
          <button 
            type="button" 
            @click="$emit('download-log')" 
            class="px-2.5 py-1 text-[9px] font-bold text-cyan-400 hover:text-cyan-300 bg-cyan-500/10 hover:bg-cyan-500/15 border border-cyan-500/20 rounded-lg flex items-center gap-1 transition-all cursor-pointer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Descargar Log (.txt)
          </button>
        </div>
        
        <div class="max-h-64 overflow-y-auto border border-darkBorder/40 rounded-xl divide-y divide-darkBorder/25 bg-slate-950/20 font-sans text-xs">
          <div v-for="(log, idx) in syncLogs" :key="idx" class="p-3 flex items-start gap-2.5">
            <span class="mt-0.5">
              <span v-if="log.status === 'success'" class="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span>
              <span v-else-if="log.status === 'skipped'" class="w-2 h-2 rounded-full bg-slate-400 inline-block"></span>
              <span v-else class="w-2 h-2 rounded-full bg-rose-500 inline-block"></span>
            </span>
            
            <div class="flex-1 min-w-0 space-y-0.5">
              <div class="font-bold text-slate-200 truncate text-[11px] font-mono">{{ log.file }}</div>
              <div class="text-[10px]" :class="log.status === 'success' ? 'text-emerald-400/90' : log.status === 'skipped' ? 'text-slate-400/90' : 'text-rose-400/90'">
                {{ log.detail }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="syncStatus === 'error'" class="bg-red-500/10 border border-red-500/25 p-4 rounded-xl space-y-2 text-red-400 font-sans">
      <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        Error en Sincronización de Drive
      </div>
      <p class="text-xs leading-relaxed text-red-300/90 font-medium">
        {{ syncMessage }}
      </p>
    </div>
    
    <!-- Clear button -->
    <div v-if="syncStatus !== 'idle'" class="flex justify-end pt-1">
      <button 
        type="button" 
        @click="$emit('clear-history')" 
        class="px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-[10px] font-bold text-slate-400 transition-all cursor-pointer"
      >
        Limpiar Historial
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { SyncLog } from '../../types'

defineProps<{
  isSyncing: boolean
  syncSecondsElapsed: number
  syncStatus: string
  syncMessage: string
  syncLogs: SyncLog[]
}>()

defineEmits<{
  (e: 'download-log'): void
  (e: 'clear-history'): void
}>()
</script>
