<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[340px] sm:h-[420px]">
    <h3 class="text-xs sm:text-sm font-bold text-slate-200 mb-3 uppercase tracking-wider flex items-center gap-2">
      <span class="w-2 h-4 bg-amber-500 rounded-sm"></span> Top Novedades Frecuentes
    </h3>
    <div class="flex-1 min-h-0">
      <div ref="chartDom" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useECharts } from '@composables/useECharts'
import { dashboardService } from '../services/dashboard.service'

const props = defineProps<{
  month?: string
  day?: string
}>()

const { chartDom, setOption } = useECharts()

const renderChart = async () => {
  if (!chartDom.value) return
  try {
    const data = await dashboardService.getNovedadesFrecuentes(props.month, props.day)
    const names = data.slice(0, 5).map((d: { novedad: string }) => d.novedad)
    const values = data.slice(0, 5).map((d: { cantidad: number }) => d.cantidad)

    setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' },
        axisPointer: { type: 'shadow' }
      },
      grid: {
        top: '6%',
        left: '2%',
        right: '6%',
        bottom: '6%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        axisLabel: { color: '#64748b', fontSize: 9 },
        splitLine: { lineStyle: { color: '#1f2b45', type: 'dashed' } }
      },
      yAxis: {
        type: 'category',
        data: names.reverse(),
        axisLine: { lineStyle: { color: '#1f2b45' } },
        axisLabel: {
          color: '#94a3b8',
          fontSize: 9,
          formatter: (value: string) => {
            return value.length > 15 ? value.substring(0, 15) + '...' : value
          }
        }
      },
      series: [
        {
          name: 'Cantidad',
          type: 'bar',
          data: values.reverse(),
          itemStyle: {
            color: '#f59e0b',
            borderRadius: [0, 4, 4, 0]
          },
          label: {
            show: true,
            position: 'right',
            color: '#94a3b8',
            fontSize: 9
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
