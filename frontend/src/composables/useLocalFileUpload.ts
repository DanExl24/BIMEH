import { ref, computed, type Ref } from 'vue'
import { uploadReportFile } from '../services/api'
import { useAppStore } from '../stores/appStore'

export interface UseLocalFileUploadParams {
  mode: Ref<'dias' | 'mes'>
  mes: Ref<string>
  selectedDates: Ref<string[]>
  overwrite: Ref<boolean>
}

export function useLocalFileUpload(params: UseLocalFileUploadParams) {
  const { mode, mes, selectedDates, overwrite } = params
  const appStore = useAppStore()

  const selectedFile = ref<File | null>(null)
  const dragActive = ref(false)
  const fileInput = ref<HTMLInputElement | null>(null)
  const loadingSubmit = ref(false)
  const statusState = ref<'success' | 'error' | 'conflict' | null>(null)
  const statusMessage = ref('')
  const conflicts = ref<string[]>([])

  const fileExtension = computed<string>(() => {
    if (!selectedFile.value) return ''
    const parts = selectedFile.value.name.split('.')
    return parts.length > 1 ? (parts.pop() ?? '') : ''
  })

  const formattedFileSize = computed(() => {
    if (!selectedFile.value) return '0 B'
    const kb = selectedFile.value.size / 1024
    if (kb < 1024) return `${kb.toFixed(1)} KB`
    return `${(kb / 1024).toFixed(1)} MB`
  })

  const triggerFileInput = () => {
    fileInput.value?.click()
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

  const clearFile = () => {
    selectedFile.value = null
    statusState.value = null
    statusMessage.value = ''
    conflicts.value = []
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

    if (mode.value === 'dias') {
      formData.append('fechas', JSON.stringify([...selectedDates.value].sort()))
    } else {
      formData.append('mes', mes.value)
    }

    try {
      const data = await uploadReportFile(formData)

      if (data.status === 'conflict') {
        statusState.value = 'conflict'
        statusMessage.value = data.message || 'Conflicto de registros existentes'
        conflicts.value = data.conflicts || []
      } else if (data.status === 'success') {
        statusState.value = 'success'
        statusMessage.value = data.message || 'Sincronización completada con éxito'
        // Actualizar fechas disponibles globales
        appStore.fetchAvailableDates()
      } else {
        statusState.value = 'error'
        statusMessage.value = data.detail || data.message || 'Ocurrió un error al sincronizar.'
      }
    } catch (error: any) {
      console.error('Error uploading file:', error)
      statusState.value = 'error'
      statusMessage.value = error.message || 'Error al conectar con el servidor. Verifique que la API esté encendida.'
    } finally {
      loadingSubmit.value = false
    }
  }

  const confirmOverwrite = () => {
    overwrite.value = true
    submitReport()
  }

  return {
    selectedFile,
    dragActive,
    fileInput,
    loadingSubmit,
    statusState,
    statusMessage,
    conflicts,
    fileExtension,
    formattedFileSize,
    triggerFileInput,
    handleDrop,
    handleFileSelected,
    clearFile,
    submitReport,
    confirmOverwrite
  }
}
