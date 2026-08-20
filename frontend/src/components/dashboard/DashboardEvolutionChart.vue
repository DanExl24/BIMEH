<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[320px] sm:h-[400px]">
    <h3 class="text-xs sm:text-sm font-bold text-slate-200 mb-3 uppercase tracking-wider flex items-center gap-2">
      <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Evolución de Disponibilidad Diaria {{ month ? `(${month})` : '(Anual)' }}
    </h3>
    <div class="flex-1 min-h-0">
      <div ref="chartDom" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useECharts } from '../../composables/useECharts'
import { fetchEvolucion } from '../../services/api'

const props = defineProps<{
  month?: string
  day?: string
}>()

const { chartDom, setOption } = useECharts()

const renderChart = async () => {
  if (!chartDom.value) return
  try {
    const data = await fetchEvolucion(props.month, props.day)
    const dates = data.map((d: { fecha: string }) => d.fecha)
    const disponibilidades = data.map((d: { disponibilidad: number }) => d.disponibilidad)
    const disponibles = data.map((d: { disponibles: number }) => d.disponibles)

    setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line' },
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' }
      },
      grid: { top: 30, right: 20, bottom: 40, left: 50 },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#1f2b45' } },
        axisLabel: { color: '#94a3b8', fontSize: 10, rotate: 30 },
        splitLine: { show: false }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Disp. %',
          min: 0,
          max: 100,
          axisLabel: { color: '#94a3b8', formatter: '{value}%' },
          splitLine: { lineStyle: { color: '#1f2b45' } }
        },
        {
          type: 'value',
          name: 'Disponibles',
          axisLabel: { color: '#94a3b8' },
          splitLine: { show: false }
        }
      ],
      series: [
        {
          name: 'Disponibilidad %',
          type: 'line',
          data: disponibilidades,
          smooth: true,
          lineStyle: { width: 3, color: '#06b6d4' },
          itemStyle: { color: '#06b6d4' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(6, 182, 212, 0.25)' },
              { offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
            ])
          }
        },
        {
          name: 'Pers. Disponible',
          type: 'bar',
          yAxisIndex: 1,
          data: disponibles,
          itemStyle: { color: 'rgba(16, 185, 129, 0.2)' }
        }
      ]
    })
  } catch (error) {
    console.error('Error cargando gráfico de evolución:', error)
  }
}

watch(() => [props.month, props.day], () => {
  renderChart()
})

onMounted(() => {
  renderChart()
})
</script>
