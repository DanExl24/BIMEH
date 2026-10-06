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
              <!-- Badge de estado Gemini -->
              <span
                v-if="status?.online"
                class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-blue-500/15 text-blue-300 border border-blue-500/30"
                title="Gemini conectado"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse"></span>
                {{ status.model_configured }}
              </span>
              <span
                v-else
                class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-amber-500/15 text-amber-300 border border-amber-500/30"
                title="Verificando conexión con Gemini..."
              >
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                Conectando...
              </span>
            </div>
            <p class="text-[11px] text-slate-400 leading-tight">
              Gemini IA · Consultas y Apreciación de Personal
            </p>
          </div>
        </div>

        <div class="flex items-center gap-1.5">
          <!-- Botón Info Gemini -->
          <button
            type="button"
            @click="mostrarConfig = !mostrarConfig"
            class="p-2 rounded-xl text-slate-400 hover:text-blue-300 hover:bg-slate-800 transition-colors cursor-pointer"
            :class="mostrarConfig ? 'text-blue-400 bg-blue-500/10 border border-blue-500/30' : ''"
            title="Ver información del modelo Gemini activo"
          >
            <Settings class="w-4 h-4" />
          </button>

          <!-- Botón de Generar Apreciación Rápida -->
          <button
            type="button"
            @click="generarApreciacionDirecta"
            :disabled="isLoadingApreciacion"
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

      <!-- Panel de información del modelo Gemini (reemplaza panel Ollama) -->
      <div
        v-if="mostrarConfig"
        class="bg-slate-950 border-b border-darkBorder px-4 py-3 space-y-2 text-xs shrink-0 animate-in fade-in duration-200"
      >
        <div class="flex items-center justify-between text-slate-300 font-bold">
          <span class="flex items-center gap-1.5 text-blue-400">
            <Globe class="w-3.5 h-3.5" />
            Motor de IA: Google Gemini
          </span>
          <button @click="mostrarConfig = false" class="text-slate-500 hover:text-slate-300 p-0.5 cursor-pointer" title="Cerrar">
            <X class="w-3.5 h-3.5" />
          </button>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div class="bg-slate-900 rounded-xl px-3 py-2 border border-darkBorder">
            <p class="text-[10px] text-slate-500 mb-0.5">Modelo activo</p>
            <p class="text-blue-300 font-mono font-bold text-[11px]">{{ status?.model_configured || 'gemini-3.5-flash-lite' }}</p>
          </div>
          <div class="bg-slate-900 rounded-xl px-3 py-2 border border-darkBorder">
            <p class="text-[10px] text-slate-500 mb-0.5">Estado</p>
            <p class="font-bold text-[11px]" :class="status?.online ? 'text-emerald-400' : 'text-amber-400'">
              {{ status?.online ? '✓ Conectado' : '⌛ Verificando...' }}
            </p>
          </div>
        </div>

        <p class="text-[11px] text-slate-400 leading-snug">
          Para cambiar el modelo edita <code class="text-blue-300 font-mono">GEMINI_MODEL</code> en el
          archivo <code class="text-blue-300 font-mono">.env</code> del backend y reinicia el servidor.
        </p>

        <div class="flex items-center gap-1.5 bg-blue-500/8 border border-blue-500/20 rounded-lg p-2">
          <span class="text-blue-400 text-[11px]">💡</span>
          <span class="text-[11px] text-slate-400">Modelos recomendados: <span class="text-blue-300 font-mono">gemini-3.5-flash-lite</span> (500/día), <span class="text-blue-300 font-mono">gemini-3.1-flash-lite</span> (500/día), <span class="text-blue-300 font-mono">gemini-3.8-flash</span></span>
        </div>
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
              Consulte personal, ausencias, novedades médicas y fuerza disponible en lenguaje natural. Impulsado por
              <strong class="text-blue-400 font-semibold">Google Gemini</strong> con procesamiento seguro en la nube.
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
            v-for="(msg, msgIdx) in mensajes" 
            :key="msg.id" 
            class="flex flex-col space-y-1.5 animate-in fade-in duration-200 group/msg"
            :class="msg.sender === 'user' ? 'items-end' : 'items-start'"
          >
            <!-- Header del mensaje con botones de acción -->
            <div 
              class="flex items-center gap-1.5 px-1 text-[10px] text-slate-500 font-mono w-full"
              :class="msg.sender === 'user' ? 'justify-end' : 'justify-between'"
            >
              <div class="flex items-center gap-1.5">
                <span class="font-bold uppercase">{{ msg.sender === 'user' ? 'Usted' : 'Asistente IA' }}</span>
                <span>•</span>
                <span>{{ msg.timestamp }}</span>
                <template v-if="msg.elapsed_seconds">
                  <span>•</span>
                  <span class="text-cyan-400 font-semibold bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/20">
                    ⏱️ {{ msg.elapsed_seconds }}s
                  </span>
                </template>
              </div>

              <!-- Botones de Acción (Copiar / Editar) -->
              <div class="flex items-center gap-1 opacity-70 group-hover/msg:opacity-100 transition-opacity">
                <!-- Botón Copiar -->
                <button
                  type="button"
                  @click="copiarTexto(msg.id, msg.text)"
                  class="p-1 rounded-md hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer flex items-center gap-1"
                  :class="mensajeCopiadoId === msg.id ? 'text-emerald-400 bg-emerald-500/10' : ''"
                  :title="mensajeCopiadoId === msg.id ? '¡Copiado en portapapeles!' : 'Copiar mensaje'"
                >
                  <Check v-if="mensajeCopiadoId === msg.id" class="w-3.5 h-3.5 text-emerald-400" />
                  <Copy v-else class="w-3.5 h-3.5" />
                  <span v-if="mensajeCopiadoId === msg.id" class="text-[9px] font-bold text-emerald-400">Copiado</span>
                </button>

                <!-- Botón Editar (Solo para el mensaje del usuario) -->
                <button
                  v-if="msg.sender === 'user'"
                  type="button"
                  @click="iniciarEdicion(msg)"
                  :disabled="isEnviando || isLoadingApreciacion"
                  class="p-1 rounded-md hover:bg-slate-800 text-slate-400 hover:text-cyan-300 transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
                  title="Editar mensaje"
                >
                  <Pencil class="w-3.5 h-3.5" />
                </button>
              </div>
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
              <!-- Modo Edición para el Mensaje de Usuario -->
              <div v-if="editandoMensajeId === msg.id" class="space-y-2 min-w-[240px] sm:min-w-[340px]">
                <textarea
                  v-model="textoEdicion"
                  rows="3"
                  class="w-full bg-slate-900/95 text-slate-100 rounded-xl p-3 text-xs font-normal border border-cyan-400 focus:outline-none focus:ring-1 focus:ring-cyan-400 resize-none shadow-inner"
                  placeholder="Edite su mensaje..."
                  @keydown.enter.exact.prevent="guardarYReenviarEdicion(msgIdx)"
                  @keydown.esc="cancelarEdicion"
                ></textarea>
                <div class="flex items-center justify-between gap-2">
                  <span class="text-[10px] text-slate-900/90 font-medium">Enter para enviar · Esc cancelar</span>
                  <div class="flex items-center gap-1.5">
                    <button
                      type="button"
                      @click="cancelarEdicion"
                      class="px-2.5 py-1 rounded-lg bg-black/25 hover:bg-black/40 text-slate-950 font-bold text-[11px] transition-colors cursor-pointer"
                    >
                      Cancelar
                    </button>
                    <button
                      type="button"
                      @click="guardarYReenviarEdicion(msgIdx)"
                      :disabled="!textoEdicion.trim() || isEnviando"
                      class="px-3 py-1 rounded-lg bg-slate-950 hover:bg-slate-900 text-cyan-300 font-bold text-[11px] transition-colors cursor-pointer shadow flex items-center gap-1 disabled:opacity-50"
                    >
                      <Check class="w-3 h-3 text-cyan-400" />
                      Guardar y enviar
                    </button>
                  </div>
                </div>
              </div>

              <!-- Contenido Normal del Mensaje -->
              <template v-else>
                <!-- Texto Markdown/Formato -->
                <div 
                  v-if="msg.sender === 'assistant'"
                  class="markdown-content text-xs sm:text-[13px] leading-relaxed select-text space-y-1.5 text-slate-200"
                  v-html="renderMarkdown(msg.text)"
                ></div>
                <div 
                  v-else
                  class="whitespace-pre-wrap text-xs sm:text-[13px] leading-relaxed select-text space-y-1.5"
                >
                  {{ msg.text }}
                </div>

                <!-- Código SQL Generado (Collapsible) -->
                <div v-if="msg.sql" class="mt-3 pt-2.5 border-t border-darkBorder/60">
                  <details class="group cursor-pointer">
                    <summary class="text-[10px] font-mono font-bold uppercase tracking-wider text-cyan-400 hover:text-cyan-300 flex items-center justify-between gap-1 select-none">
                      <span class="flex items-center gap-1">
                        <Database class="w-3 h-3" />
                        <span>Consulta SQL Ejecutada en PostgreSQL</span>
                      </span>
                      <button
                        type="button"
                        @click.stop="copiarTexto(msg.id + '-sql', msg.sql)"
                        class="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-300 transition-colors cursor-pointer font-normal normal-case text-[10px] flex items-center gap-1"
                        :title="mensajeCopiadoId === (msg.id + '-sql') ? '¡SQL Copiado!' : 'Copiar SQL'"
                      >
                        <Check v-if="mensajeCopiadoId === (msg.id + '-sql')" class="w-3 h-3 text-emerald-400" />
                        <Copy v-else class="w-3 h-3" />
                        <span class="hidden sm:inline">{{ mensajeCopiadoId === (msg.id + '-sql') ? 'Copiado' : 'Copiar' }}</span>
                      </button>
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
              </template>
            </div>
          </div>

          <!-- Spinner Pensando con Cronómetro Dinámico, Fases y Botón Detener -->
          <div v-if="isEnviando || isLoadingApreciacion" class="flex flex-col gap-2 p-3 rounded-2xl bg-slate-950/80 border border-cyan-500/25 w-fit max-w-sm text-xs text-slate-300 shadow-lg shadow-cyan-500/5 animate-in fade-in">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2">
                <Loader2 class="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
                <span class="font-medium text-slate-200">{{ faseCargaTexto }}</span>
              </div>
              <button
                type="button"
                @click="detenerGeneracion"
                class="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 text-[10px] font-bold transition-colors cursor-pointer"
                title="Detener respuesta de la IA"
              >
                <Square class="w-2.5 h-2.5 fill-rose-300" />
                <span>Detener</span>
              </button>
            </div>
            <div class="flex items-center justify-between gap-4 text-[10px] text-slate-400 font-mono pl-6">
              <span>Modelo: <strong class="text-cyan-300">{{ status?.model_configured || 'Gemini' }}</strong></span>
              <span class="px-1.5 py-0.5 rounded bg-slate-900 text-cyan-400 font-semibold border border-darkBorder">
                ⏱️ {{ tiempoTranscurrido }}s
              </span>
            </div>
          </div>
        </template>
      </div>

      <!-- 3. Footer con Input de Mensajes -->
      <div class="p-3 sm:p-4 border-t border-darkBorder/80 bg-gradient-to-r from-slate-900/95 via-darkCard/95 to-slate-900/95 shrink-0 space-y-2">
        <!-- Pastilla de Contexto Activo de Militar -->
        <div 
          v-if="activeMilitar"
          class="flex items-center justify-between gap-2 px-3 py-1.5 rounded-xl bg-cyan-950/80 border border-cyan-500/40 text-[11px] text-cyan-200 shadow-sm animate-in fade-in"
        >
          <div class="flex items-center gap-1.5 truncate">
            <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shrink-0"></span>
            <span class="text-cyan-400 font-bold shrink-0">Militar en contexto:</span>
            <span class="font-semibold truncate text-white uppercase">{{ activeMilitar.nombre }}</span>
            <span class="font-mono text-cyan-300 text-[10px] shrink-0">(C.C. {{ activeMilitar.cedula }})</span>
          </div>
          <button 
            type="button"
            @click="limpiarMilitarActivo"
            class="p-0.5 rounded text-cyan-400/80 hover:text-white hover:bg-cyan-900/80 transition-colors cursor-pointer shrink-0"
            title="Liberar contexto militar (consultar todo el batallón)"
          >
            <X class="w-3.5 h-3.5" />
          </button>
        </div>

        <form @submit.prevent="enviarMensaje()" class="flex items-center gap-2">
          <input
            ref="inputRef"
            v-model="inputTexto"
            type="text"
            :disabled="isEnviando || !status?.online"
            :placeholder="activeMilitar ? `Pregunte sobre ${activeMilitar.nombre} (ej: ¿cuál es su novedad más frecuente?)...` : 'Pregunte sobre personal, novedades, fuerza disponible o días de ausencia...'"
            class="flex-1 bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-100 rounded-xl px-3.5 py-2.5 text-xs font-medium focus:outline-none transition-all placeholder:text-slate-600 disabled:opacity-50"
          />

          <!-- Botón Detener mientras se procesa -->
          <button
            v-if="isEnviando || isLoadingApreciacion"
            type="button"
            @click="detenerGeneracion"
            class="px-4 py-2.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 font-bold text-xs transition-all shadow-md shadow-rose-500/10 cursor-pointer flex items-center gap-1.5 shrink-0 animate-pulse"
            title="Detener generación de respuesta"
          >
            <Square class="w-3.5 h-3.5 fill-rose-300" />
            <span>Detener</span>
          </button>

          <!-- Botón Consultar normal -->
          <button
            v-else
            type="submit"
            :disabled="!inputTexto.trim() || !status?.online"
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
import { ref, watch, nextTick, onMounted, onUnmounted, computed } from 'vue'
import {
  Bot,
  X,
  Sparkles,
  ShieldCheck,
  ArrowRight,
  Database,
  Table2,
  Loader2,
  Send,
  Settings,
  Globe,
  Check,
  AlertCircle,
  Copy,
  Pencil,
  Square
} from 'lucide-vue-next'

import type { IAStatusResponse, IAChatMessage, ActiveMilitar } from '../types/ia.types'
import { iaService } from '../services/ia.service'
import { marked } from 'marked'

marked.setOptions({
  breaks: true,
  gfm: true
})

const renderMarkdown = (text: string): string => {
  if (!text) return ''
  try {
    return marked.parse(text) as string
  } catch {
    return text
  }
}

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
const activeMilitar = ref<ActiveMilitar | null>(null)

const limpiarMilitarActivo = () => {
  activeMilitar.value = null
}

const mostrarConfig = ref(false)

// Cronómetro en vivo y fases de razonamiento
const tiempoTranscurrido = ref(0)
const ultimoMensajeUsuario = ref('')
let timerInterval: any = null

const esConversacionSimple = computed(() => {
  const q = ultimoMensajeUsuario.value.toLowerCase().trim()
  if (!q) return false
  const patronesConversacion = [
    /^(hola|buen(as|os)?(\s+(dias|tardes|noches))?|saludos|que\s+tal|hey)\b/i,
    /^(gracias|muchas\s+gracias|mil\s+gracias|vale|de\s+acuerdo|perfecto|ok|listo)\b/i,
    /^(que\s+puedes\s+hacer|quien\s+eres|como\s+te\s+llamas|como\s+funcionas|ayuda)\b/i,
    /^(chao|adios|hasta\s+luego|hasta\s+pronto)\b/i
  ]
  return patronesConversacion.some(p => p.test(q))
})

const iniciarTimer = () => {
  tiempoTranscurrido.value = 0
  clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    tiempoTranscurrido.value++
  }, 1000)
}

const detenerTimer = () => {
  clearInterval(timerInterval)
}

const isGemini = computed(() => (status.value?.backend || 'gemini').includes('gemini'))

const faseCargaTexto = computed(() => {
  if (isLoadingApreciacion.value) {
    return 'Generando Apreciación de Situación de Personal...'
  }

  const modelName = status.value?.model_configured || (isGemini.value ? 'Gemini' : 'Ollama')

  if (esConversacionSimple.value) {
    if (tiempoTranscurrido.value < 4) {
      return 'Procesando respuesta del Asistente...'
    } else {
      return `Consultando ${modelName}...`
    }
  }

  if (tiempoTranscurrido.value < 3) {
    return 'Analizando consulta militar...'
  } else if (tiempoTranscurrido.value < 8) {
    return `Generando análisis con ${modelName}...`
  } else if (tiempoTranscurrido.value < 18) {
    return 'Consultando base de datos PostgreSQL...'
  } else {
    return 'Sintetizando informe militar final...'
  }
})

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
      backend: 'gemini',
      model_configured: 'gemini-3.5-flash-lite',
      api_key_configured: false,
      error: 'Error de conexión con el backend'
    }
  } finally {
    isLoadingStatus.value = false
  }
}

// ---------------------------------------------------------------------------
// 1. Funcionalidad: Copiar Mensaje al Portapapeles (con fallback seguro)
// ---------------------------------------------------------------------------
const mensajeCopiadoId = ref<string | null>(null)
let copiadoTimeout: any = null

const copiarTexto = async (msgId: string, texto: string) => {
  if (!texto) return
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(texto)
    } else {
      const textArea = document.createElement('textarea')
      textArea.value = texto
      textArea.style.position = 'fixed'
      textArea.style.opacity = '0'
      document.body.appendChild(textArea)
      textArea.select()
      document.execCommand('copy')
      document.body.removeChild(textArea)
    }
    mensajeCopiadoId.value = msgId
    clearTimeout(copiadoTimeout)
    copiadoTimeout = setTimeout(() => {
      mensajeCopiadoId.value = null
    }, 2000)
  } catch (err) {
    console.error('Error al copiar al portapapeles:', err)
  }
}

// ---------------------------------------------------------------------------
// 2. Funcionalidad: Editar Mensaje del Usuario
// ---------------------------------------------------------------------------
const editandoMensajeId = ref<string | null>(null)
const textoEdicion = ref('')

const iniciarEdicion = (msg: IAChatMessage) => {
  if (isEnviando.value || isLoadingApreciacion.value) return
  editandoMensajeId.value = msg.id
  textoEdicion.value = msg.text
}

const cancelarEdicion = () => {
  editandoMensajeId.value = null
  textoEdicion.value = ''
}

const guardarYReenviarEdicion = async (msgIdx: number) => {
  const nuevoTexto = textoEdicion.value.trim()
  if (!nuevoTexto || isEnviando.value) return

  editandoMensajeId.value = null
  textoEdicion.value = ''

  // Truncar historial removiendo este mensaje y las respuestas que generó
  mensajes.value = mensajes.value.slice(0, msgIdx)

  // Re-ejecutar consulta con el nuevo mensaje editado
  await enviarMensaje(nuevoTexto)
}

// ---------------------------------------------------------------------------
// 3. Funcionalidad: Detener / Cancelar Respuesta de IA (AbortController)
// ---------------------------------------------------------------------------
const abortController = ref<AbortController | null>(null)

const detenerGeneracion = () => {
  if (abortController.value) {
    try {
      abortController.value.abort()
    } catch {}
    abortController.value = null
  }
  detenerTimer()
  isEnviando.value = false
  isLoadingApreciacion.value = false

  const stoppedMsg: IAChatMessage = {
    id: String(Date.now()),
    sender: 'assistant',
    text: '⏹️ *Generación de respuesta detenida por el usuario.*',
    type: 'conversation',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  mensajes.value.push(stoppedMsg)
  scrollAlFondo()
}

const enviarMensajeDirecto = (texto: string) => {
  enviarMensaje(texto)
}

const enviarMensaje = async (customQuery?: string) => {
  const query = (customQuery !== undefined ? customQuery : inputTexto.value).trim()
  if (!query || isEnviando.value) return

  ultimoMensajeUsuario.value = query

  const userMsg: IAChatMessage = {
    id: String(Date.now()),
    sender: 'user',
    text: query,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  mensajes.value.push(userMsg)
  if (customQuery === undefined) {
    inputTexto.value = ''
  }
  isEnviando.value = true
  iniciarTimer()
  scrollAlFondo()

  const historyPayload = mensajes.value
    .filter(m => !m.isError && m.text !== query)
    .slice(-4)
    .map(m => ({ sender: m.sender, text: m.text }))

  abortController.value = new AbortController()

  try {
    const res = await iaService.enviarMensaje(
      query,
      historyPayload,
      activeMilitar.value,
      abortController.value.signal
    )
    if (res.active_militar !== undefined) {
      activeMilitar.value = res.active_militar
    }
    const assistantMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: res.answer,
      type: res.type,
      sql: res.sql,
      columns: res.columns,
      rows: res.rows,
      total_records: res.total_records,
      elapsed_seconds: res.elapsed_seconds || tiempoTranscurrido.value,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isError: res.type === 'error'
    }
    mensajes.value.push(assistantMsg)
  } catch (err: any) {
    if (err.name === 'AbortError' || err.message?.includes('aborted') || err.message?.includes('cancel')) {
      // Detención controlada por el usuario
      return
    }
    const errorMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: err.message || 'Ocurrió un error al procesar la consulta. Verifique que la API Key de Gemini esté configurada.',
      type: 'error',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isError: true
    }
    mensajes.value.push(errorMsg)
  } finally {
    abortController.value = null
    detenerTimer()
    isEnviando.value = false
    scrollAlFondo()
  }
}

const generarApreciacionDirecta = async () => {
  if (isLoadingApreciacion.value || isEnviando.value) return
  isLoadingApreciacion.value = true
  iniciarTimer()

  const userMsg: IAChatMessage = {
    id: String(Date.now()),
    sender: 'user',
    text: 'Generar Apreciación de Situación y Estado de Fuerza para la Comandancia',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  mensajes.value.push(userMsg)
  scrollAlFondo()

  abortController.value = new AbortController()

  try {
    const res = await iaService.generarApreciacion('TODOS', abortController.value.signal)
    const assistantMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: res.apreciacion,
      type: 'data',
      elapsed_seconds: tiempoTranscurrido.value,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    mensajes.value.push(assistantMsg)
  } catch (err: any) {
    if (err.name === 'AbortError' || err.message?.includes('aborted') || err.message?.includes('cancel')) {
      return
    }
    const errorMsg: IAChatMessage = {
      id: String(Date.now() + 1),
      sender: 'assistant',
      text: err.message || 'Error generando apreciación con el Asistente IA.',
      type: 'error',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isError: true
    }
    mensajes.value.push(errorMsg)
  } finally {
    abortController.value = null
    detenerTimer()
    isLoadingApreciacion.value = false
    scrollAlFondo()
  }
}

const limpiarChat = () => {
  mensajes.value = []
  activeMilitar.value = null
}

const cerrar = () => {
  if (isEnviando.value || isLoadingApreciacion.value) {
    detenerGeneracion()
  }
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

onUnmounted(() => {
  detenerTimer()
  if (abortController.value) {
    try {
      abortController.value.abort()
    } catch {}
  }
})
</script>

<style scoped>
:deep(.markdown-content) {
  line-height: 1.6;
}

:deep(.markdown-content p) {
  margin-bottom: 0.6rem;
}

:deep(.markdown-content p:last-child) {
  margin-bottom: 0;
}

:deep(.markdown-content strong) {
  font-weight: 700;
  color: #f8fafc;
}

:deep(.markdown-content h1),
:deep(.markdown-content h2),
:deep(.markdown-content h3),
:deep(.markdown-content h4) {
  font-weight: 700;
  color: #38bdf8;
  margin-top: 0.75rem;
  margin-bottom: 0.35rem;
}

:deep(.markdown-content h1) {
  font-size: 1rem;
}

:deep(.markdown-content h2) {
  font-size: 0.925rem;
}

:deep(.markdown-content h3) {
  font-size: 0.85rem;
}

:deep(.markdown-content ul) {
  list-style-type: disc;
  padding-left: 1.25rem;
  margin-top: 0.35rem;
  margin-bottom: 0.6rem;
}

:deep(.markdown-content ol) {
  list-style-type: decimal;
  padding-left: 1.25rem;
  margin-top: 0.35rem;
  margin-bottom: 0.6rem;
}

:deep(.markdown-content li) {
  margin-bottom: 0.25rem;
}

:deep(.markdown-content code) {
  background-color: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(56, 189, 248, 0.25);
  color: #7dd3fc;
  padding: 0.1rem 0.3rem;
  border-radius: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.8em;
}

:deep(.markdown-content pre) {
  background-color: #020617;
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  overflow-x: auto;
  margin: 0.5rem 0;
}

:deep(.markdown-content pre code) {
  background: transparent;
  border: none;
  padding: 0;
  color: #e2e8f0;
}

:deep(.markdown-content blockquote) {
  border-left: 3px solid #06b6d4;
  padding-left: 0.75rem;
  color: #94a3b8;
  font-style: italic;
  margin: 0.5rem 0;
}

:deep(.markdown-content hr) {
  border: none;
  border-top: 1px solid rgba(51, 65, 85, 0.6);
  margin: 0.75rem 0;
}
</style>

