<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[320px] sm:h-[400px]">
    <h3 class="text-xs sm:text-sm font-bold text-slate-200 mb-3 uppercase tracking-wider flex items-center gap-2">
      <span class="w-2 h-4 bg-amber-500 rounded-sm"></span> Novedades más Frecuentes {{ month ? `(${month})` : '(Anual)' }}
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
import { fetchNovedadesFrecuentes } from '../../services/api'

const props = defineProps<{
  month?: string
  day?: string
}>()

const { chartDom, setOption } = useECharts()

const renderChart = async () => {
  if (!chartDom.value) return
  try {
    const data = await fetchNovedadesFrecuentes(props.month, props.day)
    const names = data.slice(0, 5).map((d: { novedad: string }) => d.novedad)
    const values = data.slice(0, 5).map((d: { cantidad: number }) => d.cantidad)

    setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' }
      },
      grid: { top: 20, right: 10, bottom: 30, left: 80 },
      xAxis: {
        type: 'value',
        axisLine: { lineStyle: { color: '#1f2b45' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1f2b45' } }
      },
      yAxis: {
        type: 'category',
        data: names.reverse(),
        axisLine: { lineStyle: { color: '#1f2b45' } },
        axisLabel: { color: '#f1f5f9', fontSize: 10 }
      },
      series: [
        {
          type: 'bar',
          data: values.reverse(),
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#f59e0b' },
              { offset: 1, color: '#ef4444' }
            ]),
            borderRadius: [0, 4, 4, 0]
          },
          label: {
            show: true,
            position: 'right',
            color: '#f1f5f9',
            fontSize: 10
          }
        }
      ]
    })
  } catch (error) {
    console.error('Error cargando gráfico de novedades frecuentes:', error)
  }
}

watch(() => [props.month, props.day], () => {
  renderChart()
})

onMounted(() => {
  renderChart()
})
</script>
