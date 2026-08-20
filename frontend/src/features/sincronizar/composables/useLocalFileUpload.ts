import { ref, computed, type Ref } from 'vue'
import { syncService } from '../services/sync.service'
import { useAppStore } from '@stores/appStore'

interface UseLocalFileUploadOptions {
  mode: Ref<'dias' | 'mes'>
  mes: Ref<string>
  selectedDates: Ref<string[]>
  overwrite: Ref<boolean>
}

export function useLocalFileUpload(options: UseLocalFileUploadOptions) {
  const appStore = useAppStore()

  const selectedFile = ref<File | null>(null)
  const loadingSubmit = ref(false)
  const statusState = ref<'idle' | 'success' | 'error' | 'conflict'>('idle')
  const statusMessage = ref('')
  const conflicts = ref<string[]>([])

  const fileExtension = computed<string>(() => {
    if (!selectedFile.value) return ''
    const parts = selectedFile.value.name.split('.')
    return parts.length > 1 ? (parts.pop() ?? '') : ''
  })

  const formattedFileSize = computed(() => {
    if (!selectedFile.value) return ''
    const bytes = selectedFile.value.size
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  })

  const handleDrop = (e: DragEvent) => {
    if (e.dataTransfer && e.dataTransfer.files.length > 0) {
      selectedFile.value = e.dataTransfer.files[0]
      statusState.value = 'idle'
    }
  }

  const handleFileSelected = (e: Event) => {
    const input = e.target as HTMLInputElement
    if (input.files && input.files.length > 0) {
      selectedFile.value = input.files[0]
      statusState.value = 'idle'
    }
  }

  const clearFile = () => {
    selectedFile.value = null
    statusState.value = 'idle'
  }

  const submitReport = async () => {
    if (!selectedFile.value) return

    loadingSubmit.value = true
    statusState.value = 'idle'
    statusMessage.value = ''
    conflicts.value = []

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('tipo', options.mode.value)
    formData.append('overwrite', options.overwrite.value ? 'true' : 'false')

    if (options.mode.value === 'mes') {
      formData.append('mes', options.mes.value)
    } else {
      const datesParam = [...options.selectedDates.value].sort().join(',')
      formData.append('fechas', datesParam)
    }

    try {
      const data = await syncService.uploadReportFile(formData)
      loadingSubmit.value = false

      if (data.status === 'conflict') {
        statusState.value = 'conflict'
        statusMessage.value = data.detail || 'Se detectaron reportes ya cargados previamente para las fechas seleccionadas.'
        conflicts.value = data.conflictos || []
      } else if (data.status === 'success' || data.status === 'ok') {
        statusState.value = 'success'
        statusMessage.value = `¡Reporte sincronizado con éxito! Registros procesados: ${data.registros_procesados ?? 0}, Novedades insertadas: ${data.novedades_insertadas ?? 0}.`
        selectedFile.value = null
        appStore.fetchAvailableDates()
      } else {
        statusState.value = 'error'
        statusMessage.value = data.detail || 'Ocurrió un error inesperado al procesar el reporte.'
      }
    } catch (e: any) {
      loadingSubmit.value = false
      statusState.value = 'error'
      statusMessage.value = e.message || 'Error de conexión con el servidor al subir el archivo.'
    }
  }

  const confirmOverwrite = () => {
    options.overwrite.value = true
    submitReport()
  }

  return {
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
  }
}
