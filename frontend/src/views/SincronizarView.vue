<template>
  <div class="space-y-6">
    <!-- Header Card con descarga de plantillas -->
    <SyncTemplateDownload :api-base="appStore.apiBase" />

    <!-- Main Form Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
      <!-- Left Column: Settings and File Dropzone -->
      <div class="glass-panel p-5 sm:p-7 rounded-3xl lg:col-span-2 space-y-6 flex flex-col justify-between border border-darkBorder shadow-xl">
        <div class="space-y-5">
          <!-- Selectores de origen y modo -->
          <SyncSourceSelector 
            v-model:source="source" 
            v-model:mode="mode" 
          />

          <!-- Inputs dinámicos según el modo -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Multi-day calendar picker -->
            <SyncMultiDayCalendar 
              v-if="mode === 'dias'"
              v-model:multi-day-month="multiDayMonth"
              :months="appStore.months"
              :selected-dates="selectedDates"
              :calendar-days="calendarDays"
              :calendar-padding="calendarPadding"
              @toggle-day="toggleDay"
              @select-all="selectAllDays"
              @clear-all="clearAllDays"
            />

            <!-- Month selection (Dropdown) -->
            <div v-else class="space-y-1.5">
              <label class="text-xs uppercase font-bold text-slate-300">Mes a Cargar:</label>
              <select 
                v-model="mes"
                class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2.5 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 cursor-pointer shadow-sm"
              >
                <option v-for="m in appStore.months" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Overwrite Checkbox -->
            <div class="flex items-center gap-2.5 pt-4 select-none">
              <input 
                type="checkbox" 
                id="overwriteCheck"
                v-model="overwrite"
                class="w-4 h-4 rounded bg-darkBg border-slate-700 text-cyan-500 focus:ring-cyan-500/20 focus:ring-offset-0 cursor-pointer"
              />
              <label for="overwriteCheck" class="text-xs text-slate-200 font-semibold cursor-pointer">
                Sobreescribir reporte si ya existe
              </label>
            </div>
          </div>

          <!-- File Upload Dropzone (Local mode) -->
          <SyncFileDropzone 
            v-if="source === 'local'"
            :selected-file="selectedFile"
            :file-extension="fileExtension"
            :formatted-file-size="formattedFileSize"
            @file-selected="handleFileSelected"
            @file-dropped="handleDrop"
            @clear-file="clearFile"
          />
        </div>

        <!-- Submit Buttons -->
        <div class="pt-6 border-t border-darkBorder/60 flex items-center justify-end gap-3">
          <button 
            type="button"
            @click="handleMainAction"
            :disabled="isSubmitDisabled"
            class="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 disabled:pointer-events-none rounded-xl text-xs font-bold text-white flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer select-none"
          >
            <Loader2 v-if="loadingSubmit || appStore.isSyncingDrive" class="w-4 h-4 animate-spin" />
            <Upload v-else-if="source === 'local'" class="w-4 h-4 stroke-[2.5]" />
            <Cloud v-else class="w-4 h-4 stroke-[2.5]" />
            <span>{{ mainButtonText }}</span>
          </button>
        </div>
      </div>

      <!-- Right Column: Status & Drive Full Sync -->
      <div class="space-y-6">
        <!-- Status Card -->
        <div class="glass-panel p-5 sm:p-6 rounded-3xl space-y-4 border border-darkBorder shadow-xl">
          <div class="flex items-center gap-2 border-b border-darkBorder/60 pb-3">
            <Activity class="w-4 h-4 text-cyan-400" />
            <h4 class="text-xs font-bold text-slate-100 uppercase tracking-wider">Estado del Proceso</h4>
          </div>
          
          <!-- Drive Status -->
          <SyncDriveProgress 
            v-if="source === 'drive'"
            :is-syncing="appStore.isSyncingDrive"
            :sync-seconds-elapsed="appStore.syncSecondsElapsed"
            :sync-status="appStore.syncStatus"
            :sync-message="appStore.syncMessage"
            :sync-logs="appStore.syncLogs"
            @download-log="handleDownloadSyncLog"
            @clear-history="appStore.syncStatus = 'idle'; appStore.syncErrors = []"
          />

          <!-- Local Upload Status -->
          <div v-else>
            <!-- Default placeholder -->
            <div v-if="!statusState" class="text-center py-10 text-slate-400 space-y-2">
              <div class="w-12 h-12 rounded-2xl bg-darkBg border border-darkBorder flex items-center justify-center mx-auto text-slate-500 shadow-inner">
                <Info class="w-6 h-6 stroke-[1.5]" />
              </div>
              <p class="text-xs font-medium max-w-xs mx-auto">Configure las opciones, arrastre su reporte e inicie la sincronización.</p>
            </div>

            <!-- Success Alert -->
            <div v-else-if="statusState === 'success'" class="bg-emerald-500/15 border border-emerald-500/30 p-4 rounded-2xl space-y-1.5 text-emerald-300 shadow-sm">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <CheckCircle2 class="w-4 h-4 stroke-[2.5]" />
                <span>Sincronización Exitosa</span>
              </div>
              <p class="text-xs leading-relaxed text-emerald-200 font-medium">
                {{ statusMessage }}
              </p>
            </div>

            <!-- Danger/Validation Alert -->
            <div v-else-if="statusState === 'error'" class="bg-red-500/15 border border-red-500/30 p-4 rounded-2xl space-y-1.5 text-red-300 shadow-sm">
              <div class="flex items-center gap-2 font-bold text-xs uppercase tracking-wide">
                <AlertCircle class="w-4 h-4 stroke-[2.5]" />
                <span>Error de Validación</span>
              </div>
              <p class="text-xs leading-relaxed text-red-200 font-medium">
                {{ statusMessage }}
              </p>
            </div>

            <!-- Conflict Alert -->
            <SyncConflictAlert 
              :status-state="statusState"
              :status-message="statusMessage"
              :conflicts="conflicts"
              @confirm-overwrite="confirmOverwrite"
            />
          </div>
        </div>

        <!-- Google Drive Full Sync Card -->
        <div class="glass-panel p-5 sm:p-6 rounded-3xl space-y-4 border border-darkBorder shadow-xl">
          <div class="flex items-center gap-2">
            <Cloud class="w-4 h-4 text-cyan-400" />
            <h4 class="text-xs font-bold text-slate-100 uppercase tracking-wider">
              Sincronización Completa Drive
            </h4>
          </div>
          <p class="text-xs text-slate-400 leading-relaxed font-medium">
            Busca y descarga de forma masiva todos los reportes de meses y días faltantes en la base de datos de manera automática.
          </p>
          <button 
            type="button"
            @click="appStore.startDriveSync({ tipo: 'todo', overwrite: false })"
            :disabled="appStore.isSyncingDrive"
            class="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 disabled:pointer-events-none rounded-xl text-xs font-bold text-white flex items-center justify-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer select-none"
          >
            <Loader2 v-if="appStore.isSyncingDrive" class="w-4 h-4 animate-spin" />
            <Cloud v-else class="w-4 h-4 stroke-[2.5]" />
            <span>Sincronizar Todo el Drive</span>
          </button>
        </div>

        <!-- Help Info Box -->
        <div class="glass-panel p-5 sm:p-6 rounded-3xl space-y-3 bg-darkBg/30 border-darkBorder/60">
          <div class="flex items-center gap-2 text-xs font-bold text-cyan-300">
            <Info class="w-4 h-4" />
            <span>Información Importante</span>
          </div>
          <ul class="text-xs text-slate-400 space-y-2 list-disc list-inside leading-relaxed font-medium">
            <li>Columnas obligatorias: <span class="text-slate-200 font-mono font-bold">CEDULA</span>, <span class="text-slate-200 font-mono font-bold">APELLIDOS Y NOMBRES</span> y <span class="text-slate-200 font-mono font-bold">SUBNOVEDAD</span>.</li>
            <li>Nuevas cédulas se registrarán automáticamente como personal activo.</li>
            <li>Si una subnovedad está vacía, se asignará <span class="text-emerald-400 font-bold">SIN NOVEDAD (Disponible)</span>.</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  Upload, 
  Cloud, 
  Loader2, 
  Activity, 
  Info, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-vue-next'
import { useAppStore } from '../stores/appStore'
import { useMultiDaySelection } from '../composables/useMultiDaySelection'
import { useLocalFileUpload } from '../composables/useLocalFileUpload'
import { generateSyncLogText } from '../utils/logFormatter'

import SyncTemplateDownload from '../components/sincronizar/SyncTemplateDownload.vue'
import SyncSourceSelector from '../components/sincronizar/SyncSourceSelector.vue'
import SyncMultiDayCalendar from '../components/sincronizar/SyncMultiDayCalendar.vue'
import SyncFileDropzone from '../components/sincronizar/SyncFileDropzone.vue'
import SyncConflictAlert from '../components/sincronizar/SyncConflictAlert.vue'
import SyncDriveProgress from '../components/sincronizar/SyncDriveProgress.vue'

const appStore = useAppStore()

// State variables
const source = ref<'local' | 'drive'>('local')
const mode = ref<'dias' | 'mes'>('dias')
const mes = ref('MAYO')
const overwrite = ref(false)

// Multi-day calendar composable
const {
  multiDayMonth,
  selectedDates,
  calendarDays,
  calendarPadding,
  toggleDay,
  selectAllDays,
  clearAllDays
} = useMultiDaySelection('JULIO')

// Local file upload composable
const {
  selectedFile,
  loadingSubmit,
  statusState,
  statusMessage,
  conflicts,
  fileExtension,
  formattedFileSize,
  handleDrop,
  handleFileSelected,
  clearFile,
  submitReport,
  confirmOverwrite
} = useLocalFileUpload({
  mode,
  mes,
  selectedDates,
  overwrite
})

const isSubmitDisabled = computed(() => {
  if (source.value === 'local') {
    return !selectedFile.value || (mode.value === 'mes' && !mes.value) || (mode.value === 'dias' && selectedDates.value.length === 0) || loadingSubmit.value
  } else {
    return (
      (mode.value === 'mes' && !mes.value) ||
      (mode.value === 'dias' && selectedDates.value.length === 0)
    ) || appStore.isSyncingDrive
  }
})

const mainButtonText = computed(() => {
  if (source.value === 'local') {
    return 'Sincronizar Reporte'
  } else {
    return 'Buscar y Sincronizar en Drive'
  }
})

const handleMainAction = () => {
  if (source.value === 'local') {
    submitReport()
  } else {
    appStore.startDriveSync({
      tipo: mode.value,
      fechas: mode.value === 'dias' ? [...selectedDates.value].sort() : null,
      mes: mode.value === 'mes' ? mes.value : null,
      overwrite: overwrite.value
    })
  }
}

const handleDownloadSyncLog = () => {
  if (appStore.syncLogs.length === 0) return
  const text = generateSyncLogText(appStore.syncLogs)
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `log_sincronizacion_${new Date().toISOString().slice(0, 10)}.txt`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

