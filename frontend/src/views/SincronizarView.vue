<template>
  <div class="space-y-6">
    <!-- Header Card -->
    <div class="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
          <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Carga y Sincronización de Reportes
        </h3>
        <p class="text-xs text-slate-500 mt-1 font-sans">
          Sube tus reportes diarios o mensuales en formato Excel o JSON para actualizar los datos operacionales.
        </p>
      </div>

      <!-- Template Download Buttons -->
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-[10px] uppercase font-bold text-slate-400 font-sans mr-2">Descargar Plantillas:</span>
        <a 
          :href="`${appStore.apiBase}/api/sincronizar/plantilla/excel`" 
          download
          class="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 hover:border-emerald-500/40 rounded-xl text-[10px] font-bold text-emerald-400 flex items-center gap-1.5 transition-all select-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h7a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          </svg>
          PLANTILLA EXCEL
        </a>
        <a 
          :href="`${appStore.apiBase}/api/sincronizar/plantilla/json`" 
          download
          class="px-3 py-1.5 bg-slate-500/10 border border-slate-500/20 hover:border-slate-500/40 rounded-xl text-[10px] font-bold text-slate-300 flex items-center gap-1.5 transition-all select-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h7a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          </svg>
          PLANTILLA JSON
        </a>
      </div>
    </div>

    <!-- Main Form Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Left Column: Settings and File Dropzone -->
      <div class="glass-panel p-6 rounded-2xl lg:col-span-2 space-y-6 flex flex-col justify-between">
        <div class="space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">Configuración de la Carga</h4>
          
          <!-- Mode switch -->
          <div class="space-y-1.5">
            <label class="text-[10px] uppercase font-bold text-slate-500">Modo de Carga:</label>
            <div class="grid grid-cols-2 gap-2 bg-darkBg p-1 rounded-xl border border-darkBorder/40 max-w-sm">
              <button 
                type="button"
                @click="mode = 'dia'"
                class="py-1.5 text-xs font-bold rounded-lg transition-all"
                :class="mode === 'dia' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
              >
                Por Día Operativo
              </button>
              <button 
                type="button"
                @click="mode = 'mes'"
                class="py-1.5 text-xs font-bold rounded-lg transition-all"
                :class="mode === 'mes' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
              >
                Por Mes Completo
              </button>
            </div>
          </div>

          <!-- Dynamic inputs based on mode -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Day selection (DatePicker) -->
            <div v-if="mode === 'dia'" class="space-y-1.5">
              <label class="text-[10px] uppercase font-bold text-slate-500">Fecha del Reporte:</label>
              <input 
                type="date" 
                v-model="fecha"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              />
            </div>

            <!-- Month selection (Dropdown) -->
            <div v-else class="space-y-1.5">
              <label class="text-[10px] uppercase font-bold text-slate-500">Mes a Cargar:</label>
              <select 
                v-model="mes"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
              >
                <option v-for="m in appStore.months" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Overwrite Checkbox -->
            <div class="flex items-center gap-2 pt-5 select-none">
              <input 
                type="checkbox" 
                id="overwriteCheck"
                v-model="overwrite"
                class="w-4 h-4 rounded bg-darkBg border-darkBorder text-cyan-500 focus:ring-cyan-500/20 focus:ring-offset-0"
              />
              <label for="overwriteCheck" class="text-xs text-slate-300 font-medium cursor-pointer">
                Sobreescribir reporte si ya existe
              </label>
            </div>
          </div>

          <!-- File Upload Dropzone -->
          <div class="space-y-1.5 pt-2">
            <label class="text-[10px] uppercase font-bold text-slate-500">Archivo del Reporte:</label>
            
            <div 
              @dragover.prevent="dragActive = true"
              @dragleave.prevent="dragActive = false"
              @drop.prevent="handleDrop"
              @click="$refs.fileInput.click()"
              class="border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center space-y-3"
              :class="dragActive ? 'border-cyan-400 bg-cyan-500/5 shadow-md shadow-cyan-500/5' : 'border-darkBorder hover:border-slate-600 bg-darkBg/30'"
            >
              <input 
                type="file" 
                ref="fileInput" 
                @change="handleFileSelected" 
                accept=".xlsx, .xls, .json" 
                class="hidden" 
              />
              
              <div class="w-12 h-12 bg-darkBg/60 rounded-full flex items-center justify-center text-slate-400 border border-darkBorder">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </div>
              
              <div v-if="!selectedFile" class="space-y-1">
                <p class="text-xs text-slate-300 font-semibold">
                  Arrastra tu archivo aquí o <span class="text-cyan-400 hover:text-cyan-300">búscalo</span>
                </p>
                <p class="text-[10px] text-slate-500 font-sans">
                  Soporta formatos Excel (.xlsx, .xls) y JSON (.json)
                </p>
              </div>

              <!-- Selected File Display -->
              <div v-else class="flex items-center gap-3 p-3 bg-darkCard/80 border border-darkBorder rounded-xl max-w-md w-full text-left">
                <div class="w-9 h-9 rounded bg-cyan-500/10 flex items-center justify-center text-cyan-400 font-bold text-xs uppercase font-mono">
                  {{ fileExtension }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-bold text-slate-300 truncate font-mono">{{ selectedFile.name }}</p>
                  <p class="text-[10px] text-slate-500 font-sans">{{ formattedFileSize }}</p>
                </div>
                <button 
                  type="button"
                  @click.stop="clearFile" 
                  class="text-slate-400 hover:text-red-400 p-1 rounded-lg hover:bg-red-500/10 transition-colors"
                >
                  &times;
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-4 border-t border-darkBorder/40 flex justify-end">
          <button 
            type="button"
            @click="submitReport"
            :disabled="!selectedFile || (mode === 'dia' && !fecha) || (mode === 'mes' && !mes) || loadingSubmit"
            class="px-5 py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:pointer-events-none rounded-xl text-xs font-bold text-slate-100 flex items-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer select-none"
          >
            <div v-if="loadingSubmit" class="w-4 h-4 border-2 border-slate-100/25 border-t-slate-100 rounded-full animate-spin"></div>
            <span v-else>Sincronizar Reporte</span>
          </button>
        </div>
      </div>

      <!-- Right Column: Status Alert & Gaps Summary -->
      <div class="space-y-6">
        <!-- Operation Results & Alerts Card -->
        <div class="glass-panel p-6 rounded-2xl space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">Resultado de la Operación</h4>
          
          <!-- Google Drive Sync Status in Results Card -->
          <div v-if="appStore.syncStatus !== 'idle'" class="space-y-3">
            <!-- Running -->
            <div v-if="appStore.syncStatus === 'running'" class="bg-cyan-500/10 border border-cyan-500/25 p-4 rounded-xl space-y-2 text-cyan-400 font-sans">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <div class="w-4 h-4 border-2 border-cyan-400/25 border-t-cyan-400 rounded-full animate-spin"></div>
                Sincronizando con Google Drive...
              </div>
              <p class="text-xs leading-relaxed text-cyan-300/90 font-medium">
                Descargando y actualizando reportes desde la nube. Por favor espere.
              </p>
              <div class="text-[10px] font-mono text-cyan-400 bg-cyan-500/15 px-2 py-1 rounded-md inline-block font-bold mt-2">
                Tiempo transcurrido: {{ Math.floor(appStore.syncSecondsElapsed / 60) }}m {{ appStore.syncSecondsElapsed % 60 }}s
              </div>
            </div>

            <!-- Success -->
            <div v-else-if="appStore.syncStatus === 'success'" class="space-y-3">
              <div class="bg-emerald-500/10 border border-emerald-500/25 p-4 rounded-xl space-y-2 text-emerald-400 font-sans">
                <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Sincronización de Drive Completada
                </div>
                <p class="text-xs leading-relaxed text-emerald-300/90 font-medium">
                  {{ appStore.syncMessage }}
                </p>
              </div>

              <!-- Corrupted/Failed Files Log -->
              <div v-if="appStore.syncErrors.length > 0" class="space-y-2 pt-1">
                <div class="flex items-center justify-between">
                  <span class="text-[10px] uppercase font-bold text-red-400 font-sans">Archivos Omitidos/Corruptos:</span>
                  <span class="text-[10px] font-bold text-slate-500 font-sans">{{ appStore.syncErrors.length }} archivo(s)</span>
                </div>
                <div class="max-h-48 overflow-y-auto bg-red-950/20 border border-red-500/20 rounded-xl p-3 font-mono text-[10px] space-y-2.5">
                  <div v-for="(err, idx) in appStore.syncErrors" :key="idx" class="border-b border-red-500/10 pb-2 last:border-0 last:pb-0">
                    <div class="font-bold text-red-300 truncate">{{ err.file }}</div>
                    <div class="text-slate-400 mt-0.5 leading-relaxed">{{ err.error }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Error -->
            <div v-else-if="appStore.syncStatus === 'error'" class="bg-red-500/10 border border-red-500/25 p-4 rounded-xl space-y-2 text-red-400 font-sans">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Error en Sincronización de Drive
              </div>
              <p class="text-xs leading-relaxed text-red-300/90 font-medium">
                {{ appStore.syncMessage }}
              </p>
            </div>
            
            <!-- Clear button to return to placeholder -->
            <div class="flex justify-end pt-1">
              <button 
                type="button"
                @click="appStore.syncStatus = 'idle'; appStore.syncErrors = []"
                class="px-3 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-[10px] font-bold text-slate-400 transition-all cursor-pointer"
              >
                Limpiar Historial
              </button>
            </div>
          </div>

          <!-- Local Upload Status -->
          <div v-else>
            <!-- Default placeholder -->
            <div v-if="!statusState" class="text-center py-12 text-slate-500 space-y-2">
              <div class="w-10 h-10 rounded-full bg-darkBg/40 border border-darkBorder flex items-center justify-center mx-auto text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p class="text-xs">Configure las opciones, arrastre su reporte e inicie la sincronización.</p>
            </div>

            <!-- Success Alert -->
            <div v-else-if="statusState === 'success'" class="bg-emerald-500/10 border border-emerald-500/25 p-4 rounded-xl space-y-2 text-emerald-400 font-sans">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Sincronización Exitosa
              </div>
              <p class="text-xs leading-relaxed text-emerald-300/90 font-medium">
                {{ statusMessage }}
              </p>
            </div>

            <!-- Danger/Validation Alert -->
            <div v-else-if="statusState === 'error'" class="bg-red-500/10 border border-red-500/25 p-4 rounded-xl space-y-2 text-red-400 font-sans">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Error de Validación
              </div>
              <p class="text-xs leading-relaxed text-red-300/90 font-medium">
                {{ statusMessage }}
              </p>
            </div>

            <!-- Conflict Alert -->
            <div v-else-if="statusState === 'conflict'" class="bg-amber-500/10 border border-amber-500/25 p-4 rounded-xl space-y-3 text-amber-500 font-sans">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Conflicto de Duplicados
              </div>
              <p class="text-xs leading-relaxed text-amber-200/90 font-medium">
                {{ statusMessage }}
              </p>
              
              <!-- Conflict list -->
              <div class="max-h-24 overflow-y-auto bg-darkBg/60 border border-darkBorder/40 rounded-lg p-2 font-mono text-[10px] text-amber-300">
                <div v-for="c in conflicts" :key="c">{{ c }}</div>
              </div>

              <!-- Overwrite decision button -->
              <button 
                type="button"
                @click="confirmOverwrite"
                class="w-full py-2 bg-amber-600 hover:bg-amber-500 rounded-lg text-slate-100 font-bold text-xs transition-all shadow active:scale-95 cursor-pointer"
              >
                Sobreescribir y Cargar
              </button>
            </div>
          </div>
        </div>

        <!-- Google Drive Sync Card -->
        <div class="glass-panel p-6 rounded-2xl space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono flex items-center gap-1.5">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            Sincronización con Google Drive
          </h4>
          <p class="text-[11px] text-slate-500 font-sans leading-relaxed">
            Busca y descarga los archivos de reportes más recientes que se hayan subido a Google Drive de forma automática.
          </p>
          <button 
            type="button"
            @click="appStore.startDriveSync()"
            :disabled="appStore.isSyncingDrive"
            class="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:pointer-events-none rounded-xl text-xs font-bold text-slate-100 flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer select-none"
          >
            <div v-if="appStore.isSyncingDrive" class="w-4 h-4 border-2 border-slate-100/25 border-t-slate-100 rounded-full animate-spin"></div>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            <span>Descargar de Google Drive</span>
          </button>
        </div>

        <!-- Instructions Panel -->
        <div class="glass-panel p-6 rounded-2xl space-y-4">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">Reglas de Sincronización</h4>
          <ul class="text-[11px] text-slate-500 space-y-2 list-disc pl-4 font-sans leading-relaxed">
            <li>El archivo debe contener las cabeceras/columnas obligatorias: <span class="text-slate-300 font-mono">CEDULA</span>, <span class="text-slate-300 font-mono">APELLIDOS Y NOMBRES</span> y <span class="text-slate-300 font-mono">SUBNOVEDAD</span>.</li>
            <li>Si sube registros con cédulas que no se encuentran en la base de datos de personal, el sistema las registrará automáticamente de manera activa.</li>
            <li>Si no se define una subnovedad en un registro, el sistema le asignará el estado por defecto <span class="text-emerald-400 font-bold">SIN NOVEDAD (Disponible)</span>.</li>
            <li>Las fechas iniciales y finales de novedades se normalizan en formato ISO <span class="text-slate-400 font-mono">YYYY-MM-DD</span>.</li>
          </ul>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const appStore = useAppStore()

// State variables
const mode = ref<'dia' | 'mes'>('dia')
const fecha = ref('2026-05-07')
const mes = ref('MAYO')
const overwrite = ref(false)

const selectedFile = ref<File | null>(null)
const dragActive = ref(false)

const loadingSubmit = ref(false)
const statusState = ref<'success' | 'error' | 'conflict' | null>(null)
const statusMessage = ref('')
const conflicts = ref<string[]>([])

// Computeds
const fileExtension = computed(() => {
  if (!selectedFile.value) return ''
  const parts = selectedFile.value.name.split('.')
  return parts.length > 1 ? parts.pop() : ''
})

const formattedFileSize = computed(() => {
  if (!selectedFile.value) return '0 B'
  const kb = selectedFile.value.size / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
})

// Methods
const handleDrop = (e: DragEvent) => {
  dragActive.value = false
  if (e.dataTransfer && e.dataTransfer.files.length > 0) {
    validateAndAssignFile(e.dataTransfer.files[0])
  }
}

const handleFileSelected = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    validateAndAssignFile(target.files[0])
  }
}

const validateAndAssignFile = (file: File) => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (ext === 'xlsx' || ext === 'xls' || ext === 'json') {
    selectedFile.value = file
    statusState.value = null
    statusMessage.value = ''
  } else {
    statusState.value = 'error'
    statusMessage.value = 'Formato de archivo no soportado. Debe seleccionar un archivo .xlsx, .xls o .json.'
    selectedFile.value = null
  }
}

const clearFile = () => {
  selectedFile.value = null
  statusState.value = null
  statusMessage.value = ''
}

const confirmOverwrite = () => {
  overwrite.value = true
  submitReport()
}

const submitReport = async () => {
  if (!selectedFile.value) return
  
  loadingSubmit.value = true
  statusState.value = null
  statusMessage.value = ''
  conflicts.value = []
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('tipo', mode.value)
  formData.append('overwrite', overwrite.value ? 'true' : 'false')
  
  if (mode.value === 'dia') {
    formData.append('fecha', fecha.value)
  } else {
    formData.append('mes', mes.value)
  }
  
  try {
    const token = localStorage.getItem('bimej12_auth_token')
    const res = await fetch(`${appStore.apiBase}/api/sincronizar/cargar`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData
    })
    
    const data = await res.json()
    
    if (res.status === 400 && data.detail) {
      statusState.value = 'error'
      statusMessage.value = data.detail
    } else if (data.status === 'conflict') {
      statusState.value = 'conflict'
      statusMessage.value = data.message
      conflicts.value = data.conflicts
    } else if (data.status === 'success') {
      statusState.value = 'success'
      statusMessage.value = data.message
      
      // Update appStore global states (like total dates list)
      appStore.fetchAvailableDates()
    } else {
      statusState.value = 'error'
      statusMessage.value = data.detail || 'Ocurrió un error inesperado al sincronizar.'
    }
  } catch (error: any) {
    console.error('Error uploading file:', error)
    statusState.value = 'error'
    statusMessage.value = 'Error al conectar con el servidor. Verifique que la API esté encendida.'
  } finally {
    loadingSubmit.value = false
  }
}
</script>
