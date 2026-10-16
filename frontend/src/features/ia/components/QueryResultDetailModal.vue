<template>
  <Teleport to="body">
    <transition name="modal-fade">
      <div 
        v-if="isOpen" 
        class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-6 bg-slate-950/85 backdrop-blur-md"
        @click.self="cerrar"
        @keydown.esc="cerrar"
        tabindex="0"
        ref="modalOverlayRef"
      >
        <div 
          class="glass-panel w-full max-w-6xl max-h-[92vh] rounded-3xl border border-darkBorder flex flex-col shadow-2xl relative overflow-hidden bg-slate-900/95"
          role="dialog"
          aria-modal="true"
        >
          <!-- Header del Modal -->
          <div class="px-5 sm:px-7 py-4 sm:py-5 border-b border-darkBorder/80 bg-gradient-to-r from-darkCard/90 via-slate-900/90 to-darkCard/90 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-md shadow-cyan-500/10 shrink-0">
                <Table2 class="w-5 h-5 stroke-[2.5]" />
              </div>
              <div>
                <div class="flex items-center gap-2 flex-wrap">
                  <h3 class="text-sm sm:text-base font-black text-slate-100 uppercase tracking-wide">
                    {{ title || 'Detalle Completo de Consulta' }}
                  </h3>
                  <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                    {{ filteredRows.length }} {{ filteredRows.length === 1 ? 'registro' : 'registros' }}
                  </span>
                </div>
                <p class="text-[11px] text-slate-400 leading-tight mt-0.5">
                  Desglose íntegro sin límite de registros · BIMEJ 12
                </p>
              </div>
            </div>

            <!-- Acciones de Cabecera: Buscador y Botón Cerrar -->
            <div class="flex items-center gap-2.5">
              <!-- Buscador Rápido -->
              <div class="relative flex-1 sm:w-64">
                <Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input 
                  v-model="busqueda"
                  type="text"
                  placeholder="Filtrar por nombre, cédula..."
                  class="w-full pl-8 pr-7 py-1.5 rounded-xl bg-slate-950/80 border border-darkBorder/90 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all font-sans"
                />
                <button 
                  v-if="busqueda"
                  type="button"
                  @click="busqueda = ''"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs p-0.5"
                  title="Limpiar filtro"
                >
                  <X class="w-3 h-3" />
                </button>
              </div>

              <!-- Botón Copiar a Portapapeles (TSV para Excel) -->
              <button
                type="button"
                @click="copiarTabla"
                class="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-darkBorder text-slate-300 hover:text-cyan-300 text-xs font-semibold transition-all cursor-pointer shadow-sm active:scale-95 shrink-0"
                :title="copiado ? '¡Copiado al portapapeles!' : 'Copiar tabla completa para pegar en Excel'"
              >
                <Check v-if="copiado" class="w-3.5 h-3.5 text-emerald-400" />
                <Copy v-else class="w-3.5 h-3.5" />
                <span>{{ copiado ? 'Copiado' : 'Copiar' }}</span>
              </button>

              <!-- Botón Cerrar -->
              <button 
                type="button"
                @click="cerrar"
                class="text-slate-400 hover:text-slate-100 p-2 rounded-xl hover:bg-slate-800/80 transition-colors cursor-pointer shrink-0 border border-transparent hover:border-darkBorder"
                title="Cerrar modal (Esc)"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Consulta SQL en Acordeón Colapsable (Opcional) -->
          <div v-if="sql" class="px-5 sm:px-7 pt-3 pb-1 border-b border-darkBorder/50 bg-slate-950/40 shrink-0">
            <details class="group">
              <summary class="text-[10px] font-mono text-cyan-400/80 hover:text-cyan-300 cursor-pointer select-none flex items-center gap-1.5 transition-colors">
                <Terminal class="w-3 h-3" />
                <span class="font-bold">SENTENCIA SQL EJECUTADA</span>
                <span class="text-slate-500 group-open:hidden text-[9px]">(clic para ver)</span>
              </summary>
              <pre class="mt-2 p-2.5 rounded-xl bg-slate-950 border border-darkBorder text-[10px] font-mono text-cyan-200/90 overflow-x-auto whitespace-pre-wrap select-all">{{ sql }}</pre>
            </details>
          </div>

          <!-- Cuerpo: Tabla Cómoda con Scroll y Header Sticky -->
          <div class="overflow-auto flex-1 scrollbar-thin p-4 sm:p-6">
            <div class="rounded-2xl border border-darkBorder/80 bg-slate-950/50 overflow-hidden shadow-inner">
              <table class="w-full text-left text-xs border-collapse">
                <thead>
                  <tr class="border-b border-darkBorder/90 bg-slate-950 sticky top-0 text-[10px] font-mono text-slate-400 uppercase tracking-wider z-10 backdrop-blur-md">
                    <th class="w-12 px-3 py-3 text-center text-slate-500 font-bold border-r border-darkBorder/40">
                      #
                    </th>
                    <th 
                      v-for="col in columns" 
                      :key="col" 
                      class="px-4 py-3 font-bold text-slate-300 select-none"
                    >
                      {{ col.replace(/_/g, ' ') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-darkBorder/40 font-mono text-[11px]">
                  <tr 
                    v-for="(row, idx) in filteredRows" 
                    :key="idx"
                    class="hover:bg-cyan-500/10 transition-colors odd:bg-slate-900/50 even:bg-slate-900/20"
                  >
                    <!-- Numeración de fila -->
                    <td class="w-12 px-3 py-2.5 text-center text-slate-500 text-[10px] font-bold border-r border-darkBorder/40 select-none">
                      {{ idx + 1 }}
                    </td>

                    <!-- Columnas de datos con formato inteligente -->
                    <td 
                      v-for="col in columns" 
                      :key="col"
                      class="px-4 py-2.5 whitespace-nowrap"
                    >
                      <!-- Cédula destacada -->
                      <span 
                        v-if="col.toLowerCase() === 'cedula'" 
                        class="font-bold text-cyan-300 font-mono select-all tracking-wider"
                      >
                        {{ formatValue(row[col]) }}
                      </span>

                      <!-- Nombre en fuente clara y legible -->
                      <span 
                        v-else-if="col.toLowerCase() === 'nombre'" 
                        class="font-semibold text-slate-100 font-sans tracking-wide"
                      >
                        {{ formatValue(row[col]) }}
                      </span>

                      <!-- Novedad con badge de color -->
                      <span 
                        v-else-if="col.toLowerCase() === 'novedad'" 
                        class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider"
                        :class="getNovedadBadgeClass(String(row[col]))"
                      >
                        {{ formatValue(row[col]) }}
                      </span>

                      <!-- Días numéricos destacados -->
                      <span 
                        v-else-if="col.toLowerCase() === 'dias' || col.toLowerCase() === 'total_dias'"
                        class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
                      >
                        {{ formatValue(row[col]) }} días
                      </span>

                      <!-- Fechas -->
                      <span 
                        v-else-if="col.toLowerCase().includes('fecha') || col.toLowerCase() === 'desde' || col.toLowerCase() === 'hasta'"
                        class="text-slate-300 font-mono text-[10px]"
                      >
                        {{ formatValue(row[col]) }}
                      </span>

                      <!-- Texto genérico -->
                      <span v-else class="text-slate-300 font-sans text-xs">
                        {{ formatValue(row[col]) }}
                      </span>
                    </td>
                  </tr>

                  <!-- Estado Vacío por Búsqueda -->
                  <tr v-if="filteredRows.length === 0">
                    <td :colspan="columns.length + 1" class="py-12 text-center text-slate-400">
                      <div class="flex flex-col items-center justify-center gap-2">
                        <AlertCircle class="w-8 h-8 text-slate-600 stroke-1" />
                        <p class="text-xs font-semibold text-slate-300">
                          No se encontraron coincidencias para "{{ busqueda }}"
                        </p>
                        <button
                          type="button"
                          @click="busqueda = ''"
                          class="mt-1 text-xs text-cyan-400 hover:underline"
                        >
                          Limpiar filtro de búsqueda
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Footer del Modal -->
          <div class="px-5 sm:px-7 py-3.5 border-t border-darkBorder/80 bg-slate-950/70 flex items-center justify-between text-xs text-slate-400 shrink-0">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-slate-300">
                Mostrando {{ filteredRows.length }} de {{ rows.length }} registros
              </span>
              <span v-if="busqueda" class="text-cyan-400 text-[11px]">
                (filtrados por "{{ busqueda }}")
              </span>
            </div>

            <button
              type="button"
              @click="cerrar"
              class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-darkBorder text-slate-200 hover:text-white font-bold text-xs transition-all cursor-pointer shadow-sm active:scale-95"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  Table2,
  X,
  Search,
  Copy,
  Check,
  Terminal,
  AlertCircle
} from 'lucide-vue-next'

const props = defineProps<{
  isOpen: boolean
  columns: string[]
  rows: Record<string, any>[]
  totalRecords?: number
  sql?: string | null
  title?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const busqueda = ref('')
const copiado = ref(false)
const modalOverlayRef = ref<HTMLDivElement | null>(null)

const cerrar = () => {
  emit('close')
}

// Autoenfocar el overlay al abrir para permitir cerrar con tecla Escape
watch(() => props.isOpen, (open) => {
  if (open) {
    busqueda.value = ''
    copiado.value = false
    nextTick(() => {
      modalOverlayRef.value?.focus()
    })
  }
})

// Filtrado reactivo en tiempo real por cualquier campo
const filteredRows = computed(() => {
  if (!busqueda.value.trim()) {
    return props.rows
  }
  const term = busqueda.value.trim().toLowerCase()
  return props.rows.filter(row => {
    return Object.values(row).some(val => {
      if (val === null || val === undefined) return false
      return String(val).toLowerCase().includes(term)
    })
  })
})

const formatValue = (val: any): string => {
  if (val === null || val === undefined || val === '') return '-'
  return String(val)
}

const getNovedadBadgeClass = (novedad: string): string => {
  const n = (novedad || '').toUpperCase()
  if (n.includes('VACACION')) {
    return 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
  }
  if (n.includes('PERMISO')) {
    return 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
  }
  if (n.includes('INCAPACIDAD') || n.includes('EXCUSA') || n.includes('MEDIC') || n.includes('SANIDAD')) {
    return 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
  }
  if (n.includes('GUARDIA') || n.includes('SERVICIO')) {
    return 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
  }
  if (n.includes('DISPONIBLE')) {
    return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
  }
  return 'bg-slate-800 text-slate-300 border border-slate-700'
}

// Copiar tabla completa a portapapeles en formato TSV (compatible con Excel/Sheets)
const copiarTabla = async () => {
  try {
    const headers = props.columns.join('\t')
    const rowsText = props.rows.map(r => {
      return props.columns.map(c => r[c] !== null && r[c] !== undefined ? String(r[c]) : '').join('\t')
    }).join('\n')
    const fullText = `${headers}\n${rowsText}`

    await navigator.clipboard.writeText(fullText)
    copiado.value = true
    setTimeout(() => {
      copiado.value = false
    }, 2500)
  } catch (err) {
    console.error('Error al copiar al portapapeles:', err)
  }
}
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  transform: scale(0.97);
}
</style>
