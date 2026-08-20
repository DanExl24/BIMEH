import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchWithAuth } from '../services/api'

export type ReportFormat = 'excel' | 'csv' | 'pdf' | 'json' | string

export const useReportDownloadStore = defineStore('reportDownload', () => {
  const isModalOpen = ref(false)
  const isGenerating = ref(false)
  const status = ref<'idle' | 'generating' | 'success' | 'error'>('idle')
  
  const reportTitle = ref('')
  const reportFormat = ref<ReportFormat>('')
  const statusMessage = ref('')
  const errorMessage = ref('')
  const downloadedFilename = ref('')
  const lastDownloadUrl = ref('')
  
  const secondsElapsed = ref(0)
  let timerInterval: any = null
  let autoDismissTimeout: any = null
  let abortController: AbortController | null = null

  const startTimer = () => {
    secondsElapsed.value = 0
    if (timerInterval) clearInterval(timerInterval)
    timerInterval = setInterval(() => {
      secondsElapsed.value++
    }, 1000)
  }

  const stopTimer = () => {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }

  const clearAutoDismiss = () => {
    if (autoDismissTimeout) {
      clearTimeout(autoDismissTimeout)
      autoDismissTimeout = null
    }
  }

  const parseFilenameFromHeaders = (res: Response, fallbackTitle: string, format: string): string => {
    const disposition = res.headers.get('content-disposition') || ''
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (match && match[1]) {
        return match[1].replace(/['"]/g, '').trim()
      }
    }
    const cleanTitle = fallbackTitle.toLowerCase().replace(/[^a-z0-9]/gi, '_')
    const ext = format === 'excel' ? 'xlsx' : format.toLowerCase()
    return `${cleanTitle || 'reporte'}_${new Date().toISOString().slice(0, 10)}.${ext}`
  }

  const downloadReport = async (url: string, title: string = 'Reporte Oficial', format: ReportFormat = 'excel') => {
    clearAutoDismiss()
    stopTimer()
    
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    isModalOpen.value = true
    isGenerating.value = true
    status.value = 'generating'
    reportTitle.value = title
    reportFormat.value = format
    statusMessage.value = 'Compilando registros y generando documento...'
    errorMessage.value = ''
    downloadedFilename.value = ''
    lastDownloadUrl.value = url

    startTimer()

    try {
      const response = await fetchWithAuth(url, {
        signal: abortController.signal
      })

      if (!response.ok) {
        // Intentar parsear el JSON con detalle de error
        const errorJson = await response.json().catch(() => null)
        const errorText = errorJson?.detail || `Error al procesar el reporte en el servidor (${response.status}: ${response.statusText})`
        throw new Error(errorText)
      }

      // Procesar blob y forzar descarga
      statusMessage.value = 'Descargando archivo en su navegador...'
      const blob = await response.blob()
      
      const filename = parseFilenameFromHeaders(response, title, format)
      downloadedFilename.value = filename

      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      // Liberar objeto URL
      setTimeout(() => {
        window.URL.revokeObjectURL(blobUrl)
      }, 2000)

      stopTimer()
      isGenerating.value = false
      status.value = 'success'
      statusMessage.value = '¡El reporte se ha generado y descargado exitosamente!'

      // Auto cerrar tras 3.5 segundos en éxito si no se interactúa
      autoDismissTimeout = setTimeout(() => {
        if (status.value === 'success') {
          closeModal()
        }
      }, 3500)

    } catch (err: any) {
      stopTimer()
      isGenerating.value = false
      
      if (err.name === 'AbortError') {
        status.value = 'error'
        errorMessage.value = 'Generación de reporte cancelada por el usuario.'
      } else {
        status.value = 'error'
        errorMessage.value = err.message || 'Ocurrió un error inesperado al generar el reporte.'
        console.error('Error generando reporte:', err)
      }
    }
  }

  const cancelGeneration = () => {
    if (abortController) {
      abortController.abort()
      abortController = null
    }
    stopTimer()
    isGenerating.value = false
    status.value = 'error'
    errorMessage.value = 'Generación cancelada por el usuario.'
  }

  const retryDownload = () => {
    if (lastDownloadUrl.value) {
      downloadReport(lastDownloadUrl.value, reportTitle.value, reportFormat.value)
    }
  }

  const closeModal = () => {
    clearAutoDismiss()
    stopTimer()
    if (isGenerating.value && abortController) {
      abortController.abort()
    }
    isModalOpen.value = false
    isGenerating.value = false
    status.value = 'idle'
    errorMessage.value = ''
    statusMessage.value = ''
  }

  return {
    isModalOpen,
    isGenerating,
    status,
    reportTitle,
    reportFormat,
    statusMessage,
    errorMessage,
    downloadedFilename,
    secondsElapsed,
    lastDownloadUrl,

    downloadReport,
    cancelGeneration,
    retryDownload,
    closeModal
  }
})
