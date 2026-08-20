<template>
  <div class="space-y-6 min-w-0 max-w-full">
    <!-- Header & Template Download -->
    <SyncTemplateDownload :api-base="appStore.apiBase" />

    <!-- Configuration and Upload Card -->
    <div class="glass-panel p-5 sm:p-7 rounded-3xl space-y-6 border border-darkBorder shadow-xl">
      <!-- 1. Source & Mode Selectors -->
      <SyncSourceSelector 
        v-model:source="syncSource" 
        v-model:mode="syncMode" 
      />

      <!-- 2. Scope Configuration: By Month or By Days -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2 border-t border-darkBorder/60">
        <!-- Month scope -->
        <div v-if="syncMode === 'mes'" class="space-y-2">
          <label class="text-xs uppercase font-bold text-slate-300">Mes a Sincronizar:</label>
          <select 
            v-model="syncMonth" 
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 shadow-sm cursor-pointer"
          >
            <option v-for="m in months" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Days scope (Multi-day calendar) -->
        <SyncMultiDayCalendar 
          v-else-if="syncMode === 'dias'"
          v-model:multi-day-month="multiDayMonth"
          :months="months"
          :selected-dates="selectedDates"
          :calendar-days="calendarDays"
          :calendar-padding="calendarPadding"
          @toggle-day="toggleDay"
          @select-all="selectAllDays"
          @clear-all="clearAllDays"
        />
      </div>

      <!-- 3. Local File Dropzone (if source is local) -->
      <SyncFileDropzone 
        v-if="syncSource === 'local'"
        :selected-file="selectedFile"
        :file-extension="fileExtension"
        :formatted-file-size="formattedFileSize"
        @file-selected="handleFileSelected"
        @file-dropped="handleDrop"
        @clear-file="clearFile"
      />

      <!-- 4. Conflict Notification -->
      <SyncConflictAlert 
        :status-state="statusState"
        :status-message="statusMessage"
        :conflicts="conflicts"
        @confirm-overwrite="confirmOverwrite"
        @cancel="statusState = 'idle'"
      />

      <!-- 5. Submit Action Button -->
      <div class="pt-2">
        <button 
          type="button"
          @click="startSynchronization"
          :disabled="isSubmitDisabled"
          class="w-full py-3.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-2xl text-xs sm:text-sm font-bold text-white flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-cyan-950/40 active:scale-98 select-none"
        >
          <Loader2 v-if="loadingSubmit || appStore.syncStatus === 'syncing'" class="w-4 h-4 animate-spin" />
          <CloudSync v-else class="w-4 h-4" />
          <span>{{ getSubmitButtonText() }}</span>
        </button>
      </div>

      <!-- Generic Status messages for Local upload -->
      <div v-if="syncSource === 'local' && statusState === 'success'" class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs p-4 rounded-xl flex items-center gap-2.5">
        <CheckCircle2 class="w-4 h-4 shrink-0 text-emerald-400" />
        <span>{{ statusMessage }}</span>
      </div>
      <div v-if="syncSource === 'local' && statusState === 'error'" class="bg-red-500/10 border border-red-500/30 text-red-300 text-xs p-4 rounded-xl flex items-center gap-2.5">
        <AlertCircle class="w-4 h-4 shrink-0 text-red-400" />
        <span>{{ statusMessage }}</span>
      </div>
    </div>

    <!-- 6. Drive Sync Real-Time Progress -->
    <SyncDriveProgress 
      v-if="syncSource === 'drive' || appStore.syncStatus !== 'idle'"
      @confirm-drive-overwrite="confirmDriveOverwrite"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  FolderSync as CloudSync, 
  Loader2, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-vue-next'

import { useAppStore } from '@stores/appStore'
import { useDateStore } from '@stores/dateStore'
import { MONTHS_LIST } from '@utils/date'
import { useMultiDaySelection } from '../composables/useMultiDaySelection'
import { useLocalFileUpload } from '../composables/useLocalFileUpload'

import SyncTemplateDownload from '../components/SyncTemplateDownload.vue'
import SyncSourceSelector from '../components/SyncSourceSelector.vue'
import SyncMultiDayCalendar from '../components/SyncMultiDayCalendar.vue'
import SyncFileDropzone from '../components/SyncFileDropzone.vue'
import SyncConflictAlert from '../components/SyncConflictAlert.vue'
import SyncDriveProgress from '../components/SyncDriveProgress.vue'

const appStore = useAppStore()
const dateStore = useDateStore()

const syncSource = ref<'local' | 'drive'>('local')
const syncMode = ref<'dias' | 'mes'>('dias')
const syncMonth = ref(dateStore.selectedMonth || dateStore.latestMonth || 'MAYO')
const overwrite = ref(false)
const months = MONTHS_LIST

// Multi-day selection composable
const {
  multiDayMonth,
  selectedDates,
  calendarDays,
  calendarPadding,
  toggleDay,
  selectAllDays,
  clearAllDays
} = useMultiDaySelection(syncMonth.value)

// Local upload composable
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
  mode: syncMode,
  mes: syncMonth,
  selectedDates,
  overwrite
})

const isSubmitDisabled = computed(() => {
  if (loadingSubmit.value || appStore.syncStatus === 'syncing') return true
  if (syncSource.value === 'local' && !selectedFile.value) return true
  if (syncMode.value === 'dias' && selectedDates.value.length === 0) return true
  return false
})

const getSubmitButtonText = () => {
  if (loadingSubmit.value || appStore.syncStatus === 'syncing') return 'PROCESANDO SINCRONIZACIÓN...'
  if (syncSource.value === 'drive') {
    return syncMode.value === 'mes'
      ? `SINCRONIZAR MES (${syncMonth.value}) DESDE GOOGLE DRIVE`
      : `SINCRONIZAR (${selectedDates.value.length}) DÍAS DESDE GOOGLE DRIVE`
  }
  return syncMode.value === 'mes'
    ? `PROCESAR REPORTE DEL MES (${syncMonth.value})`
    : `PROCESAR REPORTE DE (${selectedDates.value.length}) DÍAS`
}

const startSynchronization = () => {
  if (syncSource.value === 'local') {
    submitReport()
  } else {
    // Iniciar SSE / polling a través del store global
    appStore.startDriveSync({
      tipo: syncMode.value,
      mes: syncMode.value === 'mes' ? syncMonth.value : undefined,
      fechas: syncMode.value === 'dias' ? selectedDates.value : undefined,
      overwrite: overwrite.value
    })
  }
}

const confirmDriveOverwrite = () => {
  appStore.startDriveSync({
    tipo: syncMode.value,
    mes: syncMode.value === 'mes' ? syncMonth.value : undefined,
    fechas: syncMode.value === 'dias' ? selectedDates.value : undefined,
    overwrite: true
  })
}
</script>
