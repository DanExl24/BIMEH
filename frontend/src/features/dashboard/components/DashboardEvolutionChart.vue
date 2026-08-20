<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[340px] sm:h-[420px]">
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
    const disponibilidades = data.map((d: { disponibilidad: number }) => d.disponibilidad)
    const disponibles = data.map((d: { disponibles: number }) => d.disponibles)

    setOption({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'line', lineStyle: { color: '#06b6d4', width: 1, type: 'dashed' } },
        backgroundColor: '#151d30',
        borderColor: '#1f2b45',
        textStyle: { color: '#f1f5f9' },
        formatter: (params: any[]) => {
          if (!params || !params.length) return ''
          const header = `<div class="font-mono text-xs font-bold text-slate-300 pb-1 border-b border-slate-700">${params[0].axisValue}</div>`
          const items = params.map(p => {
            const val = p.seriesName.includes('%') ? `${p.value}%` : `${p.value} Efectivos`
            return `<div class="flex items-center justify-between gap-4 text-xs pt-1">
              <span class="flex items-center gap-1.5"><span style="background:${p.color}" class="w-2 h-2 rounded-full inline-block"></span>${p.seriesName}</span>
              <strong class="font-mono font-bold text-slate-100">${val}</strong>
            </div>`
          }).join('')
          return header + items
        }
      },
      legend: {
        data: ['Disponibilidad %', 'Personal Disponible'],
        textStyle: { color: '#94a3b8', fontSize: 11 },
        bottom: 0
      },
      grid: { 
        top: '10%', 
        right: '4%', 
        bottom: '12%', 
        left: '2%', 
        containLabel: true 
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#1f2b45' } },
        axisLabel: {
          color: '#64748b',
          fontSize: 10,
          formatter: (value: string) => {
            const parts = value.split('-')
            return parts.length === 3 ? `${parts[2]}/${parts[1]}` : value
          }
        },
        splitLine: { show: false }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Disp. %',
          min: 0,
          max: 100,
          axisLabel: { color: '#64748b', fontSize: 10, formatter: '{value}%' },
          splitLine: { lineStyle: { color: '#1f2b45', type: 'dashed' } }
        },
        {
          type: 'value',
          name: 'Efectivos',
          axisLabel: { color: '#64748b', fontSize: 10 },
          splitLine: { show: false }
        }
      ],
      series: [
        {
          name: 'Disponibilidad %',
          type: 'line',
          data: disponibilidades,
          smooth: true,
          lineStyle: { width: 3.5, color: '#06b6d4' },
          itemStyle: { color: '#06b6d4', borderWidth: 2, borderColor: '#fff' },
          symbolSize: 6,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(6, 182, 212, 0.35)' },
              { offset: 0.8, color: 'rgba(6, 182, 212, 0.05)' },
              { offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
            ])
          }
        },
        {
          name: 'Personal Disponible',
          type: 'bar',
          yAxisIndex: 1,
          data: disponibles,
          itemStyle: { 
            color: 'rgba(16, 185, 129, 0.25)',
            borderRadius: [4, 4, 0, 0],
            borderColor: 'rgba(16, 185, 129, 0.4)',
            borderWidth: 1
          },
          barMaxWidth: 28
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
