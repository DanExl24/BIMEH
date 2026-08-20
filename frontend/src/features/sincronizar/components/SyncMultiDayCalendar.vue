<template>
  <div class="space-y-3 md:col-span-2">
    <div>
      <label class="text-xs uppercase font-bold text-slate-300">Mes de Referencia:</label>
      <select 
        :value="multiDayMonth"
        @change="$emit('update:multiDayMonth', ($event.target as HTMLSelectElement).value)"
        class="w-full bg-darkBg border border-darkBorder rounded-xl px-3 py-2 text-xs font-semibold text-slate-100 outline-none focus:border-cyan-500/60 max-w-sm mt-1.5 shadow-sm cursor-pointer"
      >
        <option v-for="m in months" :key="m" :value="m">{{ m }}</option>
      </select>
    </div>

    <!-- Calendar Container -->
    <div class="bg-darkBg border border-darkBorder rounded-2xl p-4 max-w-sm shadow-inner">
      <div class="flex items-center justify-between mb-3 border-b border-darkBorder/60 pb-2">
        <span class="text-xs uppercase font-bold text-slate-300">Seleccionar Días:</span>
        <div class="flex items-center gap-3">
          <button 
            type="button" 
            @click="$emit('select-all')" 
            class="text-xs text-cyan-400 hover:text-cyan-300 font-bold transition-colors cursor-pointer"
          >
            Todos
          </button>
          <span class="text-slate-600">|</span>
          <button 
            type="button" 
            @click="$emit('clear-all')" 
            class="text-xs text-slate-400 hover:text-slate-200 font-bold transition-colors cursor-pointer"
          >
            Limpiar
          </button>
        </div>
      </div>

      <div class="grid grid-cols-7 gap-1">
        <!-- Weekday Headers -->
        <div v-for="d in ['Lu','Ma','Mi','Ju','Vi','Sa','Do']" :key="d" class="text-center text-xs font-bold text-slate-400 py-1">{{ d }}</div>
        
        <!-- Padding empty cells -->
        <div v-for="n in calendarPadding" :key="'pad-'+n"></div>

        <!-- Month Days -->
        <button
          v-for="day in calendarDays"
          :key="day.date"
          type="button"
          @click="$emit('toggle-day', day.date)"
          class="w-full h-8 flex items-center justify-center rounded-lg text-xs font-bold transition-all border cursor-pointer select-none"
          :class="selectedDates.includes(day.date)
            ? 'bg-cyan-500/30 text-cyan-300 border-cyan-500/50 shadow-sm font-black'
            : 'text-slate-300 border-transparent hover:bg-slate-800 hover:text-white'"
        >
          {{ day.num }}
        </button>
      </div>

      <div v-if="selectedDates.length > 0" class="mt-3 pt-2.5 border-t border-darkBorder/60 flex items-center justify-between">
        <span class="text-xs text-cyan-400 font-bold">
          {{ selectedDates.length }} día{{ selectedDates.length > 1 ? 's' : '' }} seleccionado{{ selectedDates.length > 1 ? 's' : '' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  multiDayMonth: string
  months: string[] | readonly string[]
  selectedDates: string[]
  calendarDays: { num: number; date: string }[]
  calendarPadding: number
}>()

defineEmits<{
  (e: 'update:multiDayMonth', val: string): void
  (e: 'toggle-day', date: string): void
  (e: 'select-all'): void
  (e: 'clear-all'): void
}>()
</script>
