<template>
  <div>
    <!-- Backdrop Overlay -->
    <transition name="fade">
      <div 
        v-if="isOpen" 
        @click="cerrar"
        class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 transition-opacity duration-300"
        aria-hidden="true"
      ></div>
    </transition>

    <!-- Drawer Lateral Derecho -->
    <aside 
      class="fixed right-0 top-0 bottom-0 w-full sm:w-[540px] md:w-[620px] max-w-full bg-slate-900/95 border-l border-darkBorder/90 z-50 flex flex-col shadow-2xl backdrop-blur-xl transition-transform duration-300 ease-out"
      :class="isOpen ? 'translate-x-0' : 'translate-x-full'"
    >
      <!-- 1. Header del Drawer -->
      <div class="px-5 py-4 border-b border-darkBorder/80 bg-gradient-to-r from-darkCard/90 via-slate-900/90 to-darkCard/90 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-md shadow-cyan-500/10">
            <Bot class="w-5 h-5 stroke-[2.5]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-sm font-black text-slate-100 uppercase tracking-wide">
                Asistente BIMEJ 12
              </h2>
              <!-- Pill de Estado de Ollama -->
              <span 
                v-if="status?.online" 
                class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                title="Ollama conectado localmente"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                {{ status.model_configured }}
              </span>
              <span 
                v-else 
                class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-rose-500/15 text-rose-300 border border-rose-500/30"
                title="Ollama desconectado"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                Offline
              </span>
            </div>
            <p class="text-[11px] text-slate-400 leading-tight">
              Inteligencia Local • Consultas y Apreciación de Personal
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <!-- Botón de Generar Apreciación Rápida -->
          <button
            type="button"
            @click="generarApreciacionDirecta"
            :disabled="isLoadingApreciacion || !status?.online"
            class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-bold transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
            title="Generar boletín militar de apreciación de situación"
          >
            <Loader2 v-if="isLoadingApreciacion" class="w-3.5 h-3.5 animate-spin" />
            <Sparkles v-else class="w-3.5 h-3.5 text-amber-400" />
            <span class="hidden sm:inline">Apreciación</span>
          </button>

          <!-- Cerrar Drawer -->
          <button 
            @click="cerrar"
            class="p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors cursor-pointer border border-transparent hover:border-darkBorder"
            title="Cerrar asistente"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Alerta si Ollama está Desconectado -->
      <div 
        v-if="!status?.online && !isLoadingStatus" 
        class="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2.5 text-xs text-amber-300 flex items-start gap-2.5 shrink-0"
      >
        <AlertTriangle class="w-4 h-4 shrink-0 text-amber-400 mt-0.5" />
        <div class="flex-1">
          <p class="font-bold">Ollama no detectado en ejecución</p>
          <p class="text-[11px] text-amber-200/80 mt-0.5">
            Abra su terminal y ejecute: <code class="px-1.5 py-0.5 rounded bg-amber-950/60 font-mono text-amber-200">ollama run {{ status?.model_configured || 'llama3.1:8b' }}</code>. Luego presione verificar.
          </p>
        </div>
        <button
          @click="verificarEstado"
          class="px-2 py-1 bg-amber-500/20 hover:bg-amber-500/30 rounded-lg text-[10px] font-bold uppercase transition-colors shrink-0"
        >
          Reintentar
        </button>
      </div>

      <!-- 2. Área de Mensajes del Chat (Scrollable) -->
      <div 
        ref="chatContainer"
        class="flex-1 p-4 sm:p-5 overflow-y-auto space-y-4 scrollbar-thin font-sans"
      >
        <!-- Estado Vacío: Bienvenida y Sugerencias -->
        <div v-if="mensajes.length === 0" class="py-6 px-2 text-center space-y-5 animate-in fade-in duration-300">
          <div class="w-16 h-16 rounded-3xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center mx-auto text-cyan-400 shadow-lg shadow-cyan-500/10">
            <ShieldCheck class="w-8 h-8 stroke-[2]" />
          </div>

          <div class="max-w-md mx-auto space-y-1.5">
            <h3 class="text-sm sm:text-base font-black text-slate-100 uppercase tracking-wide">
              Centro de Inteligencia Operacional BIMEH
            </h3>
            <p class="text-xs text-slate-400 leading-relaxed">
              Consulte personal, ausencias, novedades médicas y fuerza disponible en lenguaje natural. Procesamiento <strong class="text-emerald-400 font-semibold">100% privado y local</strong> con Ollama.
            </p>
          </div>

          <!-- Píldoras de Consultas Frecuentes -->
          <div class="space-y-2 max-w-lg mx-auto text-left">
            <p class="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-1">
              Consultas sugeridas para iniciar:
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                v-for="sug in sugerencias"
                :key="sug"
                @click="enviarMensajeDirecto(sug)"
                type="button"
                class="p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-darkBorder hover:border-cyan-500/40 text-left transition-all cursor-pointer group text-xs text-slate-300 hover:text-cyan-300 flex items-start gap-2 shadow-sm"
              >
                <ArrowRight class="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5 group-hover:translate-x-0.5 transition-transform" />
                <span class="leading-snug">{{ sug }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Lista de Mensajes -->
        <template v-else>
          <div 
            v-for="msg in mensajes" 
            :key="msg.id" 
            class="flex flex-col space-y-2 animate-in fade-in duration-200"
            :class="msg.sender === 'user' ? 'items-end' : 'items-start'"
          >
            <!-- Header del mensaje -->
            <div class="flex items-center gap-1.5 px-1 text-[10px] text-slate-500 font-mono">
              <span class="font-bold uppercase">{{ msg.sender === 'user' ? 'Usted' : 'Asistente IA' }}</span>
              <span>•</span>
              <span>{{ msg.timestamp }}</span>
            </div>

            <!-- Burbuja de Mensaje -->
            <div 
              class="max-w-[92%] rounded-2xl p-3.5 sm:p-4 text-xs sm:text-[13px] leading-relaxed shadow-md"
              :class="msg.sender === 'user' 
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-slate-950 font-semibold rounded-tr-xs' 
                : msg.isError
                  ? 'bg-rose-950/40 border border-rose-500/30 text-rose-200 rounded-tl-xs'
                  : 'bg-slate-950/90 border border-darkBorder/80 text-slate-200 rounded-tl-xs'"
            >
              <!-- Texto Markdown/Formato -->
              <div class="whitespace-pre-wrap leading-relaxed select-text space-y-1.5">
                {{ msg.text }}
              </div>

              <!-- Código SQL Generado (Collapsible) -->
              <div v-if="msg.sql" class="mt-3 pt-2.5 border-t border-darkBorder/60">
                <details class="group cursor-pointer">
                  <summary class="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400 hover:text-cyan-300 flex items-center gap-1 select-none">
                    <Database class="w-3 h-3" />
                    <span>Consulta SQL Ejecutada en PostgreSQL</span>
                  </summary>
                  <pre class="mt-2 p-2.5 rounded-xl bg-slate-900 border border-darkBorder/80 text-[10px] font-mono text-cyan-200/90 overflow-x-auto whitespace-pre-wrap select-all">{{ msg.sql }}</pre>
                </details>
              </div>

              <!-- Mini Tabla de Datos si retornó registros -->
              <div v-if="msg.rows && msg.rows.length > 0" class="mt-3 pt-2.5 border-t border-darkBorder/60 space-y-2">
                <div class="flex items-center justify-between text-[11px] font-semibold text-slate-400">
                  <span class="flex items-center gap-1.5 text-cyan-400">
                    <Table2 class="w-3.5 h-3.5" />
                    Resultados ({{ msg.total_records }} registros):
                  </span>
                  <span v-if="msg.rows.length > 10" class="text-[10px] text-slate-500">
                    Mostrando primeros 10
                  </span>
                </div>

                <div class="overflow-x-auto rounded-xl border border-darkBorder/70 max-h-56 scrollbar-thin">
                  <table class="w-full text-left text-[11px] border-collapse bg-slate-900/90">
                    <thead>
                      <tr class="border-b border-darkBorder/80 bg-slate-950/80 sticky top-0 text-[10px] font-mono text-slate-400 uppercase">
                        <th v-for="col in msg.columns" :key="col" class="px-2.5 py-1.5 font-bold">
                          {{ col }}
                        </th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-darkBorder/40">
                      <tr 
                        v-for="(row, idx) in msg.rows.slice(0, 10)" 
                        :key="idx"
                        class="hover:bg-cyan-500/5 transition-colors"
                      >
                        <td 
                          v-for="col in msg.columns" 
                          :key="col" 
                          class="px-2.5 py-1.5 text-slate-300 font-mono text-[10px] whitespace-nowrap"
                        >
                          {{ row[col] !== null && row[col] !== undefined ? row[col] : '-' }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <!-- Spinner Pensando -->
          <div v-if="isEnviando" class="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-950/60 border border-darkBorder/60 w-fit text-xs text-slate-400 animate-pulse">
            <Loader2 class="w-4 h-4 animate-spin text-cyan-400" />
            <span>Consultando base de datos con {{ status?.model_configured || 'Ollama' }}...</span>
          </div>
        </template>
      </div>

      <!-- 3. Footer con Input de Mensajes -->
      <div class="p-3 sm:p-4 border-t border-darkBorder/80 bg-gradient-to-r from-slate-900/95 via-darkCard/95 to-slate-900/95 shrink-0 space-y-2">
        <form @submit.prevent="enviarMensaje" class="flex items-center gap-2">
          <input
            ref="inputRef"
            v-model="inputTexto"
            type="text"
            :disabled="isEnviando || !status?.online"
            placeholder="Pregunte sobre personal, novedades, fuerza disponible o días de ausencia..."
            class="flex-1 bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-100 rounded-xl px-3.5 py-2.5 text-xs font-medium focus:outline-none transition-all placeholder:text-slate-600 disabled:opacity-50"
          />

          <button
            type="submit"
            :disabled="!inputTexto.trim() || isEnviando || !status?.online"
            class="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-cyan-500/20 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5 shrink-0"
          >
            <Send class="w-4 h-4" />
            <span class="hidden sm:inline">Consultar</span>
          </button>
        </form>

        <div class="flex items-center justify-between text-[10px] text-slate-500 px-1 font-mono">
          <div class="flex items-center gap-2">
            <span>Solo lectura segura</span>
            <span>•</span>
            <button 
              v-if="mensajes.length > 0" 
              @click="limpiarChat" 
              type="button" 
              class="text-rose-400/80 hover:text-rose-300 underline cursor-pointer"
            >
              Limpiar chat
            </button>
          </div>
          <span>Presione Enter para enviar</span>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'
import {
  Bot,
  X,
  Sparkles,
  AlertTriangle,
  ShieldCheck,
  ArrowRight,
  Database,
  Table2,
  Loader2,
  Send
} from 'lucide-vue-next'

import type { IAStatusResponse, IAChatMessage } from '../types/ia.types'
import { iaService } from '../services/ia.service'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const status = ref<IAStatusResponse | null>(null)
const isLoadingStatus = ref(false)
const isEnviando = ref(false)
const isLoadingApreciacion = ref(false)
const inputTexto = ref('')
const mensajes = ref<IAChatMessage[]>([])

const chatContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

const sugerencias = [
  '¿Cuántos efectivos activos hay en total en el batallón?',
  'Listar personal con más de 10 días de incapacidad médica',
  '¿Quiénes están con novedades de vacaciones este mes?',
  'Mostrar la distribución de personal activo por compañías'
]

const scrollAlFondo = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const verificarEstado = async () => {
  isLoadingStatus.value = true
  try {
    status.value = await iaService.obtenerEstado()
  } catch (err) {
    status.value = {
      online: false,
      base_url: 'http://127.0.0.1:11434',
      model_configured: 'llama3.1:8b',
      model_available: false,
      models_installed: [],
      error: 'Error de conexión con el backend'
    }
  } finally {
    isLoadingStatus.value = false
  }
}

const enviarMensajeDirecto = (texto: string) => {
  inputTexto.value = texto
  enviarMensaje()
}

const enviarMensaje = async () => {
  const query = inputTexto.value.trim()
  if (!query || isEnviando.value) return

  const userMsg: IAChatMessage = {
    id: String(Date.now()),
    sender: 'user',
    text: query,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  mensajes.value.push(userMsg)
  inputTexto.value = ''
  isEnviando.value = true
  scrollAlFondo()

  try {
    const res = await iaService.enviarMensaje(query)
    const assistantMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: res.answer,
      type: res.type,
      sql: res.sql,
      columns: res.columns,
      rows: res.rows,
      total_records: res.total_records,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isError: res.type === 'error'
    }
    mensajes.value.push(assistantMsg)
  } catch (err: any) {
    const errorMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: err.message || 'Ocurrió un error al procesar la consulta con Ollama.',
      type: 'error',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isError: true
    }
    mensajes.value.push(errorMsg)
  } finally {
    isEnviando.value = false
    scrollAlFondo()
  }
}

const generarApreciacionDirecta = async () => {
  if (isLoadingApreciacion.value) return
  isLoadingApreciacion.value = true

  const userMsg: IAChatMessage = {
    id: String(Date.now()),
    sender: 'user',
    text: 'Generar Apreciación de Situación y Estado de Fuerza para la Comandancia',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  mensajes.value.push(userMsg)
  scrollAlFondo()

  try {
    const res = await iaService.generarApreciacion('TODOS')
    const assistantMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: res.apreciacion,
      type: 'data',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    mensajes.value.push(assistantMsg)
  } catch (err: any) {
    const errorMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: err.message || 'Error generando apreciación con Ollama.',
      type: 'error',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isError: true
    }
    mensajes.value.push(errorMsg)
  } finally {
    isLoadingApreciacion.value = false
    scrollAlFondo()
  }
}

const limpiarChat = () => {
  mensajes.value = []
}

const cerrar = () => {
  emit('close')
}

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      verificarEstado()
      nextTick(() => {
        inputRef.value?.focus()
      })
    }
  }
)

onMounted(() => {
  verificarEstado()
})
</script>
