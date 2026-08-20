<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[340px] sm:h-[420px]">
    <h3 class="text-xs sm:text-sm font-bold text-slate-200 mb-3 uppercase tracking-wider flex items-center gap-2">
      <span class="w-2 h-4 bg-cyan-500 rounded-sm"></span> Evolución de Disponibilidad Diaria
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
    const data = await dashboardService.getEvolucion(props.month, props.day)
    const dates = data.map((d: { fecha: string }) => d.fecha)
    const pct = data.map((d: { disponibilidad_pct: number }) => d.disponibilidad_pct)
    const disponibles = data.map((d: { disponibles: number }) => d.disponibles)
    const novedades = data.map((d: { novedades: number }) => d.novedades)

    setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' },
        axisPointer: { type: 'cross', label: { backgroundColor: '#1f2b45' } }
      },
      legend: {
        data: ['Disponibilidad %', 'Disponibles', 'En Novedad'],
        textStyle: { color: '#94a3b8', fontSize: 10 },
        bottom: 0
      },
      grid: {
        top: '10%',
        left: '2%',
        right: '4%',
        bottom: '12%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#1f2b45' } },
        axisLabel: {
          color: '#64748b',
          fontSize: 9,
          formatter: (value: string) => {
            const parts = value.split('-')
            return parts.length === 3 ? `${parts[2]}/${parts[1]}` : value
          }
        }
      },
      yAxis: [
        {
          type: 'value',
          name: '%',
          min: 0,
          max: 100,
          axisLabel: { color: '#64748b', fontSize: 9 },
          splitLine: { lineStyle: { color: '#1f2b45', type: 'dashed' } }
        },
        {
          type: 'value',
          name: 'Pers.',
          axisLabel: { color: '#64748b', fontSize: 9 },
          splitLine: { show: false }
        }
      ],
      series: [
        {
          name: 'Disponibilidad %',
          type: 'line',
          smooth: true,
          data: pct,
          itemStyle: { color: '#06b6d4' },
          lineStyle: { width: 3 },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(6, 182, 212, 0.3)' },
                { offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
              ]
            }
          }
        },
        {
          name: 'Disponibles',
          type: 'bar',
          stack: 'Total',
          yAxisIndex: 1,
          data: disponibles,
          itemStyle: { color: '#10b981' }
        },
        {
          name: 'En Novedad',
          type: 'bar',
          stack: 'Total',
          yAxisIndex: 1,
          data: novedades,
          itemStyle: { color: '#f59e0b' }
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
