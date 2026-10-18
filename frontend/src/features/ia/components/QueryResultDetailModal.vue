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
          <!-- 1. Header del Modal -->
          <div class="px-5 sm:px-7 py-4 border-b border-darkBorder/80 bg-gradient-to-r from-darkCard/90 via-slate-900/90 to-darkCard/90 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shrink-0">
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
                  Desglose íntegro y previsualización de formatos oficiales · BIMEJ 12
                </p>
              </div>
            </div>

            <!-- Acciones de Cabecera: Buscador, Copiar y Botón Cerrar -->
            <div class="flex items-center gap-2.5">
              <!-- Buscador Rápido -->
              <div class="relative flex-1 sm:w-60">
                <Search class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input 
                  v-model="busqueda"
                  type="text"
                  placeholder="Filtrar en vista actual..."
                  class="w-full pl-8 pr-7 py-1.5 rounded-xl bg-slate-950/80 border border-darkBorder/90 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 focus:ring-1 focus:ring-cyan-500/30 transition-all font-sans"
                />
                <button 
                  v-if="busqueda"
                  type="button"
                  @click="busqueda = ''"
                  class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 text-xs p-0.5 cursor-pointer"
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
                :title="copiado ? '¡Copiado al portapapeles!' : `Copiar vista ${formatoTituloActual} para pegar en Excel`"
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

          <!-- 2. Barra de Selección de Formato y Botones Principales de Exportación -->
          <div class="px-5 sm:px-7 py-2.5 bg-slate-950/80 border-b border-darkBorder/70 flex flex-col md:flex-row md:items-center justify-between gap-3 shrink-0">
            <!-- Tabs de Formato Oficial de Reporte -->
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1 mr-1 select-none">
                <FileSpreadsheet class="w-3.5 h-3.5 text-cyan-400" />
                Formato de Reporte:
              </span>

              <!-- Opción A: Tabla Actual de Consulta -->
              <button
                type="button"
                @click="formatoSeleccionado = 'consulta'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                :class="formatoSeleccionado === 'consulta'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-darkBorder/70 hover:border-slate-700'"
                title="Ver exactamente la tabla resultante de la consulta SQL"
              >
                <Table2 class="w-3.5 h-3.5" />
                <span>Tabla de Consulta</span>
                <span class="px-1.5 py-0.2 rounded text-[9px] bg-cyan-500/20 text-cyan-300 font-mono">
                  {{ filteredRows.length }}
                </span>
              </button>

              <!-- Opción B: Matriz Heatmap -->
              <button
                type="button"
                @click="formatoSeleccionado = 'heatmap'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                :class="formatoSeleccionado === 'heatmap'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50 shadow-sm'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-darkBorder/70 hover:border-slate-700'"
                title="Previsualizar cómo quedará la Matriz Heatmap diaria consolidada"
              >
                <Layers class="w-3.5 h-3.5 text-purple-400" />
                <span>Matriz Heatmap</span>
              </button>

              <!-- Opción C: Parte Ágil -->
              <button
                type="button"
                @click="formatoSeleccionado = 'agil'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                :class="formatoSeleccionado === 'agil'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-darkBorder/70 hover:border-slate-700'"
                title="Previsualizar cómo quedará el Parte Ágil de novedades agrupadas por rangos"
              >
                <Zap class="w-3.5 h-3.5 text-amber-400" />
                <span>Parte Ágil</span>
              </button>

              <!-- Opción D: Estadística de Totales -->
              <button
                type="button"
                @click="formatoSeleccionado = 'estadistica'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                :class="formatoSeleccionado === 'estadistica'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-sm'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-darkBorder/70 hover:border-slate-700'"
                title="Previsualizar estadísticas y totales acumulados por novedad"
              >
                <BarChart3 class="w-3.5 h-3.5 text-emerald-400" />
                <span>Estadística Totales</span>
              </button>
            </div>

            <!-- Botones ÚNICOS de Exportación Oficial -->
            <div class="flex items-center gap-2 shrink-0">
              <!-- Botón Excel -->
              <button
                type="button"
                @click="descargarFormato('excel')"
                :disabled="isExportando"
                class="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 hover:text-emerald-200 font-bold text-xs transition-all flex items-center gap-1.5 cursor-pointer shadow-sm active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                :title="`Exportar ${formatoTituloActual} en Excel (.xlsx)`"
              >
                <Loader2 v-if="isExportando && exportandoTipo === 'excel'" class="w-3.5 h-3.5 animate-spin text-emerald-400" />
                <FileSpreadsheet v-else class="w-3.5 h-3.5" />
                <span>Excel (.xlsx)</span>
              </button>

              <!-- Botón PDF -->
              <button
                type="button"
                @click="descargarFormato('pdf')"
                :disabled="isExportando"
                class="px-3.5 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 hover:text-cyan-200 font-bold text-xs transition-all flex items-center gap-1.5 cursor-pointer shadow-sm active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                :title="`Exportar ${formatoTituloActual} en PDF (.pdf)`"
              >
                <Loader2 v-if="isExportando && exportandoTipo === 'pdf'" class="w-3.5 h-3.5 animate-spin text-cyan-400" />
                <FileText v-else class="w-3.5 h-3.5" />
                <span>PDF (.pdf)</span>
              </button>
            </div>
          </div>

          <!-- 3. Inspector SQL en Acordeón Colapsable (Opcional) -->
          <div v-if="sql" class="px-5 sm:px-7 pt-2.5 pb-1 border-b border-darkBorder/50 bg-slate-950/40 shrink-0">
            <details class="group">
              <summary class="text-[10px] font-mono text-cyan-400/80 hover:text-cyan-300 cursor-pointer select-none flex items-center gap-1.5 transition-colors">
                <Terminal class="w-3 h-3" />
                <span class="font-bold">SENTENCIA SQL EJECUTADA</span>
                <span class="text-slate-500 group-open:hidden text-[9px]">(clic para ver)</span>
              </summary>
              <pre class="mt-2 p-2.5 rounded-xl bg-slate-950 border border-darkBorder text-[10px] font-mono text-cyan-200/90 overflow-x-auto whitespace-pre-wrap select-all">{{ sql }}</pre>
            </details>
          </div>

          <!-- 4. Cuerpo Principal Dinámico según el Formato de Reporte Seleccionado -->
          <div class="overflow-auto flex-1 scrollbar-thin p-4 sm:p-6">
            
            <!-- VISTA 1: TABLA DE CONSULTA -->
            <div v-if="formatoSeleccionado === 'consulta'" class="rounded-2xl border border-darkBorder/80 bg-slate-950/50 overflow-hidden shadow-inner">
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
                          class="mt-1 text-xs text-cyan-400 hover:underline cursor-pointer"
                        >
                          Limpiar filtro de búsqueda
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- VISTA 2: MATRIZ HEATMAP CONSOLIDADA -->
            <div v-else-if="formatoSeleccionado === 'heatmap'" class="flex flex-col gap-3">
              <!-- Encabezado de la Vista Previa del Heatmap y Leyenda -->
              <div class="p-3.5 rounded-2xl border border-purple-500/30 bg-purple-950/20 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                <div>
                  <div class="flex items-center gap-2 font-bold text-purple-300">
                    <Layers class="w-4 h-4" />
                    <span>PREVISUALIZACIÓN DE MATRIZ HEATMAP DÍA A DÍA</span>
                  </div>
                  <p class="text-[11px] text-slate-400 mt-0.5">
                    Mes en matriz: <strong class="text-slate-200">{{ activeHeatmapMonth.monthName }} {{ activeHeatmapMonth.year }}</strong> ({{ activeHeatmapMonth.daysCount }} días).
                    <span v-if="detectedMonthsList.length > 1" class="text-purple-300 ml-1 font-semibold">
                      · Período total consultado: {{ detectedPeriodLabel }}
                    </span>
                  </p>
                </div>
                <!-- Leyenda de Colores del Heatmap -->
                <div class="flex items-center gap-2 flex-wrap text-[10px] font-mono">
                  <span class="inline-flex items-center gap-1 text-emerald-300">
                    <span class="w-2.5 h-2.5 rounded bg-emerald-500/40 border border-emerald-500/60 inline-block"></span>
                    D (Disponible)
                  </span>
                  <span class="inline-flex items-center gap-1 text-purple-300">
                    <span class="w-2.5 h-2.5 rounded bg-purple-500/40 border border-purple-500/60 inline-block"></span>
                    C (Cdo Unidad)
                  </span>
                  <span class="inline-flex items-center gap-1 text-blue-300">
                    <span class="w-2.5 h-2.5 rounded bg-blue-500/40 border border-blue-500/60 inline-block"></span>
                    P (Permiso)
                  </span>
                  <span class="inline-flex items-center gap-1 text-amber-300">
                    <span class="w-2.5 h-2.5 rounded bg-amber-500/40 border border-amber-500/60 inline-block"></span>
                    I (Incapacidad)
                  </span>
                  <span class="inline-flex items-center gap-1 text-cyan-300">
                    <span class="w-2.5 h-2.5 rounded bg-cyan-500/40 border border-cyan-500/60 inline-block"></span>
                    V (Vacaciones)
                  </span>
                </div>
              </div>

              <!-- Selector de Meses cuando la consulta abarca un rango de varios meses -->
              <div 
                v-if="detectedMonthsList.length > 1" 
                class="px-4 py-2.5 rounded-2xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-between gap-3 flex-wrap"
              >
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="text-[11px] font-bold uppercase tracking-wider text-purple-300 flex items-center gap-1 mr-1 select-none">
                    <Calendar class="w-3.5 h-3.5 text-purple-400" />
                    Inspeccionar Mes en Matriz:
                  </span>
                  <button
                    v-for="m in detectedMonthsList"
                    :key="m.key"
                    type="button"
                    @click="selectedHeatmapMonthKey = m.key"
                    class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 shadow-xs"
                    :class="selectedHeatmapMonthKey === m.key
                      ? 'bg-purple-500 text-white shadow-md shadow-purple-500/25 border border-purple-400'
                      : 'bg-slate-950/80 text-slate-300 hover:text-white hover:bg-slate-800 border border-darkBorder'"
                  >
                    <span>{{ m.monthName }} {{ m.year }}</span>
                    <span 
                      class="text-[10px] px-1.5 py-0.2 rounded font-mono font-bold"
                      :class="selectedHeatmapMonthKey === m.key ? 'bg-purple-700/80 text-purple-100' : 'bg-slate-800 text-slate-400'"
                    >
                      {{ m.countRows }}
                    </span>
                  </button>
                </div>
                <span class="text-[11px] text-slate-400 font-mono">
                  Mostrando {{ activeHeatmapMonth.monthName }}
                </span>
              </div>

              <!-- Tabla Matriz Heatmap con Scroll Horizontal -->
              <div class="rounded-2xl border border-darkBorder/80 bg-slate-950/60 overflow-x-auto shadow-inner">
                <table class="w-full text-left text-xs border-collapse min-w-[950px]">
                  <thead>
                    <tr class="border-b border-darkBorder/90 bg-slate-950 text-[10px] font-mono text-slate-400 uppercase tracking-wider sticky top-0 z-20">
                      <th class="w-10 px-2 py-3 text-center text-slate-500 font-bold border-r border-darkBorder/40">
                        #
                      </th>
                      <!-- Columna fija de Integrante -->
                      <th class="py-3 px-3 sm:px-4 w-52 md:w-60 text-left font-bold sticky left-0 bg-slate-950 text-slate-200 uppercase tracking-wider z-20 border-r border-darkBorder/40 shadow-[4px_0_10px_rgba(0,0,0,0.5)]">
                        Integrante
                      </th>
                      <!-- Total de Días con Novedad -->
                      <th class="w-20 px-2 py-3 text-center font-bold text-amber-300 border-r border-darkBorder/40">
                        Novedades
                      </th>
                      <!-- Columnas de Días 1..N -->
                      <th 
                        v-for="d in daysArray" 
                        :key="d"
                        class="py-2.5 text-center w-8 font-bold text-slate-400 select-none font-mono text-[10px]"
                        :title="`Día ${d} de ${activeHeatmapMonth.monthName}`"
                      >
                        {{ String(d).padStart(2, '0') }}
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-darkBorder/40 text-[11px]">
                    <tr 
                      v-for="(militar, idx) in paginatedHeatmapMilitares" 
                      :key="militar.cedula"
                      class="hover:bg-purple-500/5 transition-colors group"
                    >
                      <!-- Numeración considerando la página actual -->
                      <td class="w-10 px-2 py-2 text-center text-slate-500 text-[10px] font-bold border-r border-darkBorder/40 select-none">
                        {{ (heatmapPage - 1) * heatmapPageSize + idx + 1 }}
                      </td>

                      <!-- Nombre y Cédula Sticky -->
                      <td class="py-2 px-3 sm:px-4 font-bold text-slate-200 uppercase sticky left-0 bg-slate-900/95 z-10 group-hover:bg-slate-800 transition-colors border-r border-darkBorder/40 shadow-[4px_0_10px_rgba(0,0,0,0.5)]">
                        <div class="truncate text-xs text-slate-100 font-sans" :title="militar.nombre">
                          {{ militar.nombre }}
                        </div>
                        <span class="text-[10px] text-cyan-400 font-mono font-normal">
                          CC {{ militar.cedula }}
                        </span>
                      </td>

                      <!-- Contador de Novedades del Integrante -->
                      <td class="w-20 px-2 py-2 text-center border-r border-darkBorder/40">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 font-mono">
                          {{ militar.totalDiasNovedad }} d
                        </span>
                      </td>

                      <!-- Celdas de cada Día -->
                      <td 
                        v-for="d in daysArray" 
                        :key="d"
                        class="py-2 px-0.5 text-center w-8"
                      >
                        <div 
                          class="w-6 h-6 mx-auto rounded-md flex items-center justify-center font-bold text-[10px] font-mono transition-transform group-hover:scale-105 cursor-help shadow-sm"
                          :class="getHeatmapCellBadgeClass(militar.daysMap.get(d))"
                          :title="getHeatmapCellTooltip(militar, d)"
                        >
                          {{ getHeatmapCellShortLabel(militar.daysMap.get(d)) }}
                        </div>
                      </td>
                    </tr>

                    <tr v-if="filteredHeatmapMilitares.length === 0">
                      <td :colspan="daysArray.length + 3" class="py-12 text-center text-slate-400">
                        No hay registros para proyectar la matriz con los filtros actuales.
                      </td>
                    </tr>
                  </tbody>
                </table>

                <!-- Controles de Paginación para la Matriz Heatmap en Consultas Grandes -->
                <div 
                  v-if="filteredHeatmapMilitares.length > 25" 
                  class="px-4 py-2.5 bg-slate-900/90 border-t border-darkBorder/80 flex items-center justify-between text-xs text-slate-400 flex-wrap gap-2 sticky left-0"
                >
                  <div class="flex items-center gap-2">
                    <span>
                      Mostrando {{ (heatmapPage - 1) * heatmapPageSize + 1 }} - {{ Math.min(heatmapPage * heatmapPageSize, filteredHeatmapMilitares.length) }} de {{ filteredHeatmapMilitares.length }} efectivos
                    </span>
                    <select 
                      v-model.number="heatmapPageSize" 
                      class="bg-slate-950 border border-darkBorder rounded-lg px-2 py-1 text-slate-300 text-xs focus:outline-none focus:border-purple-500/50"
                    >
                      <option :value="25">25 por página</option>
                      <option :value="50">50 por página</option>
                      <option :value="100">100 por página</option>
                      <option :value="10000">Ver todos</option>
                    </select>
                  </div>
                  <div class="flex items-center gap-1.5" v-if="totalHeatmapPages > 1">
                    <button 
                      type="button" 
                      :disabled="heatmapPage <= 1"
                      @click="heatmapPage--"
                      class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold text-slate-200 transition-colors flex items-center gap-1"
                    >
                      <ChevronLeft class="w-3.5 h-3.5" />
                      <span>Anterior</span>
                    </button>
                    <span class="text-xs font-mono text-purple-300 font-bold px-2">
                      {{ heatmapPage }} / {{ totalHeatmapPages }}
                    </span>
                    <button 
                      type="button" 
                      :disabled="heatmapPage >= totalHeatmapPages"
                      @click="heatmapPage++"
                      class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-xs font-semibold text-slate-200 transition-colors flex items-center gap-1"
                    >
                      <span>Siguiente</span>
                      <ChevronRight class="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- VISTA 3: PARTE ÁGIL EJECUTIVO -->
            <div v-else-if="formatoSeleccionado === 'agil'" class="flex flex-col gap-4">
              <!-- Banner Superior del Parte Ágil -->
              <div class="p-3.5 rounded-2xl border border-amber-500/30 bg-amber-950/20 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                <div>
                  <div class="flex items-center gap-2 font-bold text-amber-300">
                    <Zap class="w-4 h-4" />
                    <span>PREVISUALIZACIÓN DE PARTE ÁGIL EJECUTIVO DE NOVEDADES</span>
                  </div>
                  <p class="text-[11px] text-slate-400 mt-0.5">
                    Extracto nominal consolidado por intervalos continuos de novedad · Período: <strong class="text-slate-200">{{ detectedPeriodLabel }}</strong>
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <span class="px-2.5 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono font-bold text-xs">
                    {{ agilSummaryRows.length }} efectivos en novedad
                  </span>
                </div>
              </div>

              <!-- Tabla Oficial del Parte Ágil -->
              <div class="rounded-2xl border border-darkBorder/80 bg-slate-950/60 overflow-hidden shadow-inner">
                <table class="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr class="border-b border-darkBorder/90 bg-slate-950 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                      <th class="w-12 px-3 py-3 text-center text-slate-500 font-bold border-r border-darkBorder/40">#</th>
                      <th class="w-32 px-4 py-3 font-bold text-slate-300">Cédula</th>
                      <th class="px-4 py-3 font-bold text-slate-300">Integrante</th>
                      <th class="px-4 py-3 font-bold text-slate-300">Resumen de Novedades por Rangos de Fecha</th>
                      <th class="w-28 px-4 py-3 text-center font-bold text-amber-300">Total Días</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-darkBorder/40 text-[11px]">
                    <tr 
                      v-for="(item, idx) in filteredAgilSummaryRows" 
                      :key="item.cedula"
                      class="hover:bg-amber-500/5 transition-colors odd:bg-slate-900/40 even:bg-slate-900/10"
                    >
                      <td class="w-12 px-3 py-3 text-center text-slate-500 font-bold border-r border-darkBorder/40 font-mono">
                        {{ idx + 1 }}
                      </td>
                      <td class="w-32 px-4 py-3 font-mono font-bold text-cyan-300 select-all">
                        {{ item.cedula }}
                      </td>
                      <td class="px-4 py-3 font-sans font-bold text-slate-100">
                        {{ item.nombre }}
                      </td>
                      <td class="px-4 py-3">
                        <div class="flex flex-wrap gap-1.5 items-center">
                          <span 
                            v-for="(rango, rIdx) in item.ranges" 
                            :key="rIdx"
                            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-mono font-medium border shadow-xs"
                            :class="getNovedadBadgeClass(rango.novedad)"
                          >
                            <span class="font-bold underline decoration-dotted">{{ rango.labelDays }}</span>
                            <span class="font-bold uppercase tracking-wider text-[10px]">({{ rango.novedad }})</span>
                          </span>
                        </div>
                      </td>
                      <td class="w-28 px-4 py-3 text-center">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 font-mono">
                          {{ item.totalDias }} días
                        </span>
                      </td>
                    </tr>

                    <tr v-if="filteredAgilSummaryRows.length === 0">
                      <td colspan="5" class="py-12 text-center text-slate-400">
                        No se encontraron registros de novedades para el Parte Ágil.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Desglose Adicional Agrupado por Tipo de Novedad -->
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <div 
                  v-for="cat in agilCategories" 
                  :key="cat.novedad"
                  class="p-3.5 rounded-2xl border border-darkBorder/70 bg-slate-900/60 flex flex-col justify-between"
                >
                  <div class="flex items-center justify-between gap-2 border-b border-darkBorder/40 pb-2">
                    <span 
                      class="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider"
                      :class="getNovedadBadgeClass(cat.novedad)"
                    >
                      {{ cat.novedad }}
                    </span>
                    <span class="text-xs font-mono font-bold text-amber-300">
                      {{ cat.totalDias }} días
                    </span>
                  </div>
                  <div class="mt-2 text-[11px] text-slate-300 space-y-1">
                    <div class="flex items-center justify-between text-slate-400 text-[10px]">
                      <span>Personal Afectado:</span>
                      <strong class="text-slate-200">{{ cat.militares.length }}</strong>
                    </div>
                    <p class="truncate text-slate-300 font-sans" :title="cat.militares.join(', ')">
                      {{ cat.militares.slice(0, 2).join(', ') }}{{ cat.militares.length > 2 ? ` y ${cat.militares.length - 2} más` : '' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- VISTA 4: ESTADÍSTICA DE TOTALES -->
            <div v-else-if="formatoSeleccionado === 'estadistica'" class="flex flex-col gap-4">
              <!-- Banner Superior de Estadísticas -->
              <div class="p-3.5 rounded-2xl border border-emerald-500/30 bg-emerald-950/20 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
                <div>
                  <div class="flex items-center gap-2 font-bold text-emerald-300">
                    <BarChart3 class="w-4 h-4" />
                    <span>PREVISUALIZACIÓN DE ESTADÍSTICAS Y TOTALES DE AFECTACIÓN</span>
                  </div>
                  <p class="text-[11px] text-slate-400 mt-0.5">
                    Consolidado analítico de distribución porcentual y métricas de ausentismo militar · Período: <strong class="text-slate-200">{{ detectedPeriodLabel }}</strong>
                  </p>
                </div>
              </div>

              <!-- Grid de Tarjetas KPI -->
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <!-- KPI 1: Días Totales -->
                <div class="p-3.5 rounded-2xl border border-darkBorder/70 bg-slate-900/80 flex flex-col justify-between">
                  <div class="flex items-center justify-between text-slate-400 text-xs">
                    <span>Días Registrados</span>
                    <Calendar class="w-4 h-4 text-cyan-400" />
                  </div>
                  <div class="mt-2 text-2xl font-black font-mono text-cyan-300">
                    {{ estadisticasGenerales.totalDias }}
                  </div>
                  <span class="text-[10px] text-slate-500 mt-0.5">Días de afectación sumados</span>
                </div>

                <!-- KPI 2: Personal Afectado -->
                <div class="p-3.5 rounded-2xl border border-darkBorder/70 bg-slate-900/80 flex flex-col justify-between">
                  <div class="flex items-center justify-between text-slate-400 text-xs">
                    <span>Efectivos Involucrados</span>
                    <Users class="w-4 h-4 text-purple-400" />
                  </div>
                  <div class="mt-2 text-2xl font-black font-mono text-purple-300">
                    {{ estadisticasGenerales.totalMilitares }}
                  </div>
                  <span class="text-[10px] text-slate-500 mt-0.5">Militares con reportes</span>
                </div>

                <!-- KPI 3: Tipos de Novedad -->
                <div class="p-3.5 rounded-2xl border border-darkBorder/70 bg-slate-900/80 flex flex-col justify-between">
                  <div class="flex items-center justify-between text-slate-400 text-xs">
                    <span>Categorías Activas</span>
                    <Layers class="w-4 h-4 text-amber-400" />
                  </div>
                  <div class="mt-2 text-2xl font-black font-mono text-amber-300">
                    {{ estadisticasGenerales.totalCategorias }}
                  </div>
                  <span class="text-[10px] text-slate-500 mt-0.5">Causales de ausencia</span>
                </div>

                <!-- KPI 4: Novedad Predominante -->
                <div class="p-3.5 rounded-2xl border border-darkBorder/70 bg-slate-900/80 flex flex-col justify-between">
                  <div class="flex items-center justify-between text-slate-400 text-xs">
                    <span>Causa Principal</span>
                    <TrendingUp class="w-4 h-4 text-emerald-400" />
                  </div>
                  <div class="mt-2 text-base font-black truncate font-sans text-emerald-300" :title="estadisticasGenerales.novedadTop">
                    {{ estadisticasGenerales.novedadTop }}
                  </div>
                  <span class="text-[10px] text-emerald-400/80 font-mono font-bold mt-0.5">
                    {{ estadisticasGenerales.porcentajeTop }}% del total
                  </span>
                </div>
              </div>

              <!-- Tabla Detallada de Distribución Porcentual con Barras Visuales -->
              <div class="rounded-2xl border border-darkBorder/80 bg-slate-950/60 overflow-hidden shadow-inner">
                <table class="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr class="border-b border-darkBorder/90 bg-slate-950 text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                      <th class="w-12 px-3 py-3 text-center text-slate-500 font-bold border-r border-darkBorder/40">#</th>
                      <th class="w-48 px-4 py-3 font-bold text-slate-300">Tipo de Novedad</th>
                      <th class="w-28 px-4 py-3 text-center font-bold text-slate-300">Días Totales</th>
                      <th class="w-28 px-4 py-3 text-center font-bold text-slate-300">Efectivos</th>
                      <th class="w-24 px-4 py-3 text-center font-bold text-cyan-300">% del Total</th>
                      <th class="px-4 py-3 font-bold text-slate-300">Distribución Gráfica</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-darkBorder/40 text-[11px]">
                    <tr 
                      v-for="(item, idx) in filteredEstadisticasDistribucion" 
                      :key="item.novedad"
                      class="hover:bg-emerald-500/5 transition-colors odd:bg-slate-900/40 even:bg-slate-900/10"
                    >
                      <td class="w-12 px-3 py-3 text-center text-slate-500 font-bold border-r border-darkBorder/40 font-mono">
                        {{ idx + 1 }}
                      </td>
                      <td class="w-48 px-4 py-3">
                        <span 
                          class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider"
                          :class="getNovedadBadgeClass(item.novedad)"
                        >
                          {{ item.novedad }}
                        </span>
                      </td>
                      <td class="w-28 px-4 py-3 text-center font-mono font-bold text-slate-200">
                        {{ item.dias }}
                      </td>
                      <td class="w-28 px-4 py-3 text-center font-mono text-slate-300">
                        {{ item.militaresCount }}
                      </td>
                      <td class="w-24 px-4 py-3 text-center font-mono font-bold text-cyan-300">
                        {{ item.porcentaje }}%
                      </td>
                      <td class="px-4 py-3">
                        <div class="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden border border-darkBorder/50 flex">
                          <div 
                            class="h-full rounded-full transition-all duration-500"
                            :class="getProgressGradientClass(item.novedad)"
                            :style="{ width: `${item.porcentaje}%` }"
                          ></div>
                        </div>
                      </td>
                    </tr>

                    <tr v-if="filteredEstadisticasDistribucion.length === 0">
                      <td colspan="6" class="py-12 text-center text-slate-400">
                        No hay datos estadísticos para mostrar.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>

          <!-- 5. Footer del Modal: Limpio y Sin Botones Redundantes -->
          <div class="px-5 sm:px-7 py-3.5 border-t border-darkBorder/80 bg-slate-950/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400 shrink-0">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-slate-300">
                Mostrando {{ filteredRows.length }} de {{ rows.length }} registros
              </span>
              <span v-if="busqueda" class="text-cyan-400 text-[11px]">
                (filtrados por "{{ busqueda }}")
              </span>
            </div>

            <!-- Botón Único de Cierre en Footer -->
            <div class="flex items-center gap-2.5">
              <button
                type="button"
                @click="cerrar"
                class="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-darkBorder text-slate-200 hover:text-white font-bold text-xs transition-all cursor-pointer shadow-sm active:scale-95"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onErrorCaptured } from 'vue'
import {
  Table2,
  X,
  Search,
  Copy,
  Check,
  Terminal,
  AlertCircle,
  FileSpreadsheet,
  FileText,
  Layers,
  Zap,
  BarChart3,
  Loader2,
  Calendar,
  Users,
  TrendingUp,
  ChevronLeft,
  ChevronRight
} from 'lucide-vue-next'
import { iaService } from '../services/ia.service'
import { useReportDownloadStore } from '@stores/reportDownloadStore'
import { useDateStore } from '@stores/dateStore'
import type { IAReportInfo, ActiveMilitar } from '../types/ia.types'

const props = defineProps<{
  isOpen: boolean
  columns: string[]
  rows: Record<string, any>[]
  totalRecords?: number
  sql?: string | null
  title?: string
  reportInfo?: IAReportInfo | null
  activeMes?: string | null
  activeMilitar?: ActiveMilitar | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const reportDownloadStore = useReportDownloadStore()
const dateStore = useDateStore()

const busqueda = ref('')
const copiado = ref(false)
const modalOverlayRef = ref<HTMLDivElement | null>(null)

// Formato de reporte seleccionado en la barra: 'consulta' | 'heatmap' | 'agil' | 'estadistica'
const formatoSeleccionado = ref<'consulta' | 'heatmap' | 'agil' | 'estadistica'>('consulta')
const isExportando = ref(false)
const exportandoTipo = ref<'excel' | 'pdf' | null>(null)

const formatoTituloActual = computed(() => {
  switch (formatoSeleccionado.value) {
    case 'heatmap': return 'Matriz Heatmap'
    case 'agil': return 'Parte Ágil'
    case 'estadistica': return 'Estadística de Totales'
    default: return 'Tabla de Consulta'
  }
})

const cerrar = () => {
  emit('close')
}

// Autoenfocar el overlay al abrir para permitir cerrar con tecla Escape y resetear vista
watch(() => props.isOpen, (open) => {
  if (open) {
    busqueda.value = ''
    copiado.value = false
    formatoSeleccionado.value = 'consulta'
    heatmapPage.value = 1
    nextTick(() => {
      modalOverlayRef.value?.focus()
    })
  }
})

// Protección reactiva: evitar que cualquier excepción imprevista desmonte el modal
onErrorCaptured((err, instance, info) => {
  console.warn('[QueryResultDetailModal] Error interceptado en render:', err, info)
  formatoSeleccionado.value = 'consulta'
  return false
})

// ---------------------------------------------------------------------------
// 1. Filtrado reactivo en tiempo real para la Tabla de Consulta
// ---------------------------------------------------------------------------
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

// ---------------------------------------------------------------------------
// 2. Detección Inteligente del Período Temporal (Soporte Monomes y Multimes)
// ---------------------------------------------------------------------------
interface DetectedMonthEntry {
  key: string // e.g. "2026-03"
  year: number
  monthNum: number
  monthName: string
  daysCount: number
  countRows: number
}

const getDaysInMonth = (monthName: string, year: number = 2026): number => {
  const m = monthName.toUpperCase()
  if (['ABRIL', 'JUNIO', 'SEPTIEMBRE', 'NOVIEMBRE'].includes(m)) return 30
  if (m === 'FEBRERO') return (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 29 : 28
  return 31
}

const MESES = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

// Extrae todos los meses presentes en el conjunto de datos de la consulta
const detectedMonthsList = computed<DetectedMonthEntry[]>(() => {
  const map = new Map<string, { year: number; monthNum: number; count: number }>()

  for (const row of props.rows) {
    const f = row.fecha_reporte || row.fecha || row.desde || row.primer_reporte
    if (f && typeof f === 'string' && f.includes('-')) {
      const parts = f.split('-')
      if (parts.length >= 2) {
        const y = parseInt(parts[0]) || 2026
        const m = parseInt(parts[1])
        if (!isNaN(m) && m >= 1 && m <= 12) {
          const key = `${y}-${String(m).padStart(2, '0')}`
          if (!map.has(key)) {
            map.set(key, { year: y, monthNum: m, count: 0 })
          }
          map.get(key)!.count++
        }
      }
    }
  }

  if (map.size === 0) {
    let fallbackName = props.activeMes || dateStore.mesSeleccionado || 'OCTUBRE'
    fallbackName = fallbackName.toUpperCase()
    const idx = MESES.indexOf(fallbackName)
    const mNum = idx >= 0 ? idx + 1 : 10
    const y = 2026
    const key = `${y}-${String(mNum).padStart(2, '0')}`
    return [{
      key,
      year: y,
      monthNum: mNum,
      monthName: fallbackName,
      daysCount: getDaysInMonth(fallbackName, y),
      countRows: props.rows.length
    }]
  }

  const sortedKeys = Array.from(map.keys()).sort()
  return sortedKeys.map(k => {
    const item = map.get(k)!
    const monthName = MESES[item.monthNum - 1]
    return {
      key: k,
      year: item.year,
      monthNum: item.monthNum,
      monthName,
      daysCount: getDaysInMonth(monthName, item.year),
      countRows: item.count
    }
  })
})

// Mes seleccionado para la previsualización del Heatmap día a día (1..31)
const selectedHeatmapMonthKey = ref<string>('')

watch(detectedMonthsList, (list) => {
  if (list && list.length > 0 && (!selectedHeatmapMonthKey.value || !list.some(m => m.key === selectedHeatmapMonthKey.value))) {
    selectedHeatmapMonthKey.value = list[0].key
  }
}, { immediate: true })

const activeHeatmapMonth = computed<DetectedMonthEntry>(() => {
  const list = detectedMonthsList.value
  if (!list || list.length === 0) {
    const fallbackName = (props.activeMes || dateStore.mesSeleccionado || 'OCTUBRE').toUpperCase()
    const idx = MESES.indexOf(fallbackName)
    const mNum = idx >= 0 ? idx + 1 : 10
    const y = 2026
    return {
      key: `${y}-${String(mNum).padStart(2, '0')}`,
      year: y,
      monthNum: mNum,
      monthName: fallbackName,
      daysCount: getDaysInMonth(fallbackName, y),
      countRows: props.rows?.length || 0
    }
  }
  const found = list.find(m => m.key === selectedHeatmapMonthKey.value)
  return found || list[0]
})

const detectedPeriodLabel = computed<string>(() => {
  const list = detectedMonthsList.value
  if (!list || list.length === 0) return 'Período Activo'
  if (list.length === 1) return `${list[0].monthName} ${list[0].year}`
  return `${list[0].monthName} ${list[0].year} - ${list[list.length - 1].monthName} ${list[list.length - 1].year} (${list.length} meses)`
})

const daysArray = computed<number[]>(() => {
  const count = activeHeatmapMonth.value?.daysCount || 31
  const safeCount = Math.max(1, Math.min(31, isNaN(count) ? 31 : count))
  return Array.from({ length: safeCount }, (_, i) => i + 1)
})

const detectedSingleMilitarCedula = computed(() => {
  if (!props.rows) return null
  const cedulas = new Set<string>()
  for (const row of props.rows) {
    if (!row) continue
    const c = row.cedula || row.identificacion
    if (c) cedulas.add(String(c).trim())
  }
  return cedulas.size === 1 ? Array.from(cedulas)[0] : null
})

// ---------------------------------------------------------------------------
// 3. Transformación de Datos para la Matriz Heatmap (por Mes Activo)
// ---------------------------------------------------------------------------
interface MilitarHeatmapRecord {
  cedula: string
  nombre: string
  totalDiasNovedad: number
  daysMap: Map<number, { novedad: string; descripcion?: string }>
}

const heatmapMilitares = computed<MilitarHeatmapRecord[]>(() => {
  if (!props.rows || props.rows.length === 0) return []

  const curY = activeHeatmapMonth.value?.year || 2026
  const curM = activeHeatmapMonth.value?.monthNum || 10
  const daysLimit = activeHeatmapMonth.value?.daysCount || 31
  const map = new Map<string, MilitarHeatmapRecord>()

  // 1. Inicializar todos los militares involucrados para asegurar su fila
  for (const row of props.rows) {
    if (!row) continue
    const ced = String(row.cedula || row.identificacion || '').trim()
    const nom = String(row.nombre || row.integrante || row.militar || '').trim()
    const finalCed = ced || (nom ? nom : '0000')
    const finalNom = nom || (ced ? `CC ${ced}` : 'INTEGRANTE')

    if (!map.has(finalCed)) {
      map.set(finalCed, {
        cedula: finalCed,
        nombre: finalNom,
        totalDiasNovedad: 0,
        daysMap: new Map()
      })
    }
  }

  // 2. Mapear días de novedades estrictamente del mes activo
  for (const row of props.rows) {
    if (!row) continue
    const ced = String(row.cedula || row.identificacion || '').trim()
    const nom = String(row.nombre || row.integrante || row.militar || '').trim()
    const finalCed = ced || (nom ? nom : '0000')

    const item = map.get(finalCed)
    if (!item) continue

    const nov = String(row.novedad || row.sub_novedad || 'NOVEDAD').trim().toUpperCase()
    const desc = row.descripcion ? String(row.descripcion) : undefined

    // Caso A: Reporte puntual por fecha
    const fStr = row.fecha_reporte || row.fecha
    if (fStr && typeof fStr === 'string' && fStr.includes('-')) {
      const parts = fStr.split('-')
      if (parts.length >= 3) {
        const y = parseInt(parts[0])
        const m = parseInt(parts[1])
        const d = parseInt(parts[2])
        if (y === curY && m === curM && !isNaN(d) && d >= 1 && d <= daysLimit) {
          if (!item.daysMap.has(d)) {
            item.daysMap.set(d, { novedad: nov, descripcion: desc })
            item.totalDiasNovedad++
          }
        }
      }
    } 
    // Caso B: Reporte consolidado por rango 'desde' y 'hasta'
    else if (row.desde && row.hasta) {
      try {
        const [y1, m1, d1] = String(row.desde).split('-').map(Number)
        const [y2, m2, d2] = String(row.hasta).split('-').map(Number)
        if (y1 === curY && m1 === curM && !isNaN(d1)) {
          const minD = Math.max(1, d1)
          const maxD = Math.min(daysLimit, (!isNaN(d2) && m2 === curM ? d2 : daysLimit))
          for (let d = minD; d <= maxD; d++) {
            if (!item.daysMap.has(d)) {
              item.daysMap.set(d, { novedad: nov, descripcion: desc })
              item.totalDiasNovedad++
            }
          }
        }
      } catch (e) {
        // Fallback silencioso
      }
    }
  }

  return Array.from(map.values())
})

const filteredHeatmapMilitares = computed(() => {
  if (!busqueda.value.trim()) return heatmapMilitares.value
  const term = busqueda.value.trim().toLowerCase()
  return heatmapMilitares.value.filter(m => {
    return m.nombre.toLowerCase().includes(term) || m.cedula.includes(term)
  })
})

// Paginación eficiente para la Matriz Heatmap (óptima para consultas con cientos de registros)
const heatmapPage = ref(1)
const heatmapPageSize = ref(50)

const totalHeatmapPages = computed(() => {
  const total = filteredHeatmapMilitares.value.length
  return Math.max(1, Math.ceil(total / heatmapPageSize.value))
})

const paginatedHeatmapMilitares = computed(() => {
  const list = filteredHeatmapMilitares.value
  if (list.length <= heatmapPageSize.value) return list
  const start = (heatmapPage.value - 1) * heatmapPageSize.value
  return list.slice(start, start + heatmapPageSize.value)
})

watch([busqueda, selectedHeatmapMonthKey], () => {
  heatmapPage.value = 1
})

const getHeatmapCellShortLabel = (cellData?: { novedad: string }) => {
  if (!cellData || !cellData.novedad) return 'D'
  const nov = String(cellData.novedad).toUpperCase()
  if (nov.includes('CDO') || nov.includes('COMANDO')) return 'CDO'
  if (nov.includes('PERMISO')) return 'PER'
  if (nov.includes('INCAPACIDAD') || nov.includes('EXCUSA')) return 'INC'
  if (nov.includes('VACACION')) return 'VAC'
  if (nov.includes('GUARDIA')) return 'GUA'
  if (nov.includes('RETIRADO')) return 'R'
  if (nov.includes('DISPONIBLE')) return 'D'
  return nov.slice(0, 3)
}

const getHeatmapCellBadgeClass = (cellData?: { novedad: string }) => {
  if (!cellData || !cellData.novedad) {
    return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
  }
  const nov = String(cellData.novedad).toUpperCase()
  if (nov.includes('CDO') || nov.includes('COMANDO')) {
    return 'bg-purple-500/40 text-purple-200 border border-purple-500/60'
  }
  if (nov.includes('PERMISO')) {
    return 'bg-blue-500/40 text-blue-200 border border-blue-500/60'
  }
  if (nov.includes('INCAPACIDAD') || nov.includes('EXCUSA') || nov.includes('MEDIC')) {
    return 'bg-amber-500/40 text-amber-200 border border-amber-500/60'
  }
  if (nov.includes('VACACION')) {
    return 'bg-cyan-500/40 text-cyan-200 border border-cyan-500/60'
  }
  if (nov.includes('RETIRADO')) {
    return 'bg-red-500/80 text-white border border-red-500'
  }
  return 'bg-slate-700 text-slate-200 border border-slate-600'
}

const getHeatmapCellTooltip = (militar: MilitarHeatmapRecord, day: number) => {
  if (!militar || !militar.daysMap) return ''
  const cellData = militar.daysMap.get(day)
  const dStr = String(day).padStart(2, '0')
  const y = activeHeatmapMonth.value?.year || 2026
  const m = String(activeHeatmapMonth.value?.monthNum || 10).padStart(2, '0')
  const fechaCompleta = `${y}-${m}-${dStr}`
  if (!cellData) {
    return `${militar.nombre} | ${fechaCompleta} : DISPONIBLE`
  }
  return `${militar.nombre} | ${fechaCompleta} : ${cellData.novedad} ${cellData.descripcion ? `(${cellData.descripcion})` : ''}`
}

// ---------------------------------------------------------------------------
// 4. Transformación de Datos para el Parte Ágil Ejecutivo (Rango Real de Fechas)
// ---------------------------------------------------------------------------
interface AgilMilitarSummary {
  cedula: string
  nombre: string
  totalDias: number
  ranges: { startDay: number; endDay: number; novedad: string; labelDays: string; daysCount: number }[]
}

const agilSummaryRows = computed<AgilMilitarSummary[]>(() => {
  const militaresMap = new Map<string, { cedula: string; nombre: string; dateEvents: { dateStr: string; novedad: string; desc?: string }[] }>()

  for (const row of props.rows) {
    const ced = String(row.cedula || row.identificacion || '0000').trim()
    const nom = String(row.nombre || row.integrante || 'INTEGRANTE').trim()
    const nov = String(row.novedad || row.sub_novedad || 'NOVEDAD').trim().toUpperCase()
    const desc = row.descripcion ? String(row.descripcion) : undefined

    if (!militaresMap.has(ced)) {
      militaresMap.set(ced, { cedula: ced, nombre: nom, dateEvents: [] })
    }

    const fStr = row.fecha_reporte || row.fecha
    if (fStr && typeof fStr === 'string' && fStr.includes('-')) {
      militaresMap.get(ced)!.dateEvents.push({ dateStr: fStr.trim(), novedad: nov, desc })
    } else if (row.desde && row.hasta) {
      militaresMap.get(ced)!.dateEvents.push({ dateStr: String(row.desde).trim(), novedad: nov, desc })
    }
  }

  const isConsecutiveDay = (d1Str: string, d2Str: string): boolean => {
    try {
      const dt1 = new Date(d1Str + 'T00:00:00')
      const dt2 = new Date(d2Str + 'T00:00:00')
      const diff = Math.round((dt2.getTime() - dt1.getTime()) / (1000 * 60 * 60 * 24))
      return diff === 1
    } catch {
      return false
    }
  }

  const formatRangeText = (d1Str: string, d2Str: string): string => {
    const MESES_ABR = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    try {
      const parts1 = d1Str.split('-').map(Number)
      const parts2 = d2Str.split('-').map(Number)
      const m1 = MESES_ABR[parts1[1] - 1] || ''
      const m2 = MESES_ABR[parts2[1] - 1] || ''
      const d1 = String(parts1[2]).padStart(2, '0')
      const d2 = String(parts2[2]).padStart(2, '0')

      if (d1Str === d2Str) {
        return `${d1} ${m1}`
      }
      if (parts1[0] === parts2[0] && parts1[1] === parts2[1]) {
        return `${d1}-${d2} ${m1}`
      }
      return `${d1} ${m1} - ${d2} ${m2}`
    } catch {
      return `${d1Str} a ${d2Str}`
    }
  }

  const result: AgilMilitarSummary[] = []

  for (const mData of militaresMap.values()) {
    const uniqueByDate = new Map<string, { dateStr: string; novedad: string; desc?: string }>()
    for (const ev of mData.dateEvents) {
      uniqueByDate.set(ev.dateStr, ev)
    }
    const sortedEvents = Array.from(uniqueByDate.values()).sort((a, b) => a.dateStr.localeCompare(b.dateStr))

    if (sortedEvents.length === 0) continue

    const ranges: { startDay: number; endDay: number; novedad: string; labelDays: string; daysCount: number }[] = []
    let currStartStr = sortedEvents[0].dateStr
    let currEndStr = sortedEvents[0].dateStr
    let currNov = sortedEvents[0].novedad
    let countInRange = 1

    for (let i = 1; i < sortedEvents.length; i++) {
      const ev = sortedEvents[i]
      if (ev.novedad === currNov && isConsecutiveDay(currEndStr, ev.dateStr)) {
        currEndStr = ev.dateStr
        countInRange++
      } else {
        ranges.push({
          startDay: 0,
          endDay: 0,
          novedad: currNov,
          labelDays: formatRangeText(currStartStr, currEndStr),
          daysCount: countInRange
        })
        currStartStr = ev.dateStr
        currEndStr = ev.dateStr
        currNov = ev.novedad
        countInRange = 1
      }
    }

    ranges.push({
      startDay: 0,
      endDay: 0,
      novedad: currNov,
      labelDays: formatRangeText(currStartStr, currEndStr),
      daysCount: countInRange
    })

    result.push({
      cedula: mData.cedula,
      nombre: mData.nombre,
      totalDias: sortedEvents.length,
      ranges
    })
  }

  return result
})

const filteredAgilSummaryRows = computed(() => {
  if (!busqueda.value.trim()) return agilSummaryRows.value
  const term = busqueda.value.trim().toLowerCase()
  return agilSummaryRows.value.filter(item => {
    return (
      item.nombre.toLowerCase().includes(term) ||
      item.cedula.includes(term) ||
      item.ranges.some(r => r.novedad.toLowerCase().includes(term))
    )
  })
})

const agilCategories = computed(() => {
  const map = new Map<string, { novedad: string; totalDias: number; militares: Set<string> }>()
  for (const item of agilSummaryRows.value) {
    for (const r of item.ranges) {
      if (!map.has(r.novedad)) {
        map.set(r.novedad, { novedad: r.novedad, totalDias: 0, militares: new Set() })
      }
      const cat = map.get(r.novedad)!
      cat.totalDias += r.daysCount
      cat.militares.add(item.nombre)
    }
  }
  return Array.from(map.values()).map(c => ({
    novedad: c.novedad,
    totalDias: c.totalDias,
    militares: Array.from(c.militares)
  }))
})

// ---------------------------------------------------------------------------
// 5. Transformación de Datos para Estadística de Totales
// ---------------------------------------------------------------------------
const estadisticasDistribucion = computed(() => {
  const map = new Map<string, { novedad: string; dias: number; militares: Set<string> }>()
  let totalDiasGeneral = 0

  for (const row of props.rows) {
    const nov = String(row.novedad || row.sub_novedad || 'NOVEDAD').trim().toUpperCase()
    const ced = String(row.cedula || row.identificacion || '').trim()
    const diasVal = parseInt(row.dias || row.total_dias || '1') || 1

    if (!map.has(nov)) {
      map.set(nov, { novedad: nov, dias: 0, militares: new Set() })
    }
    const cat = map.get(nov)!
    cat.dias += diasVal
    totalDiasGeneral += diasVal
    if (ced) cat.militares.add(ced)
  }

  return Array.from(map.values())
    .map(cat => ({
      novedad: cat.novedad,
      dias: cat.dias,
      militaresCount: cat.militares.size || 1,
      porcentaje: totalDiasGeneral > 0 ? ((cat.dias / totalDiasGeneral) * 100).toFixed(1) : '0'
    }))
    .sort((a, b) => b.dias - a.dias)
})

const filteredEstadisticasDistribucion = computed(() => {
  if (!busqueda.value.trim()) return estadisticasDistribucion.value
  const term = busqueda.value.trim().toLowerCase()
  return estadisticasDistribucion.value.filter(s => s.novedad.toLowerCase().includes(term))
})

const estadisticasGenerales = computed(() => {
  const list = estadisticasDistribucion.value
  const totalDias = list.reduce((acc, curr) => acc + curr.dias, 0)
  const totalCategorias = list.length
  const allMilitares = new Set<string>()

  for (const row of props.rows) {
    const c = row.cedula || row.identificacion
    if (c) allMilitares.add(String(c))
  }

  const top = list.length > 0 ? list[0] : null
  return {
    totalDias,
    totalCategorias,
    totalMilitares: allMilitares.size || (props.rows.length > 0 ? 1 : 0),
    novedadTop: top ? top.novedad : 'Sin registros',
    porcentajeTop: top ? top.porcentaje : '0'
  }
})

const getProgressGradientClass = (novedad: string) => {
  const n = novedad.toUpperCase()
  if (n.includes('VACACION')) return 'bg-gradient-to-r from-cyan-500 to-cyan-300'
  if (n.includes('PERMISO')) return 'bg-gradient-to-r from-blue-500 to-blue-300'
  if (n.includes('INCAPACIDAD') || n.includes('EXCUSA')) return 'bg-gradient-to-r from-amber-500 to-amber-300'
  if (n.includes('CDO') || n.includes('COMANDO')) return 'bg-gradient-to-r from-purple-500 to-purple-300'
  return 'bg-gradient-to-r from-emerald-500 to-teal-300'
}

// ---------------------------------------------------------------------------
// 6. Badges y Utilidades Visuales Compartidas
// ---------------------------------------------------------------------------
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
  if (n.includes('GUARDIA') || n.includes('SERVICIO') || n.includes('CDO') || n.includes('COMANDO')) {
    return 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
  }
  if (n.includes('DISPONIBLE')) {
    return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
  }
  return 'bg-slate-800 text-slate-300 border border-slate-700'
}

// Copiar tabla activa a portapapeles en formato TSV (compatible con Excel/Sheets)
const copiarTabla = async () => {
  try {
    let fullText = ''

    if (formatoSeleccionado.value === 'consulta') {
      const headers = props.columns.join('\t')
      const rowsText = props.rows.map(r => {
        return props.columns.map(c => r[c] !== null && r[c] !== undefined ? String(r[c]) : '').join('\t')
      }).join('\n')
      fullText = `${headers}\n${rowsText}`
    } else if (formatoSeleccionado.value === 'agil') {
      const headers = ['CEDULA', 'NOMBRE', 'RANGOS_NOVEDADES', 'TOTAL_DIAS'].join('\t')
      const rowsText = agilSummaryRows.value.map(item => {
        const rangesStr = item.ranges.map(r => `${r.labelDays} (${r.novedad})`).join('; ')
        return [item.cedula, item.nombre, rangesStr, item.totalDias].join('\t')
      }).join('\n')
      fullText = `${headers}\n${rowsText}`
    } else if (formatoSeleccionado.value === 'estadistica') {
      const headers = ['NOVEDAD', 'DIAS', 'EFECTIVOS', 'PORCENTAJE'].join('\t')
      const rowsText = estadisticasDistribucion.value.map(s => {
        return [s.novedad, s.dias, s.militaresCount, `${s.porcentaje}%`].join('\t')
      }).join('\n')
      fullText = `${headers}\n${rowsText}`
    } else if (formatoSeleccionado.value === 'heatmap') {
      const headers = ['CEDULA', 'NOMBRE', 'TOTAL_NOVEDADES', ...daysArray.value.map(d => `D${d}`)].join('\t')
      const rowsText = heatmapMilitares.value.map(m => {
        const daysValues = daysArray.value.map(d => getHeatmapCellShortLabel(m.daysMap.get(d)))
        return [m.cedula, m.nombre, m.totalDiasNovedad, ...daysValues].join('\t')
      }).join('\n')
      fullText = `${headers}\n${rowsText}`
    }

    await navigator.clipboard.writeText(fullText)
    copiado.value = true
    setTimeout(() => {
      copiado.value = false
    }, 2500)
  } catch (err) {
    console.error('Error al copiar al portapapeles:', err)
  }
}

// ---------------------------------------------------------------------------
// 7. Descarga de Reportes en Excel (.xlsx) y PDF (.pdf) con tipos de formato
// ---------------------------------------------------------------------------
const descargarFormato = async (tipo: 'excel' | 'pdf') => {
  if (isExportando.value) return

  const periodoConsulta = detectedPeriodLabel.value
  const mesHeatmap = activeHeatmapMonth.value.monthName
  const cedulaMilitar = props.activeMilitar?.cedula || detectedSingleMilitarCedula.value

  // Caso 1: Descargar Tabla Actual de la Consulta
  if (formatoSeleccionado.value === 'consulta') {
    try {
      isExportando.value = true
      exportandoTipo.value = tipo

      const blob = await iaService.exportarTabla({
        titulo: props.title || 'Reporte de Consulta de Personal',
        columns: props.columns,
        rows: filteredRows.value,
        formato: tipo,
        mes: periodoConsulta,
        subtitulo: `Período: ${periodoConsulta}`
      })

      // Disparar descarga en el navegador
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      const extension = tipo === 'excel' ? 'xlsx' : 'pdf'
      a.download = `Reporte_Consulta_BIMEJ12_${new Date().toISOString().slice(0, 10)}.${extension}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Error al exportar tabla de consulta:', err)
      alert(`No se pudo generar el reporte en ${tipo.toUpperCase()}. Por favor intente nuevamente.`)
    } finally {
      isExportando.value = false
      exportandoTipo.value = null
    }
    return
  }

  // Casos 2, 3 y 4: Matriz Heatmap, Parte Ágil, Estadística de Totales Oficiales
  let url = ''
  let tituloReporte = ''

  if (formatoSeleccionado.value === 'heatmap') {
    tituloReporte = `Matriz Heatmap - ${mesHeatmap}`
    if (cedulaMilitar) {
      url = `/api/exportar/${tipo}?tipo=consolidado_mensual&cedula=${cedulaMilitar}&mes=${mesHeatmap}&modo=letras`
    } else {
      url = `/api/exportar/${tipo}?tipo=consolidado_mensual&mes=${mesHeatmap}&modo=letras`
    }
  } else if (formatoSeleccionado.value === 'agil') {
    tituloReporte = `Parte Ágil de Novedades - ${mesHeatmap}`
    if (cedulaMilitar) {
      url = `/api/exportar/${tipo}?tipo=agil&cedula=${cedulaMilitar}&mes=${mesHeatmap}`
    } else {
      url = `/api/exportar/${tipo}?tipo=agil&mes=${mesHeatmap}`
    }
  } else if (formatoSeleccionado.value === 'estadistica') {
    tituloReporte = `Estadística de Novedades - ${mesHeatmap}`
    if (cedulaMilitar) {
      url = `/api/exportar/${tipo}?tipo=personal&cedula=${cedulaMilitar}&mes=${mesHeatmap}`
    } else {
      url = `/api/exportar/${tipo}?tipo=consolidado_mensual&mes=${mesHeatmap}&modo=numeros`
    }
  }

  if (url) {
    reportDownloadStore.downloadReport(url, tituloReporte, tipo)
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
