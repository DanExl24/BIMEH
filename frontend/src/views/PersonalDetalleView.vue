<template>
  <div class="space-y-6">
    <!-- Back Button -->
    <div>
      <router-link 
        to="/personal" 
        class="text-xs text-slate-400 font-semibold hover:text-cyan-400 flex items-center gap-1.5 transition-colors"
      >
        &larr; Volver al Buscador
      </router-link>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 space-y-4">
      <div class="w-10 h-10 border-4 border-cyan-500/25 border-t-cyan-500 rounded-full animate-spin"></div>
      <p class="text-slate-400 text-sm">Cargando expediente personal...</p>
    </div>

    <!-- Profile content -->
    <div v-else-if="profile" class="space-y-6">
      
      <!-- 1. Header Info Card -->
      <div class="glass-panel p-6 rounded-3xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div class="flex items-start gap-4">
          <!-- Profile Icon / Badge -->
          <div class="w-16 h-16 bg-cyan-500/10 border border-cyan-500/25 rounded-2xl flex items-center justify-center text-cyan-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-3 flex-wrap">
              <h2 class="text-lg font-bold text-slate-100 uppercase tracking-tight">{{ profile.nombre }}</h2>
              <span 
                class="text-[9px] font-extrabold tracking-wider px-2.5 py-0.5 rounded border uppercase"
                :class="profile.estado === 'ACTIVO' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'"
              >
                {{ profile.estado }}
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-1 font-mono">
              Cédula de Ciudadanía: <span class="text-slate-200 font-bold">{{ profile.cedula }}</span>
            </p>
            <p v-if="profile.fecha_retiro" class="text-xs text-red-400 mt-1 font-mono font-semibold">
              Fecha de Retiro: {{ profile.fecha_retiro }}
            </p>
          </div>
        </div>

        <!-- Export Button (Trigger Modal) -->
        <div class="flex items-center gap-3 self-stretch md:self-auto justify-end">
          <button 
            @click="triggerExportModal('personal')"
            class="px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 rounded-xl text-xs font-bold text-slate-100 flex items-center gap-2 transition-all shadow-md active:scale-95 cursor-pointer select-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3M3 17V7a2 2 0 012-2h6l2 2h7a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
            </svg>
            Generar Reporte
          </button>
        </div>
      </div>

      <!-- 2. Statistics Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Tarjeta Tiempo Disponible -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">📈 Tasa Disponibilidad</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-cyan-400">{{ profile.tiempo_disponible_pct }}%</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Porcentaje de días en servicio disponible</p>
        </div>

        <!-- Tarjeta Tiempo en Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">🏥 Tasa Novedades</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-amber-500">{{ profile.tiempo_novedades_pct }}%</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Porcentaje de días fuera de servicio</p>
        </div>

        <!-- Tarjeta Total Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">📝 Novedades Registradas</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-slate-200">{{ profile.total_novedades }}</span>
            <span class="text-xs text-slate-400">días</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Días totales reportados con novedad</p>
        </div>

        <!-- Promedio Duración Novedades -->
        <div class="glass-panel p-5 rounded-2xl flex flex-col justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">⏱️ Duración Promedio</span>
          <div class="mt-2 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold text-slate-200">{{ profile.promedio_duracion_novedades }}</span>
            <span class="text-xs text-slate-400">días consecutivos</span>
          </div>
          <p class="text-[10px] text-slate-500 mt-2 block">Promedio de duración por evento de novedad</p>
        </div>
      </div>

      <!-- 3. Chart and Details -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Tiempo acumulado subnovedad chart -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col h-[400px]">
          <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
            <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Distribución de Novedades (Días)
          </h3>
          <div class="flex-1 min-h-0">
            <div ref="acumuladoChartDom" class="chart-container"></div>
          </div>
        </div>

        <!-- Línea de tiempo individual -->
        <div class="glass-panel p-6 rounded-2xl lg:col-span-2 flex flex-col h-[400px]">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4 border-b border-darkBorder/40 pb-3">
            <h3 class="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <span class="w-2 h-4 bg-teal-500 rounded-sm"></span> Línea de Tiempo de Novedades e Historial
            </h3>
            <!-- Selectores de Filtro -->
            <div class="flex items-center gap-2">
              <select 
                v-model="filtroSubnovedad"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1 text-[11px] text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todas las Novedades</option>
                <option v-for="s in subnovedadesList" :key="s" :value="s">{{ s }}</option>
              </select>
              <select 
                v-model="filtroMes"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1 text-[11px] text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todos los Meses</option>
                <option value="01">Enero</option>
                <option value="02">Febrero</option>
                <option value="03">Marzo</option>
                <option value="04">Abril</option>
                <option value="05">Mayo</option>
                <option value="06">Junio</option>
                <option value="07">Julio</option>
              </select>
              <select 
                v-model="filtroDia"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1 text-[11px] text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todos los Días</option>
                <option v-for="d in diasDelMes" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
          </div>
          
          <div class="flex-1 overflow-y-auto pr-2 space-y-4">
            <div v-if="filteredHistorial.length === 0" class="text-center py-20 text-slate-500 text-xs">
              No se encontraron registros para los filtros seleccionados.
            </div>
            <div 
              v-else
              v-for="h in filteredHistorial" 
              :key="h.fecha"
              class="relative pl-6 border-l-2 border-darkBorder hover:border-cyan-500/30 transition-colors pb-4 last:pb-0"
            >
              <!-- Timeline node -->
              <div 
                class="absolute -left-[6px] top-1.5 w-2.5 h-2.5 rounded-full border border-darkBg"
                :class="isAvailable(h.subnovedad) ? 'bg-emerald-500' : 'bg-amber-500'"
              ></div>

              <div class="flex items-center justify-between">
                <span class="text-[11px] font-bold font-mono text-cyan-400 bg-cyan-500/5 border border-cyan-500/10 px-2 py-0.5 rounded">
                  {{ h.fecha }}
                </span>
                <span 
                  class="text-[9px] font-bold px-2 py-0.5 rounded border uppercase"
                  :class="isAvailable(h.subnovedad) ? 'bg-emerald-500/10 border-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 border-amber-500/10 text-amber-500'"
                >
                  {{ h.subnovedad }}
                </span>
              </div>
              <div class="mt-1.5 space-y-1">
                <p class="text-xs text-slate-300 font-semibold uppercase">{{ h.descripcion || 'Sin descripción oficial' }}</p>
                <p v-if="h.desde || h.hasta" class="text-[10px] text-slate-500 font-mono">
                  Rango novedad: {{ h.desde || 'N/A' }} al {{ h.hasta || 'N/A' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. Individual Heatmap and Daily Detail Card -->
      <div class="glass-panel p-6 rounded-2xl space-y-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-darkBorder/40 pb-4">
          <div>
            <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
              <span class="w-2.5 h-4 bg-cyan-500 rounded-sm"></span> Mi Historial Operacional y Mapa de Calor
            </h3>
            <p class="text-xs text-slate-500 mt-1 font-sans">Hoja de ruta y disponibilidad diaria (D = Disponible, N = Novedad, R = Retirado, - = Sin registro).</p>
          </div>

          <!-- Tabs -->
          <div class="flex bg-darkBg/60 p-1.5 rounded-xl border border-darkBorder/40 self-start sm:self-auto">
            <button 
              @click="activeHeatmapTab = 'mensual'"
              class="px-3 py-1.5 text-[10px] font-bold uppercase rounded-lg transition-all"
              :class="activeHeatmapTab === 'mensual' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
            >
              Vista Mensual
            </button>
            <button 
              @click="activeHeatmapTab = 'anual'"
              class="px-3 py-1.5 text-[10px] font-bold uppercase rounded-lg transition-all"
              :class="activeHeatmapTab === 'anual' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
            >
              Vista Anual
            </button>
            <button 
              @click="activeHeatmapTab = 'diario'"
              class="px-3 py-1.5 text-[10px] font-bold uppercase rounded-lg transition-all"
              :class="activeHeatmapTab === 'diario' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/20' : 'text-slate-400 hover:text-slate-200'"
            >
              Reporte Detallado
            </button>
          </div>
        </div>

        <!-- Content: Vista Mensual -->
        <div v-if="activeHeatmapTab === 'mensual'" class="space-y-6">
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-darkBg/30 p-4 rounded-xl border border-darkBorder/20">
            <div class="flex items-center gap-2">
              <label class="text-[10px] uppercase font-bold text-slate-400 font-sans">Seleccionar Mes:</label>
              <select 
                v-model="selectedMonthlyHeatmapMonth"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1 text-xs text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>

            <!-- Trigger Modal for Monthly Heatmap -->
            <button 
              @click="triggerExportModal('consolidado_mensual', selectedMonthlyHeatmapMonth)"
              class="px-3.5 py-1.5 bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/20 hover:border-cyan-500/40 rounded-xl text-[10px] font-bold text-cyan-400 flex items-center gap-1.5 transition-all cursor-pointer select-none active:scale-95"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Exportar Heatmap ({{ selectedMonthlyHeatmapMonth }})
            </button>
          </div>

          <div class="bg-darkCard p-4 rounded-xl border border-darkBorder/40 overflow-x-auto">
            <div class="flex items-center gap-1.5 min-w-[700px] font-mono text-center pb-2">
              <div v-for="d in 31" :key="d" class="flex-1">
                <span class="text-[9px] text-slate-500 uppercase block mb-1.5 font-sans">D{{ d }}</span>
                <div 
                  class="w-8 h-8 mx-auto rounded transition-colors flex items-center justify-center text-[10px] font-bold"
                  :class="getIndividualHeatmapCellClass(selectedMonthlyHeatmapMonth, d)"
                  :title="getIndividualHeatmapCellTitle(selectedMonthlyHeatmapMonth, d)"
                >
                  {{ getIndividualHeatmapCellLetter(selectedMonthlyHeatmapMonth, d) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Content: Vista Anual -->
        <div v-else-if="activeHeatmapTab === 'anual'" class="bg-darkCard p-5 rounded-xl border border-darkBorder/40 overflow-x-auto">
          <div class="space-y-3 min-w-[850px]">
            <!-- Header row for days -->
            <div class="flex items-center gap-1.5 font-mono text-[9px] text-slate-500 pl-24">
              <div v-for="d in 31" :key="d" class="w-6.5 text-center font-bold">D{{ d }}</div>
            </div>
            
            <!-- Rows for months -->
            <div v-for="m in activeMonths" :key="m" class="flex items-center gap-1.5 font-mono">
              <!-- Month Name Label -->
              <div class="w-24 text-[10px] font-bold text-slate-400 uppercase tracking-wider text-right pr-3">{{ m }}</div>
              <!-- Days cells -->
              <div 
                v-for="d in 31" 
                :key="d"
                class="w-6.5 h-6.5 rounded transition-colors flex items-center justify-center text-[9px] font-bold"
                :class="getIndividualHeatmapCellClass(m, d)"
                :title="`${m} ${d}: ${getStatusForDate(m, d)}`"
              >
                {{ getIndividualHeatmapCellLetter(m, d) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Content: Reporte Detallado (Tabla) -->
      <div v-else-if="activeHeatmapTab === 'diario'" class="space-y-4 font-sans">
          <!-- Filters Row -->
          <div class="flex flex-col md:flex-row gap-4 bg-darkBg/30 p-4 rounded-xl border border-darkBorder/20">
            <!-- Text Search -->
            <div class="flex-1 relative">
              <input 
                type="text" 
                v-model="tableSearchQuery" 
                placeholder="Filtrar por descripción o subnovedad..."
                class="w-full bg-darkBg border border-darkBorder rounded-lg pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-500/50 transition-colors"
              />
              <div class="absolute left-3 top-2.5 text-slate-500">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>

            <!-- Subnovedad Selector -->
            <div class="flex items-center gap-2">
              <label class="text-[10px] uppercase font-bold text-slate-400 font-sans">Subnovedad:</label>
              <select 
                v-model="tableSubnovedadFilter"
                class="bg-darkBg border border-darkBorder rounded-lg px-2.5 py-1.5 text-xs text-slate-300 outline-none focus:border-cyan-500/50"
              >
                <option value="">Todas</option>
                <option v-for="s in subnovedadesList" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>

          <!-- Table Container -->
          <div class="bg-darkCard rounded-xl border border-darkBorder/40 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b border-darkBorder text-[10px] text-slate-400 uppercase font-mono bg-darkBg/30">
                    <th class="py-3 px-4 font-semibold">Fecha</th>
                    <th class="py-3 px-4 font-semibold text-center">Estado</th>
                    <th class="py-3 px-4 font-semibold">Subnovedad</th>
                    <th class="py-3 px-4 font-semibold">Descripción / Justificación</th>
                    <th class="py-3 px-4 font-semibold">Desde</th>
                    <th class="py-3 px-4 font-semibold">Hasta</th>
                  </tr>
                </thead>
                <tbody class="text-xs">
                  <tr 
                    v-for="row in tablePaginatedHistory" 
                    :key="row.fecha"
                    class="border-b border-darkBorder/20 hover:bg-darkBorder/5 transition-colors"
                  >
                    <!-- Date -->
                    <td class="py-2.5 px-4 font-mono font-bold text-cyan-400">{{ row.fecha }}</td>
                    
                    <!-- Estado Badge -->
                    <td class="py-2.5 px-4 text-center">
                      <span 
                        class="text-[9px] font-bold px-2 py-0.5 rounded border uppercase inline-block"
                        :class="isAvailable(row.subnovedad) ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400' : 'bg-amber-500/10 border-amber-500/25 text-amber-500'"
                      >
                        {{ isAvailable(row.subnovedad) ? 'DISP' : 'NOVEDAD' }}
                      </span>
                    </td>
                    
                    <!-- Subnovedad -->
                    <td class="py-2.5 px-4 font-bold text-slate-300 uppercase">{{ row.subnovedad }}</td>
                    
                    <!-- Descripción -->
                    <td class="py-2.5 px-4 text-slate-400 uppercase max-w-xs truncate" :title="row.descripcion || undefined">
                      {{ row.descripcion || 'Sin justificación registrada' }}
                    </td>
                    
                    <!-- Desde -->
                    <td class="py-2.5 px-4 font-mono text-slate-500">{{ row.desde || '-' }}</td>
                    
                    <!-- Hasta -->
                    <td class="py-2.5 px-4 font-mono text-slate-500">{{ row.hasta || '-' }}</td>
                  </tr>
                  
                  <!-- Empty state -->
                  <tr v-if="tableFilteredHistory.length === 0">
                    <td colspan="6" class="text-center py-12 text-slate-500">
                      No se encontraron registros para los filtros ingresados.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Table Pagination Controls -->
            <div v-if="tableFilteredHistory.length > 0" class="flex justify-between items-center text-xs p-3 bg-darkBg/20 border-t border-darkBorder/20">
              <span class="text-slate-500 font-mono">
                Mostrando {{ (tablePage - 1) * 10 + 1 }} - {{ Math.min(tablePage * 10, tableFilteredHistory.length) }} de {{ tableFilteredHistory.length }} registros
              </span>
              <div class="flex items-center gap-2">
                <button 
                  @click="tablePage--" 
                  :disabled="tablePage <= 1"
                  class="px-2.5 py-1 bg-darkCard border border-darkBorder rounded-lg text-slate-400 hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none"
                >
                  Anterior
                </button>
                <span class="font-bold text-slate-200">Pág. {{ tablePage }} / {{ tableMaxPage }}</span>
                <button 
                  @click="tablePage++" 
                  :disabled="tablePage >= tableMaxPage"
                  class="px-2.5 py-1 bg-darkCard border border-darkBorder rounded-lg text-slate-400 hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none"
                >
                  Siguiente
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Export Modal -->
  <div v-if="openExportModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
    <div class="glass-panel max-w-md w-full p-6 rounded-3xl space-y-6 shadow-2xl border border-darkBorder font-sans">
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-darkBorder/40 pb-3">
        <h3 class="text-sm font-bold text-slate-200 uppercase tracking-wide flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2a2 2 0 00-2-2H5a2 2 0 00-2 2v2a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v8m-5 0h7M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          Generar Reporte del Integrante
        </h3>
        <button @click="openExportModal = false" class="text-slate-400 hover:text-slate-200 text-lg cursor-pointer">&times;</button>
      </div>

      <!-- Form fields -->
      <div class="space-y-4">
        <!-- Formato selector -->
        <div class="space-y-1.5">
          <label class="text-[10px] uppercase font-bold text-slate-400">Formato de Exportación:</label>
          <div class="grid grid-cols-3 gap-2">
            <button 
              @click="modalFormat = 'excel'"
              class="px-3 py-2 text-xs font-bold rounded-xl transition-all border cursor-pointer"
              :class="modalFormat === 'excel' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-darkBg border-darkBorder text-slate-400 hover:text-slate-200'"
            >
              EXCEL
            </button>
            <button 
              @click="modalFormat = 'csv'"
              class="px-3 py-2 text-xs font-bold rounded-xl transition-all border cursor-pointer"
              :class="modalFormat === 'csv' ? 'bg-slate-500/10 border-slate-500/30 text-slate-300' : 'bg-darkBg border-darkBorder text-slate-400 hover:text-slate-200'"
            >
              CSV
            </button>
            <button 
              @click="modalFormat = 'pdf'"
              class="px-3 py-2 text-xs font-bold rounded-xl transition-all border cursor-pointer"
              :class="modalFormat === 'pdf' ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400' : 'bg-darkBg border-darkBorder text-slate-400 hover:text-slate-200'"
            >
              PDF
            </button>
          </div>
        </div>

        <!-- Tipo / Rango selector -->
        <div class="space-y-1.5">
          <label class="text-[10px] uppercase font-bold text-slate-400">Tipo de Reporte / Rango:</label>
          <select 
            v-model="modalReportType"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
          >
            <option value="personal">Historial Completo (Listado)</option>
            <option value="consolidado_mensual">Heatmap Mensual (Matriz)</option>
          </select>
        </div>

        <!-- Mes selector (Conditional) -->
        <div v-if="modalReportType === 'consolidado_mensual' || modalReportType === 'personal'" class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-[10px] uppercase font-bold text-slate-400">Mes del Reporte:</label>
            <span v-if="modalReportType === 'personal'" class="text-[8px] text-slate-500 uppercase font-bold">(Opcional)</span>
          </div>
          <select 
            v-model="modalMonth"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
          >
            <option v-if="modalReportType === 'personal'" value="">Todos los Meses</option>
            <option v-for="m in activeMonths" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Subnovedad selector (Opcional) -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-[10px] uppercase font-bold text-slate-400">Filtrar por Subnovedad:</label>
            <span class="text-[8px] text-slate-500 uppercase font-bold">(Opcional)</span>
          </div>
          <select 
            v-model="modalSubnovedad"
            class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs text-slate-200 outline-none focus:border-cyan-500/50"
          >
            <option value="">Todas las Subnovedades</option>
            <option v-for="s in subnovedadesList" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-3 pt-3 border-t border-darkBorder/40">
        <button 
          @click="openExportModal = false"
          class="flex-1 px-4 py-2 border border-darkBorder hover:bg-darkBg/50 rounded-xl text-xs font-bold text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
        >
          Cancelar
        </button>
        <a 
          :href="downloadUrl"
          download
          @click="openExportModal = false"
          class="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 rounded-xl text-xs font-bold text-slate-100 text-center transition-all cursor-pointer shadow-md select-none"
        >
          Descargar
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '../stores/appStore'
import * as echarts from 'echarts'
import { fetchPersonalDetalle, fetchPersonalHistorial, fetchPersonalAcumulado } from '../services/api'
import type { PersonalDetalle, HistorialRegistro } from '../types'

const route = useRoute()
const appStore = useAppStore()

const loading = ref(true)
const profile = ref<PersonalDetalle | null>(null)
const historial = ref<HistorialRegistro[]>([])

const acumuladoChartDom = ref<HTMLDivElement | null>(null)
let acumuladoChart: echarts.ECharts | null = null

// Filtros de fecha y novedad individuales
const filtroMes = ref('')
const filtroDia = ref('')
const filtroSubnovedad = ref('')

// Heatmap individual variables
const activeHeatmapTab = ref<'mensual' | 'anual' | 'diario'>('mensual')
const selectedMonthlyHeatmapMonth = ref('JULIO')

const activeMonths = computed(() => {
  if (!profile.value || !profile.value.fecha_retiro) {
    return appStore.months
  }
  try {
    const parts = profile.value.fecha_retiro.split('-')
    const retirementMonthNum = parseInt(parts[1], 10)
    const monthList = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
    return monthList.slice(0, retirementMonthNum)
  } catch (e) {
    console.error("Error computing active months:", e)
    return appStore.months
  }
})
const tableSearchQuery = ref('')
const tableSubnovedadFilter = ref('')
const tablePage = ref(1)

const diasDelMes = Array.from({ length: 31 }, (_, i) => String(i + 1).padStart(2, '0'))

// Get unique subnovedades registered by this member
const subnovedadesList = computed(() => {
  const set = new Set<string>()
  historial.value.forEach(h => {
    if (h.subnovedad) {
      set.add(h.subnovedad)
    }
  })
  return Array.from(set).sort()
})

const filteredHistorial = computed(() => {
  return historial.value.filter(h => {
    const parts = h.fecha.split('-')
    const month = parts[1]
    const day = parts[2]
    
    const matchMonth = !filtroMes.value || month === filtroMes.value
    const matchDay = !filtroDia.value || day === filtroDia.value
    const matchSubnovedad = !filtroSubnovedad.value || h.subnovedad === filtroSubnovedad.value
    
    return matchMonth && matchDay && matchSubnovedad
  })
})

const DISPONIBLE_STATUSES = ["CDO UNIDAD", "AREA OPERACIONES"]
const isAvailable = (subnovedad: string) => {
  return DISPONIBLE_STATUSES.includes(subnovedad)
}

const loadProfile = async () => {
  loading.value = true
  const cedula = Number(route.params.cedula)
  try {
    profile.value = await fetchPersonalDetalle(cedula)
    historial.value = await fetchPersonalHistorial(cedula)
    loading.value = false
    
    setTimeout(() => {
      initAcumuladoChart()
    }, 50)
  } catch (error) {
    console.error('Error fetching profile:', error)
    loading.value = false
  }
}

const initAcumuladoChart = async () => {
  if (!acumuladoChartDom.value || !profile.value) return
  
  if (acumuladoChart) {
    acumuladoChart.dispose()
  }
  
  acumuladoChart = echarts.init(acumuladoChartDom.value)
  
  try {
    const data = await fetchPersonalAcumulado(profile.value.cedula)
    
    const chartData = data.map((d: any) => ({
      name: d.subnovedad,
      value: d.dias
    }))
    
    acumuladoChart.setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' },
        formatter: '{b}: <b>{c} días</b> ({d}%)'
      },
      series: [
        {
          type: 'pie',
          radius: '65%',
          center: ['50%', '50%'],
          roseType: 'area', // Premium look
          itemStyle: {
            borderRadius: 5,
            borderColor: '#151d30',
            borderWidth: 1.5
          },
          data: chartData,
          color: ['#06b6d4', '#f59e0b', '#10b981', '#ef4444', '#6366f1', '#a855f7'],
          label: {
            color: '#94a3b8',
            fontSize: 10,
            formatter: '{b}'
          }
        }
      ]
    })

    // Add click handler to filter by clicked subnovedad
    acumuladoChart.on('click', (params: any) => {
      if (params.name) {
        filtroSubnovedad.value = params.name
      }
    })
  } catch (error) {
    console.error('Error generating accumulated chart:', error)
  }
}

const handleResize = () => {
  acumuladoChart?.resize()
}

onMounted(() => {
  loadProfile()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  acumuladoChart?.dispose()
})

// Individual Heatmap Calculations
const MONTH_MAP: Record<string, string> = {
  'ENERO': '01', 'FEBRERO': '02', 'MARZO': '03', 'ABRIL': '04', 
  'MAYO': '05', 'JUNIO': '06', 'JULIO': '07', 'AGOSTO': '08', 
  'SEPTIEMBRE': '09', 'OCTUBRE': '10', 'NOVIEMBRE': '11', 'DICIEMBRE': '12'
}
const isRetiredForDate = (monthName: string, dayNum: number) => {
  if (!profile.value || !profile.value.fecha_retiro) return false
  const mm = MONTH_MAP[monthName]
  if (!mm) return false
  const dd = String(dayNum).padStart(2, '0')
  const targetDate = `2026-${mm}-${dd}`
  return targetDate >= profile.value.fecha_retiro
}

const getStatusForDate = (monthName: string, dayNum: number) => {
  if (isRetiredForDate(monthName, dayNum)) return 'RETIRADO'
  const mm = MONTH_MAP[monthName]
  if (!mm) return 'N/A'
  const dd = String(dayNum).padStart(2, '0')
  const targetDate = `2026-${mm}-${dd}`
  const found = historial.value.find(h => h.fecha === targetDate)
  return found ? found.subnovedad : 'N/A'
}

const getIndividualHeatmapCellClass = (monthName: string, dayNum: number) => {
  const est = getStatusForDate(monthName, dayNum)
  if (est === 'RETIRADO') return 'bg-red-500/80 shadow shadow-red-500/10 text-red-100'
  if (est === 'N/A') return 'bg-darkBg border border-darkBorder/40 text-slate-600'
  return isAvailable(est) 
    ? 'bg-emerald-500/80 shadow shadow-emerald-500/10 text-emerald-100' 
    : 'bg-amber-500/80 shadow shadow-amber-500/10 text-amber-100'
}

const getIndividualHeatmapCellLetter = (monthName: string, dayNum: number) => {
  const est = getStatusForDate(monthName, dayNum)
  if (est === 'RETIRADO') return 'R'
  if (est === 'N/A') return '-'
  return isAvailable(est) ? 'D' : 'N'
}

const getIndividualHeatmapCellTitle = (monthName: string, dayNum: number) => {
  const est = getStatusForDate(monthName, dayNum)
  return `Día ${dayNum} de ${monthName}: ${est}`
}

const tableFilteredHistory = computed(() => {
  return historial.value.filter(h => {
    const matchSearch = !tableSearchQuery.value || 
      (h.descripcion && h.descripcion.toLowerCase().includes(tableSearchQuery.value.toLowerCase())) ||
      (h.subnovedad && h.subnovedad.toLowerCase().includes(tableSearchQuery.value.toLowerCase()))
      
    const matchSubnovedad = !tableSubnovedadFilter.value || h.subnovedad === tableSubnovedadFilter.value
    
    return matchSearch && matchSubnovedad
  })
})

const tableMaxPage = computed(() => {
  return Math.ceil(tableFilteredHistory.value.length / 10) || 1
})

const tablePaginatedHistory = computed(() => {
  const start = (tablePage.value - 1) * 10
  return tableFilteredHistory.value.slice(start, start + 10)
})

watch([tableSearchQuery, tableSubnovedadFilter], () => {
  tablePage.value = 1
})

// Modal state variables and logic
const openExportModal = ref(false)
const modalFormat = ref<'excel' | 'csv' | 'pdf'>('excel')
const modalReportType = ref<'personal' | 'consolidado_mensual'>('personal')
const modalMonth = ref('JULIO')
const modalSubnovedad = ref('')

const triggerExportModal = (tipo: 'personal' | 'consolidado_mensual', defaultMonth?: string) => {
  modalReportType.value = tipo
  if (defaultMonth) {
    modalMonth.value = defaultMonth
  }
  openExportModal.value = true
}

const downloadUrl = computed(() => {
  const format = modalFormat.value
  const tipo = modalReportType.value
  const cedula = profile.value ? profile.value.cedula : ''
  
  let url = `${appStore.apiBase}/api/exportar/${format}?tipo=${tipo}&cedula=${cedula}`
  
  if (tipo === 'consolidado_mensual') {
    url += `&mes=${modalMonth.value}`
  } else if (tipo === 'personal' && modalMonth.value) {
    url += `&mes=${modalMonth.value}`
  }
  
  if (modalSubnovedad.value) {
    url += `&subnovedad=${encodeURIComponent(modalSubnovedad.value)}`
  }
  
  return url
})

watch(activeMonths, (newMonths) => {
  if (newMonths && newMonths.length > 0) {
    if (!newMonths.includes(selectedMonthlyHeatmapMonth.value)) {
      selectedMonthlyHeatmapMonth.value = newMonths[newMonths.length - 1]
    }
    if (modalMonth.value && !newMonths.includes(modalMonth.value)) {
      modalMonth.value = newMonths[newMonths.length - 1]
    }
  }
}, { immediate: true })

watch(modalReportType, (newType) => {
  if (newType === 'consolidado_mensual' && !modalMonth.value) {
    if (activeMonths.value && activeMonths.value.length > 0) {
      modalMonth.value = activeMonths.value[activeMonths.value.length - 1]
    } else {
      modalMonth.value = 'JULIO'
    }
  }
})
</script>
