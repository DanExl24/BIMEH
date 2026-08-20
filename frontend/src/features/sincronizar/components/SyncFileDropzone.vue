<template>
  <div class="space-y-2 pt-2">
    <label class="text-xs uppercase font-bold text-slate-300">Archivo del Reporte:</label>
    
    <div 
      @dragover.prevent="dragActive = true"
      @dragleave.prevent="dragActive = false"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
      class="border-2 border-dashed rounded-3xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center space-y-3 shadow-inner"
      :class="dragActive ? 'border-cyan-400 bg-cyan-500/10 shadow-lg shadow-cyan-500/10' : 'border-darkBorder hover:border-cyan-500/50 bg-darkBg/50'"
    >
      <input 
        type="file" 
        ref="fileInput" 
        @change="onFileChange" 
        accept=".xlsx, .xls, .json" 
        class="hidden" 
      />
      
      <div class="w-14 h-14 bg-cyan-500/10 rounded-2xl flex items-center justify-center text-cyan-400 border border-cyan-500/20 shadow-sm">
        <UploadCloud class="w-7 h-7 stroke-[2]" />
      </div>

      <div v-if="!selectedFile">
        <p class="text-xs sm:text-sm font-bold text-slate-100">
          Arrastra tu reporte aquí o <span class="text-cyan-400 underline decoration-cyan-500/50 underline-offset-2">haz clic para examinar</span>
        </p>
        <p class="text-xs text-slate-400 mt-1 font-medium">Formatos soportados: Excel (.xlsx, .xls) o JSON de novedades</p>
      </div>

      <!-- File Details if selected -->
      <div v-else class="flex items-center gap-2.5 sm:gap-3 bg-darkCard border border-darkBorder px-3 sm:px-5 py-2.5 sm:py-3 rounded-2xl text-left shadow-md max-w-full" @click.stop>
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 flex items-center justify-center font-bold text-xs shrink-0">
          <FileSpreadsheet class="w-4 h-4 sm:w-5 sm:h-5" />
        </div>
        <div class="min-w-0 flex-1">
          <h5 class="text-xs font-bold text-slate-100 max-w-[130px] sm:max-w-xs truncate">{{ selectedFile.name }}</h5>
          <span class="text-[11px] sm:text-xs text-slate-400 font-mono block">{{ formattedFileSize }} • {{ fileExtension.toUpperCase() }}</span>
        </div>
        <button 
          type="button" 
          @click.stop="$emit('clear-file')" 
          class="ml-1 sm:ml-3 text-slate-400 hover:text-red-400 p-1.5 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer shrink-0"
          title="Eliminar archivo seleccionado"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadCloud, FileSpreadsheet, X } from 'lucide-vue-next'

defineProps<{
  selectedFile: File | null
  fileExtension: string
  formattedFileSize: string
}>()

const emit = defineEmits<{
  (e: 'file-selected', evt: Event): void
  (e: 'file-dropped', evt: DragEvent): void
  (e: 'clear-file'): void
}>()

const dragActive = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const onDrop = (e: DragEvent) => {
  dragActive.value = false
  emit('file-dropped', e)
}

const onFileChange = (e: Event) => {
  emit('file-selected', e)
}
</script>
