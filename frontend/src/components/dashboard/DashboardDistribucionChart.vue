<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[340px] sm:h-[420px]">
    <h3 class="text-xs sm:text-sm font-bold text-slate-200 mb-3 uppercase tracking-wider flex items-center gap-2">
      <span class="w-2 h-4 bg-teal-500 rounded-sm"></span> Distribución del Personal por Estado
    </h3>
    <div class="flex-1 min-h-0">
      <div ref="chartDom" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useECharts } from '../../composables/useECharts'
import { fetchDistribucion } from '../../services/api'

const props = defineProps<{
  month?: string
  day?: string
}>()

const { chartDom, setOption } = useECharts()

const renderChart = async () => {
  if (!chartDom.value) return
  try {
    const data = await fetchDistribucion(props.month, props.day)
    const sorted = [...data].sort((a, b) => b.cantidad - a.cantidad)
    const topItems = sorted.slice(0, 5)
    const others = sorted.slice(5)

    const chartData = topItems.map((item) => ({
      name: item.subnovedad,
      value: item.cantidad
    }))

    if (others.length > 0) {
      const othersCount = others.reduce((sum, item) => sum + item.cantidad, 0)
      chartData.push({
        name: 'OTROS',
        value: othersCount
      })
    }

    setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' },
        formatter: '{b}: <b>{c}</b> ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 0,
        textStyle: { color: '#94a3b8', fontSize: 9 }
      },
      series: [
        {
          name: 'Distribución',
          type: 'pie',
          radius: ['35%', '60%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 6,
            borderColor: '#151d30',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold',
              color: '#f1f5f9'
            }
          },
          labelLine: {
            show: false
          },
          data: chartData,
          color: ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#6366f1', '#a855f7']
        }
      ]
    })
  } catch (error) {
    console.error('Error cargando gráfico de distribución:', error)
  }
}

watch(() => [props.month, props.day], () => {
  renderChart()
})

onMounted(() => {
  renderChart()
})
</script>
