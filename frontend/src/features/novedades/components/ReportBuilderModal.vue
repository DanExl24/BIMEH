<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 overflow-y-auto bg-slate-950/80 backdrop-blur-md transition-opacity duration-200"
    @click.self="cerrarModal"
  >
    <div 
      class="glass-panel w-full max-w-5xl rounded-3xl border border-darkBorder/90 bg-slate-900/95 shadow-2xl overflow-hidden flex flex-col max-h-[92vh] animate-in fade-in zoom-in-95 duration-200"
    >
      <!-- 1. Header del Constructor -->
      <div class="px-5 sm:px-7 py-4 sm:py-5 border-b border-darkBorder/70 flex items-center justify-between bg-gradient-to-r from-darkCard/90 via-slate-900/90 to-darkCard/90">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-sm shadow-cyan-500/10">
            <Sliders class="w-5 h-5" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base sm:text-lg font-black text-slate-100 tracking-tight">
                Constructor de Reportes de Novedades
              </h2>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                Personalizado
              </span>
            </div>
            <p class="text-xs text-slate-400 hidden sm:block">
              Diseñe reportes personalizados: elija filtros, columnas y active la exportación ágil sin filas repetidas para comandancia.
            </p>
          </div>
        </div>

        <button 
          @click="cerrarModal"
          class="p-2 rounded-xl text-slate-400 hover:text-slate-100 hover:bg-slate-800/80 transition-colors cursor-pointer border border-transparent hover:border-darkBorder"
          title="Cerrar ventana"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- 2. Cuerpo del Constructor (Scrollable) -->
      <div class="p-5 sm:p-7 overflow-y-auto space-y-6 scrollbar-thin">
        
        <!-- A. Selector de Enfoque / Modo de Reporte -->
        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2.5">
            1. Modo y Estilo del Reporte:
          </label>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            <!-- Opción Ágil (Comandancia) -->
            <button
              type="button"
              @click="cambiarModo('agil')"
              class="p-4 rounded-2xl border text-left transition-all cursor-pointer relative overflow-hidden flex flex-col justify-between"
              :class="config.modo === 'agil' 
                ? 'bg-cyan-500/10 border-cyan-400/80 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-400/50' 
                : 'bg-darkCard/60 border-darkBorder hover:border-slate-600 hover:bg-slate-800/40 text-slate-400'"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-2.5">
                  <div 
                    class="w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs"
                    :class="config.modo === 'agil' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'"
                  >
                    <Zap class="w-4 h-4" />
                  </div>
                  <div>
                    <h3 class="text-xs sm:text-sm font-black text-slate-100 flex items-center gap-1.5">
                      Modo Ágil (Para Comandancia)
                      <span class="text-[10px] font-bold px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        Recomendado
                      </span>
                    </h3>
                    <p class="text-[11px] text-slate-400 leading-snug mt-0.5">
                      <strong>1 sola fila por integrante</strong>. Comprime fechas continuas en rangos (ej: <span class="font-mono text-cyan-300">01-10 (VACACIONES)</span>). Cero filas duplicadas.
                    </p>
                  </div>
                </div>
                <div 
                  class="w-4 h-4 rounded-full border flex items-center justify-center shrink-0 mt-0.5"
                  :class="config.modo === 'agil' ? 'border-cyan-400 bg-cyan-400 text-slate-950' : 'border-slate-600'"
                >
                  <Check v-if="config.modo === 'agil'" class="w-3 h-3 stroke-[3]" />
                </div>
              </div>
            </button>

            <!-- Opción Detallada (Auditoría Día a Día) -->
            <button
              type="button"
              @click="cambiarModo('detallado')"
              class="p-4 rounded-2xl border text-left transition-all cursor-pointer relative overflow-hidden flex flex-col justify-between"
              :class="config.modo === 'detallado' 
                ? 'bg-cyan-500/10 border-cyan-400/80 shadow-lg shadow-cyan-500/10 ring-1 ring-cyan-400/50' 
                : 'bg-darkCard/60 border-darkBorder hover:border-slate-600 hover:bg-slate-800/40 text-slate-400'"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-2.5">
                  <div 
                    class="w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs"
                    :class="config.modo === 'detallado' ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'"
                  >
                    <ListFilter class="w-4 h-4" />
                  </div>
                  <div>
                    <h3 class="text-xs sm:text-sm font-black text-slate-100">
                      Modo Detallado (Auditoría Día a Día)
                    </h3>
                    <p class="text-[11px] text-slate-400 leading-snug mt-0.5">
                      <strong>1 fila por cada reporte diario</strong>. Muestra fechas exactas individuales de cada jornada, fechas desde/hasta registradas y justificación.
                    </p>
                  </div>
                </div>
                <div 
                  class="w-4 h-4 rounded-full border flex items-center justify-center shrink-0 mt-0.5"
                  :class="config.modo === 'detallado' ? 'border-cyan-400 bg-cyan-400 text-slate-950' : 'border-slate-600'"
                >
                  <Check v-if="config.modo === 'detallado'" class="w-3 h-3 stroke-[3]" />
                </div>
              </div>
            </button>
          </div>
        </div>

        <!-- B. Filtros de Datos -->
        <div class="glass-panel p-4 sm:p-5 rounded-2xl border border-darkBorder/80 bg-slate-900/60 space-y-4">
          <div class="flex items-center justify-between border-b border-darkBorder/50 pb-2.5">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Filter class="w-3.5 h-3.5 text-cyan-400" />
              2. Filtros del Reporte
            </h3>
            <span class="text-[11px] text-slate-500 font-mono">Cruce de Criterios</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <!-- Novedad a Auditar -->
            <div>
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Novedad / Subnovedad
              </label>
              <select
                v-model="config.id_sub_novedad"
                @change="debouncedPreview"
                class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
              >
                <option :value="null">-- TODAS LAS NOVEDADES --</option>
                <option v-for="nov in catalogo" :key="nov.id" :value="nov.id">
                  {{ nov.nombre }} ({{ nov.total_registros }} días)
                </option>
              </select>
            </div>

            <!-- Mes Operacional -->
            <div>
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
                <span>Mes Operacional</span>
                <span v-if="mesLimits.isSpecificMonth" class="text-[10px] text-cyan-400 font-mono font-bold">
                  {{ mesLimits.totalDias }} días
                </span>
              </label>
              <select
                v-model="config.mes"
                @change="onMesChange"
                class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
              >
                <option value="TODOS">TODOS LOS MESES (AÑO COMPLETO)</option>
                <option v-for="m in mesesDisponibles" :key="m" :value="m">
                  {{ m }}
                </option>
              </select>
            </div>

            <!-- Rango de Fechas: Desde -->
            <div>
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
                <span>Fecha Desde</span>
                <span v-if="mesLimits.isSpecificMonth" class="text-[10px] text-amber-400 font-mono">
                  Min: 01/{{ mesLimits.mesNum }}
                </span>
              </label>
              <input
                v-model="config.fecha_inicio"
                :min="mesLimits.min"
                :max="config.fecha_fin || mesLimits.max"
                @change="onFechaInicioChange"
                type="date"
                class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all"
              />
            </div>

            <!-- Rango de Fechas: Hasta -->
            <div>
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5 flex items-center justify-between">
                <span>Fecha Hasta</span>
                <span v-if="mesLimits.isSpecificMonth" class="text-[10px] text-amber-400 font-mono">
                  Max: {{ mesLimits.totalDias }}/{{ mesLimits.mesNum }}
                </span>
              </label>
              <input
                v-model="config.fecha_fin"
                :min="config.fecha_inicio || mesLimits.min"
                :max="mesLimits.max"
                @change="onFechaFinChange"
                type="date"
                class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all"
              />
            </div>

            <!-- Barra de sincronización y accesos rápidos de fechas -->
            <div class="sm:col-span-2 lg:col-span-4 flex flex-wrap items-center justify-between gap-2 px-3.5 py-2 rounded-xl bg-slate-950/70 border border-darkBorder/70 text-xs">
              <div class="flex items-center gap-2 text-slate-300">
                <span class="w-2 h-2 rounded-full" :class="mesLimits.isSpecificMonth ? 'bg-cyan-400 animate-pulse' : 'bg-slate-500'"></span>
                <span v-if="mesLimits.isSpecificMonth" class="text-[11px]">
                  Filtro sincronizado con <strong class="text-cyan-300 font-semibold">{{ config.mes }} {{ anioOperacional }}</strong> (rango estricto del 01 al {{ mesLimits.totalDias }})
                </span>
                <span v-else class="text-[11px] text-slate-400">
                  Filtro libre en todo el año <strong class="text-slate-200 font-mono">{{ anioOperacional }}</strong>
                  <span v-if="config.fecha_inicio || config.fecha_fin" class="text-cyan-400 ml-1 font-mono">
                    ({{ config.fecha_inicio || '01/01' }} ➔ {{ config.fecha_fin || '31/12' }})
                  </span>
                </span>
              </div>

              <!-- Botones rápidos de quincena y limpieza -->
              <div class="flex items-center gap-1.5">
                <template v-if="mesLimits.isSpecificMonth">
                  <button
                    type="button"
                    @click="aplicarPresetMes('todo')"
                    class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-bold transition-all cursor-pointer border border-darkBorder"
                  >
                    Todo el Mes
                  </button>
                  <button
                    type="button"
                    @click="aplicarPresetMes('q1')"
                    class="px-2.5 py-1 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 text-[10px] font-bold transition-all cursor-pointer border border-cyan-500/30"
                  >
                    1ra Quincena (01-15)
                  </button>
                  <button
                    type="button"
                    @click="aplicarPresetMes('q2')"
                    class="px-2.5 py-1 rounded-lg bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 text-[10px] font-bold transition-all cursor-pointer border border-cyan-500/30"
                  >
                    2da Quincena (16-{{ mesLimits.totalDias }})
                  </button>
                </template>
                <button
                  v-if="config.fecha_inicio || config.fecha_fin"
                  type="button"
                  @click="aplicarPresetMes('limpiar')"
                  class="px-2.5 py-1 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 text-[10px] font-bold transition-all cursor-pointer border border-rose-500/30"
                >
                  Limpiar Fechas
                </button>
              </div>
            </div>

            <!-- Estado de Personal -->
            <div>
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Estado del Personal
              </label>
              <select
                v-model="config.estado"
                @change="debouncedPreview"
                class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
              >
                <option value="TODOS">TODOS (ACTIVOS Y RETIRADOS)</option>
                <option value="ACTIVO">SOLO ACTIVOS</option>
                <option value="RETIRADO">SOLO RETIRADOS</option>
              </select>
            </div>

            <!-- Mínimo de Días Acumulados -->
            <div>
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Filtro por Incidencia
              </label>
              <select
                v-model="config.min_dias"
                @change="debouncedPreview"
                class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl px-3 py-2 text-xs font-medium focus:outline-none transition-all cursor-pointer"
              >
                <option :value="0">Cualquier duración (Desde 1 día)</option>
                <option :value="3">Con 3 o más días acumulados</option>
                <option :value="5">Con 5 o más días acumulados</option>
                <option :value="10">Con 10 o más días (Casos críticos)</option>
                <option :value="15">Con 15 o más días (Prolongados)</option>
              </select>
            </div>

            <!-- Búsqueda específica -->
            <div class="sm:col-span-2">
              <label class="block text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
                Búsqueda por Cédula, Nombre o Motivo
              </label>
              <div class="relative">
                <Search class="w-3.5 h-3.5 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  v-model="config.q"
                  @input="debouncedPreview"
                  type="text"
                  placeholder="Ej: Cédula, Apellido o palabra en descripción..."
                  class="w-full bg-slate-950 border border-darkBorder hover:border-cyan-500/40 focus:border-cyan-400 text-slate-200 rounded-xl pl-9 pr-3 py-2 text-xs font-medium focus:outline-none transition-all placeholder:text-slate-600"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- C. Columnas Visibles y Ordenamiento -->
        <div class="glass-panel p-4 sm:p-5 rounded-2xl border border-darkBorder/80 bg-slate-900/60 space-y-4">
          <div class="flex items-center justify-between border-b border-darkBorder/50 pb-2.5">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Columns3 class="w-3.5 h-3.5 text-cyan-400" />
              3. Columnas y Ordenamiento
            </h3>
            <div class="flex items-center gap-2 text-xs">
              <label class="text-[11px] font-semibold text-slate-400">Ordenar por:</label>
              <select
                v-model="config.orden"
                @change="debouncedPreview"
                class="bg-slate-950 border border-darkBorder text-slate-200 rounded-lg px-2.5 py-1 text-xs font-semibold focus:outline-none focus:border-cyan-400 cursor-pointer"
              >
                <option value="nombre_asc">Alfabético por Integrante (A - Z)</option>
                <option value="fecha_desc">Fecha más reciente primero</option>
                <option value="fecha_asc">Fecha más antigua primero</option>
                <option value="dias_desc">Mayor cantidad de días acumulados</option>
              </select>
            </div>
          </div>

          <!-- Checkboxes de Columnas disponibles -->
          <div>
            <div class="text-[11px] text-slate-400 mb-2 font-medium">
              Marque las columnas que desea incluir en el archivo final:
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
              <label 
                v-for="col in columnasDisponibles" 
                :key="col.id"
                class="flex items-center gap-2.5 p-2 rounded-xl border border-darkBorder/60 bg-darkCard/40 hover:bg-slate-800/50 cursor-pointer transition-colors"
                :class="{ 'border-cyan-500/40 bg-cyan-500/5': config.columnas.includes(col.id) }"
              >
                <input 
                  type="checkbox"
                  :value="col.id"
                  v-model="config.columnas"
                  class="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-400/30 cursor-pointer"
                />
                <span class="text-xs font-medium text-slate-200 select-none">
                  {{ col.label }}
                </span>
              </label>
            </div>
          </div>
        </div>

        <!-- D. Vista Previa en Vivo (Live Preview) -->
        <div class="glass-panel p-4 sm:p-5 rounded-2xl border border-darkBorder/80 bg-slate-950/80 space-y-3">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-darkBorder/50 pb-2.5">
            <div class="flex items-center gap-2">
              <Eye class="w-3.5 h-3.5 text-cyan-400" />
              <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200">
                4. Vista Previa del Reporte
              </h3>
              <span v-if="previewData" class="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px] font-mono font-bold border border-cyan-500/20">
                {{ previewData.total_filas }} filas estimadas / {{ previewData.total_personal }} efectivos
              </span>
            </div>
            <div class="text-[11px] text-slate-500 italic">
              Mostrando las primeras 5 filas de muestra
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="isLoadingPreview" class="py-8 flex flex-col items-center justify-center gap-2 text-slate-400">
            <Loader2 class="w-6 h-6 animate-spin text-cyan-400" />
            <span class="text-xs">Actualizando vista previa en tiempo real...</span>
          </div>

          <!-- Empty State -->
          <div v-else-if="!previewData || previewData.filas.length === 0" class="py-8 text-center text-slate-500 text-xs">
            No se encontraron registros con los filtros seleccionados. Pruebe ampliando el rango o cambiando la novedad.
          </div>

          <!-- Tabla de Muestra -->
          <div v-else class="overflow-x-auto rounded-xl border border-darkBorder/60 scrollbar-thin">
            <table class="w-full text-left text-xs">
              <thead class="bg-slate-900 text-slate-300 uppercase tracking-wider text-[10px] font-bold border-b border-darkBorder">
                <tr>
                  <th v-if="config.columnas.includes('cedula')" class="px-3 py-2 text-center">Cédula</th>
                  <th v-if="config.columnas.includes('nombre')" class="px-3 py-2">Integrante</th>
                  <th v-if="config.columnas.includes('estado')" class="px-3 py-2 text-center">Estado</th>
                  <th v-if="config.columnas.includes('sub_novedad')" class="px-3 py-2">Novedad</th>
                  <th v-if="config.modo === 'agil' && config.columnas.includes('rango_fechas')" class="px-3 py-2">
                    Rangos Condensados
                  </th>
                  <th v-if="config.modo === 'agil' && config.columnas.includes('dias_acumulados')" class="px-3 py-2 text-center">
                    Días Totales
                  </th>
                  <th v-if="config.modo === 'detallado' && config.columnas.includes('fecha_reporte')" class="px-3 py-2 text-center">
                    Fecha Reporte
                  </th>
                  <th v-if="config.modo === 'detallado' && config.columnas.includes('fecha_inicio')" class="px-3 py-2 text-center">
                    Desde
                  </th>
                  <th v-if="config.modo === 'detallado' && config.columnas.includes('fecha_final')" class="px-3 py-2 text-center">
                    Hasta
                  </th>
                  <th v-if="config.columnas.includes('descripcion')" class="px-3 py-2">
                    Descripción / Motivo
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-darkBorder/40 bg-slate-950/60 font-mono">
                <tr v-for="(fila, idx) in previewData.filas" :key="idx" class="hover:bg-slate-900/60 transition-colors">
                  <td v-if="config.columnas.includes('cedula')" class="px-3 py-2 text-center text-slate-300 font-bold">
                    {{ fila.cedula }}
                  </td>
                  <td v-if="config.columnas.includes('nombre')" class="px-3 py-2 text-slate-100 font-sans font-semibold">
                    {{ fila.nombre }}
                  </td>
                  <td v-if="config.columnas.includes('estado')" class="px-3 py-2 text-center">
                    <span 
                      class="px-1.5 py-0.5 rounded text-[10px] font-sans font-bold"
                      :class="fila.estado === 'ACTIVO' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-slate-700/40 text-slate-400'"
                    >
                      {{ fila.estado }}
                    </span>
                  </td>
                  <td v-if="config.columnas.includes('sub_novedad')" class="px-3 py-2 text-cyan-300 font-sans">
                    {{ fila.sub_novedad || '-' }}
                  </td>
                  <td v-if="config.modo === 'agil' && config.columnas.includes('rango_fechas')" class="px-3 py-2 text-amber-300">
                    {{ fila.rango_fechas || '-' }}
                  </td>
                  <td v-if="config.modo === 'agil' && config.columnas.includes('dias_acumulados')" class="px-3 py-2 text-center font-bold text-slate-100">
                    {{ fila.dias_acumulados || 0 }} d
                  </td>
                  <td v-if="config.modo === 'detallado' && config.columnas.includes('fecha_reporte')" class="px-3 py-2 text-center text-slate-400">
                    {{ fila.fecha_reporte }}
                  </td>
                  <td v-if="config.modo === 'detallado' && config.columnas.includes('fecha_inicio')" class="px-3 py-2 text-center text-slate-400">
                    {{ fila.fecha_inicio || '-' }}
                  </td>
                  <td v-if="config.modo === 'detallado' && config.columnas.includes('fecha_final')" class="px-3 py-2 text-center text-slate-400">
                    {{ fila.fecha_final || '-' }}
                  </td>
                  <td v-if="config.columnas.includes('descripcion')" class="px-3 py-2 text-slate-400 font-sans text-[11px] truncate max-w-xs">
                    {{ fila.descripcion || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- 3. Footer con Botones de Descarga -->
      <div class="px-5 sm:px-7 py-4 border-t border-darkBorder/70 bg-gradient-to-r from-slate-900/95 via-darkCard/95 to-slate-900/95 flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0">
        <div class="text-xs text-slate-400">
          Modo seleccionado: 
          <span class="font-bold text-cyan-400 capitalize">{{ config.modo }}</span>
          <span v-if="config.modo === 'agil'" class="text-amber-400 font-semibold ml-1">
            (Resumido sin duplicados)
          </span>
        </div>

        <div class="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button
            type="button"
            @click="cerrarModal"
            class="px-4 py-2.5 rounded-xl border border-darkBorder hover:bg-slate-800 text-slate-300 text-xs font-semibold transition-colors cursor-pointer"
          >
            Cancelar
          </button>

          <!-- Exportar Excel -->
          <button
            type="button"
            @click="descargar('excel')"
            :disabled="isDownloadingExcel || isDownloadingPdf || isLoadingPreview"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition-all shadow-md shadow-emerald-500/20 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="isDownloadingExcel" class="w-4 h-4 animate-spin text-slate-950" />
            <FileSpreadsheet v-else class="w-4 h-4 text-slate-950" />
            <span>{{ isDownloadingExcel ? 'Generando Excel...' : 'Descargar Excel' }}</span>
          </button>

          <!-- Exportar PDF -->
          <button
            type="button"
            @click="descargar('pdf')"
            :disabled="isDownloadingExcel || isDownloadingPdf || isLoadingPreview"
            class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-500 hover:bg-rose-400 text-white font-bold text-xs transition-all shadow-md shadow-rose-500/20 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Loader2 v-if="isDownloadingPdf" class="w-4 h-4 animate-spin text-white" />
            <FileText v-else class="w-4 h-4 text-white" />
            <span>{{ isDownloadingPdf ? 'Generando PDF...' : 'Descargar PDF' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import {
  Sliders,
  X,
  Zap,
  ListFilter,
  Check,
  Filter,
  Columns3,
  Eye,
  Loader2,
  FileSpreadsheet,
  FileText,
  Search
} from 'lucide-vue-next'

import type {
  NovedadCatalogoItem,
  ReportBuilderConfig,
  ReportBuilderModo,
  ReportBuilderPreviewResponse
} from '../types/novedades.types'
import { novedadesService } from '../services/novedades.service'
import { MONTH_TO_NUMBER, getDaysInMonth } from '@/utils/date'

const props = defineProps<{
  isOpen: boolean
  catalogo: NovedadCatalogoItem[]
  mesesDisponibles: string[]
  initialFilters?: {
    id_sub_novedad?: number | null
    mes?: string
    fecha_inicio?: string
    fecha_fin?: string
    estado?: 'TODOS' | 'ACTIVO' | 'RETIRADO'
    q?: string
  }
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const anioOperacional = 2026

// Columnas por defecto para cada modo
const COLUMNAS_AGIL = ['cedula', 'nombre', 'estado', 'sub_novedad', 'rango_fechas', 'dias_acumulados', 'descripcion']
const COLUMNAS_DETALLADO = ['cedula', 'nombre', 'estado', 'sub_novedad', 'fecha_reporte', 'fecha_inicio', 'fecha_final', 'descripcion']

// Configuración reactiva del constructor
const config = reactive<ReportBuilderConfig>({
  modo: 'agil',
  id_sub_novedad: props.initialFilters?.id_sub_novedad ?? null,
  mes: props.initialFilters?.mes || 'TODOS',
  fecha_inicio: props.initialFilters?.fecha_inicio || '',
  fecha_fin: props.initialFilters?.fecha_fin || '',
  q: props.initialFilters?.q || '',
  estado: props.initialFilters?.estado || 'TODOS',
  min_dias: 0,
  columnas: [...COLUMNAS_AGIL],
  orden: 'nombre_asc'
})

// Cálculo reactivo de los límites de fecha según el mes operacional
const mesLimits = computed(() => {
  if (!config.mes || config.mes === 'TODOS') {
    return {
      min: `${anioOperacional}-01-01`,
      max: `${anioOperacional}-12-31`,
      isSpecificMonth: false,
      totalDias: 31,
      mesNum: '',
      label: 'Año Completo (2026)'
    }
  }
  const mNum = MONTH_TO_NUMBER[config.mes.toUpperCase()] || '01'
  const total = getDaysInMonth(config.mes, anioOperacional)
  const totalStr = String(total).padStart(2, '0')
  return {
    min: `${anioOperacional}-${mNum}-01`,
    max: `${anioOperacional}-${mNum}-${totalStr}`,
    isSpecificMonth: true,
    totalDias: total,
    mesNum: mNum,
    label: `${config.mes} ${anioOperacional}`
  }
})

// Lista dinámica de columnas según el modo
const columnasDisponibles = computed(() => {
  if (config.modo === 'agil') {
    return [
      { id: 'cedula', label: 'Cédula de Ciudadanía' },
      { id: 'nombre', label: 'Apellidos y Nombres' },
      { id: 'estado', label: 'Estado (Activo / Retirado)' },
      { id: 'sub_novedad', label: 'Tipo de Novedad' },
      { id: 'rango_fechas', label: 'Rangos Condensados (ej: 01-10)' },
      { id: 'dias_acumulados', label: 'Total Días Acumulados' },
      { id: 'descripcion', label: 'Descripción / Motivo' }
    ]
  } else {
    return [
      { id: 'cedula', label: 'Cédula de Ciudadanía' },
      { id: 'nombre', label: 'Apellidos y Nombres' },
      { id: 'estado', label: 'Estado (Activo / Retirado)' },
      { id: 'sub_novedad', label: 'Tipo de Novedad' },
      { id: 'fecha_reporte', label: 'Fecha del Reporte' },
      { id: 'fecha_inicio', label: 'Fecha Inicio (Desde)' },
      { id: 'fecha_final', label: 'Fecha Final (Hasta)' },
      { id: 'descripcion', label: 'Descripción / Motivo' }
    ]
  }
})

// Estados de carga
const isLoadingPreview = ref(false)
const isDownloadingExcel = ref(false)
const isDownloadingPdf = ref(false)
const previewData = ref<ReportBuilderPreviewResponse | null>(null)

let debounceTimer: any = null
const debouncedPreview = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    cargarPreview()
  }, 350)
}

const cambiarModo = (nuevoModo: ReportBuilderModo) => {
  config.modo = nuevoModo
  config.columnas = nuevoModo === 'agil' ? [...COLUMNAS_AGIL] : [...COLUMNAS_DETALLADO]
  debouncedPreview()
}

// Sincronización cuando cambia el mes operacional
const onMesChange = () => {
  if (mesLimits.value.isSpecificMonth) {
    const { min, max } = mesLimits.value
    // Si las fechas actuales están fuera de los límites del mes seleccionado, limpiarlas
    if (config.fecha_inicio && (config.fecha_inicio < min || config.fecha_inicio > max)) {
      config.fecha_inicio = ''
    }
    if (config.fecha_fin && (config.fecha_fin < min || config.fecha_fin > max)) {
      config.fecha_fin = ''
    }
  }
  debouncedPreview()
}

// Sincronización y validación estricta de Fecha Desde
const onFechaInicioChange = () => {
  if (config.fecha_inicio) {
    // Clamping con los límites actuales del mes
    if (config.fecha_inicio < mesLimits.value.min) {
      config.fecha_inicio = mesLimits.value.min
    } else if (config.fecha_inicio > mesLimits.value.max) {
      config.fecha_inicio = mesLimits.value.max
    }
    // Sincronizar fecha fin si quedó menor que fecha inicio
    if (config.fecha_fin && config.fecha_fin < config.fecha_inicio) {
      config.fecha_fin = config.fecha_inicio
    }
  }
  debouncedPreview()
}

// Sincronización y validación estricta de Fecha Hasta
const onFechaFinChange = () => {
  if (config.fecha_fin) {
    // Clamping con los límites actuales del mes
    if (config.fecha_fin > mesLimits.value.max) {
      config.fecha_fin = mesLimits.value.max
    } else if (config.fecha_fin < mesLimits.value.min) {
      config.fecha_fin = mesLimits.value.min
    }
    // Sincronizar fecha inicio si quedó mayor que fecha fin
    if (config.fecha_inicio && config.fecha_inicio > config.fecha_fin) {
      config.fecha_inicio = config.fecha_fin
    }
  }
  debouncedPreview()
}

// Aplicar presets de quincenas o mes completo
const aplicarPresetMes = (tipo: 'todo' | 'q1' | 'q2' | 'limpiar') => {
  if (tipo === 'limpiar') {
    config.fecha_inicio = ''
    config.fecha_fin = ''
  } else if (!mesLimits.value.isSpecificMonth) {
    config.fecha_inicio = ''
    config.fecha_fin = ''
  } else {
    const { min, max, mesNum, totalDias } = mesLimits.value
    const totalStr = String(totalDias).padStart(2, '0')
    if (tipo === 'todo') {
      config.fecha_inicio = min
      config.fecha_fin = max
    } else if (tipo === 'q1') {
      config.fecha_inicio = `${anioOperacional}-${mesNum}-01`
      config.fecha_fin = `${anioOperacional}-${mesNum}-15`
    } else if (tipo === 'q2') {
      config.fecha_inicio = `${anioOperacional}-${mesNum}-16`
      config.fecha_fin = `${anioOperacional}-${mesNum}-${totalStr}`
    }
  }
  debouncedPreview()
}

const cargarPreview = async () => {
  if (!props.isOpen) return
  isLoadingPreview.value = true
  try {
    const res = await novedadesService.obtenerPreviewBuilder(config)
    previewData.value = res
  } catch (err) {
    console.error('Error cargando preview:', err)
    previewData.value = null
  } finally {
    isLoadingPreview.value = false
  }
}

const descargar = async (formato: 'excel' | 'pdf') => {
  if (formato === 'excel') isDownloadingExcel.value = true
  else isDownloadingPdf.value = true

  try {
    await novedadesService.descargarReporteBuilder(formato, config)
  } catch (err: any) {
    alert(err.message || `Error descargando el reporte en ${formato.toUpperCase()}`)
  } finally {
    if (formato === 'excel') isDownloadingExcel.value = false
    else isDownloadingPdf.value = false
  }
}

const cerrarModal = () => {
  emit('close')
}

// Sincronizar filtros iniciales cuando se abre el modal
watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      if (props.initialFilters) {
        config.id_sub_novedad = props.initialFilters.id_sub_novedad ?? null
        config.mes = props.initialFilters.mes || 'TODOS'
        config.fecha_inicio = props.initialFilters.fecha_inicio || ''
        config.fecha_fin = props.initialFilters.fecha_fin || ''
        config.q = props.initialFilters.q || ''
        config.estado = props.initialFilters.estado || 'TODOS'

        // Validar coherencia de fechas iniciales recibidas
        if (config.fecha_inicio && config.fecha_fin && config.fecha_inicio > config.fecha_fin) {
          const temp = config.fecha_inicio
          config.fecha_inicio = config.fecha_fin
          config.fecha_fin = temp
        }
        if (mesLimits.value.isSpecificMonth) {
          const { min, max } = mesLimits.value
          if (config.fecha_inicio && (config.fecha_inicio < min || config.fecha_inicio > max)) {
            config.fecha_inicio = ''
          }
          if (config.fecha_fin && (config.fecha_fin < min || config.fecha_fin > max)) {
            config.fecha_fin = ''
          }
        }
      }
      cargarPreview()
    }
  }
)
</script>
