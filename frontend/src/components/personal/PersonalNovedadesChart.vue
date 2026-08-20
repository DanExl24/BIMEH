<template>
  <div class="glass-panel p-6 rounded-2xl flex flex-col h-[400px] min-w-0 max-w-full overflow-hidden">
    <h3 class="text-sm font-bold text-slate-200 mb-4 uppercase tracking-wider flex items-center gap-2">
      <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Distribución de Novedades {{ filterSubtitle }}
    </h3>
    <div class="flex-1 min-h-0">
      <div ref="chartDom" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useECharts } from '../../composables/useECharts'
import type { HistorialRegistro } from '../../types'

const props = defineProps<{
  filteredHistorial: HistorialRegistro[]
  filterSubtitle: string
  selectedSubnovedad: string
}>()

const emit = defineEmits<{
  (e: 'update:selectedSubnovedad', val: string): void
}>()

const { chartDom, setOption, chartInstance } = useECharts()

const renderChart = () => {
  if (!chartDom.value) return
  try {
    const counts: Record<string, number> = {}
    props.filteredHistorial.forEach(item => {
      if (item.subnovedad) {
        counts[item.subnovedad] = (counts[item.subnovedad] || 0) + 1
      }
    })

    const chartData = Object.entries(counts)
      .map(([subnovedad, dias]) => ({
        name: subnovedad,
        value: dias
      }))
      .sort((a, b) => b.value - a.value)

    if (chartData.length === 0) {
      setOption({
        backgroundColor: 'transparent',
        title: {
          text: 'Sin registros para el filtro',
          left: 'center',
          top: 'center',
          textStyle: { color: '#64748b', fontSize: 12, fontWeight: 'normal' }
        }
      })
      return
    }

    setOption({
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
          roseType: 'area',
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

    // Click handler to filter by clicked subnovedad
    if (chartInstance.value) {
      chartInstance.value.off('click')
      chartInstance.value.on('click', (params: { name?: string }) => {
        if (params.name) {
          if (props.selectedSubnovedad === params.name) {
            emit('update:selectedSubnovedad', '')
          } else {
            emit('update:selectedSubnovedad', params.name)
          }
        }
      })
    }
  } catch (error) {
    console.error('Error generando gráfico acumulado de personal:', error)
  }
}

watch(() => [props.filteredHistorial, props.selectedSubnovedad], () => {
  renderChart()
})

onMounted(() => {
  renderChart()
})
</script>
