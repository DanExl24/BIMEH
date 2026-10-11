<template>
  <div class="space-y-4">
    <div class="flex items-center gap-2">
      <div class="w-2 h-4 bg-cyan-400 rounded-sm"></div>
      <h4 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">Configuración de la Carga</h4>
    </div>
    
    <!-- Data Source Switcher -->
    <div class="space-y-1.5">
      <label class="text-xs uppercase font-bold text-slate-300">Origen de los Datos:</label>
      <div class="grid grid-cols-2 gap-2 bg-darkBg p-1.5 rounded-2xl border border-darkBorder max-w-md shadow-inner">
        <button 
          type="button"
          @click="$emit('update:source', 'local')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="source === 'local' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <HardDrive class="w-4 h-4" />
          <span>Subir Archivo</span>
        </button>
        <button 
          type="button"
          @click="$emit('update:source', 'drive')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="source === 'drive' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <Cloud class="w-4 h-4" />
          <span>Google Drive</span>
        </button>
      </div>
    </div>

    <!-- Google Drive Connection Status & Reauthorization Card (Solo si origen es Drive) -->
    <div 
      v-if="source === 'drive'" 
      class="p-4 rounded-2xl border transition-all shadow-md"
      :class="driveConnected 
        ? 'bg-emerald-500/5 border-emerald-500/20' 
        : 'bg-amber-500/10 border-amber-500/30'"
    >
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <!-- Status Indicator & Text -->
        <div class="flex items-start sm:items-center gap-3">
          <div 
            class="w-3 h-3 rounded-full shrink-0 mt-0.5 sm:mt-0"
            :class="driveConnected 
              ? 'bg-emerald-400 shadow-lg shadow-emerald-400/50 animate-pulse' 
              : 'bg-amber-400 shadow-lg shadow-amber-400/50'"
          ></div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold" :class="driveConnected ? 'text-emerald-300' : 'text-amber-300'">
                {{ driveConnected ? 'Conexión a Google Drive Activa' : 'Google Drive Requiere Autorización' }}
              </span>
              <span 
                class="text-[10px] px-2 py-0.5 rounded-full font-mono font-semibold"
                :class="driveConnected ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-300'"
              >
                {{ driveConnected ? 'TOKEN VÁLIDO' : 'EXPIRADO O PENDIENTE' }}
              </span>
            </div>
            <p class="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
              {{ driveConnected 
                ? 'El servidor cuenta con credenciales activas para escanear y descargar reportes diarios.' 
                : 'Se requiere re-autorizar el acceso a Google Drive para descargar los reportes del servidor.' 
              }}
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center gap-2 shrink-0 self-end sm:self-auto">
          <button
            type="button"
            @click="$emit('refresh-drive')"
            :disabled="checkingDrive"
            class="p-2 bg-darkBg hover:bg-darkBorder/60 border border-darkBorder rounded-xl text-slate-300 hover:text-white transition-all text-xs font-bold cursor-pointer disabled:opacity-50"
            title="Verificar estado de la conexión"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': checkingDrive }" />
          </button>

          <button
            type="button"
            @click="$emit('reconnect-drive')"
            class="py-2 px-3.5 bg-gradient-to-r from-cyan-600/30 to-blue-600/30 hover:from-cyan-600/50 hover:to-blue-600/50 border border-cyan-500/40 rounded-xl text-cyan-300 hover:text-white transition-all text-xs font-bold cursor-pointer flex items-center gap-1.5 shadow-sm active:scale-95"
            title="Renovar o vincular token OAuth de Google Drive"
          >
            <ExternalLink class="w-3.5 h-3.5" />
            <span>Actualizar Sincronización a Google Drive</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Mode Switcher -->
    <div class="space-y-1.5">
      <label class="text-xs uppercase font-bold text-slate-300">Modo de Carga:</label>
      
      <!-- Si el origen es Google Drive: 3 modos (Por Días, Mes Completo, Todos los Meses) -->
      <div 
        v-if="source === 'drive'" 
        class="grid grid-cols-1 sm:grid-cols-3 gap-2 bg-darkBg p-1.5 rounded-2xl border border-darkBorder max-w-xl shadow-inner"
      >
        <button 
          type="button"
          @click="$emit('update:mode', 'dias')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'dias' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <CalendarDays class="w-4 h-4" />
          <span>Por Días</span>
        </button>
        <button 
          type="button"
          @click="$emit('update:mode', 'mes')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'mes' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <Calendar class="w-4 h-4" />
          <span>Mes Completo</span>
        </button>
        <button 
          type="button"
          @click="$emit('update:mode', 'todo')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'todo' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <CalendarRange class="w-4 h-4" />
          <span>Todos los Meses</span>
        </button>
      </div>

      <!-- Si el origen es Local: 2 modos (Por Días, Mes Completo) -->
      <div 
        v-else 
        class="grid grid-cols-2 gap-2 bg-darkBg p-1.5 rounded-2xl border border-darkBorder max-w-md shadow-inner"
      >
        <button 
          type="button"
          @click="$emit('update:mode', 'dias')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'dias' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <CalendarDays class="w-4 h-4" />
          <span>Por Días</span>
        </button>
        <button 
          type="button"
          @click="$emit('update:mode', 'mes')"
          class="py-2 px-3 text-xs font-bold rounded-xl transition-all cursor-pointer flex items-center justify-center gap-2 select-none"
          :class="mode === 'mes' ? 'bg-cyan-500/20 text-cyan-300 shadow-sm border border-cyan-500/30' : 'text-slate-400 hover:text-slate-200'"
        >
          <Calendar class="w-4 h-4" />
          <span>Mes Completo</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  HardDrive, 
  Cloud, 
  CalendarDays, 
  Calendar, 
  CalendarRange, 
  RefreshCw, 
  ExternalLink 
} from 'lucide-vue-next'

defineProps<{
  source: 'local' | 'drive'
  mode: 'dias' | 'mes' | 'todo'
  driveConnected?: boolean
  checkingDrive?: boolean
}>()

defineEmits<{
  (e: 'update:source', value: 'local' | 'drive'): void
  (e: 'update:mode', value: 'dias' | 'mes' | 'todo'): void
  (e: 'refresh-drive'): void
  (e: 'reconnect-drive'): void
}>()
</script>
