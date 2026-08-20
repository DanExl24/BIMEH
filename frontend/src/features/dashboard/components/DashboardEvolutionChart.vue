<template>
  <div class="glass-panel p-4 sm:p-6 rounded-2xl flex flex-col h-[340px] sm:h-[420px] relative overflow-hidden">
    <div class="flex items-center justify-between gap-2 mb-3">
      <div class="flex items-center gap-2">
        <span class="w-2 h-4 bg-cyan-400 rounded-xs shadow-sm shadow-cyan-400/50"></span>
        <h3 class="text-xs sm:text-sm font-bold text-slate-100 uppercase tracking-wider">
          Evolución de Disponibilidad Diaria {{ month ? `(${month})` : '(Anual)' }}
        </h3>
      </div>

      <!-- Tactical Status Legend Tags -->
      <div class="hidden sm:flex items-center gap-2 text-[10px] font-mono">
        <span class="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">
          ≥80% ÓPTIMO
        </span>
        <span class="px-2 py-0.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 font-bold">
          &lt;60% ALERTA
        </span>
      </div>
    </div>

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
        axisPointer: {
          type: 'cross',
          lineStyle: { color: 'rgba(6, 182, 212, 0.6)', width: 1, type: 'dashed' },
          crossStyle: { color: 'rgba(6, 182, 212, 0.4)' }
        },
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(6, 182, 212, 0.4)',
        borderWidth: 1.5,
        padding: [10, 14],
        textStyle: { color: '#f1f5f9', fontFamily: 'monospace' },
        formatter: (params: any) => {
          const arr = Array.isArray(params) ? params : [params]
          if (!arr || !arr.length) return ''
          const axisVal = arr[0]?.axisValue || ''
          const dispoItem = arr.find((p: any) => p.seriesName === 'Disponibilidad %')
          const dispoVal = dispoItem ? dispoItem.value : 0
          const persItem = arr.find((p: any) => p.seriesName === 'Personal Disponible')
          const persVal = persItem ? persItem.value : 0

          const statusColor = dispoVal >= 80 ? '#34d399' : (dispoVal >= 60 ? '#fbbf24' : '#f87171')
          const statusText = dispoVal >= 80 ? 'ÓPTIMO' : (dispoVal >= 60 ? 'MEDIO' : 'CRÍTICO')

          return `
            <div class="space-y-1.5 min-w-[170px] text-xs select-none">
              <div class="flex items-center justify-between pb-1 border-b border-slate-700/80 font-bold">
                <span class="text-slate-300 font-mono tracking-wider">${axisVal}</span>
                <span style="color:${statusColor}" class="px-1.5 py-0.2 rounded text-[10px] bg-slate-800 font-black border border-slate-700">${statusText}</span>
              </div>
              <div class="flex items-center justify-between pt-1">
                <span class="text-cyan-400 font-medium">Disponibilidad:</span>
                <strong class="text-cyan-300 font-bold font-mono">${dispoVal}%</strong>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-emerald-400 font-medium">Efectivos Disp.:</span>
                <strong class="text-slate-100 font-bold font-mono">${persVal} Pers.</strong>
              </div>
            </div>
          `
        }
      },
      legend: {
        data: ['Disponibilidad %', 'Personal Disponible'],
        textStyle: { color: '#94a3b8', fontSize: 11 },
        bottom: 2,
        icon: 'rect',
        itemWidth: 12,
        itemHeight: 4
      },
      grid: { 
        top: '14%', 
        right: '4%', 
        bottom: '12%', 
        left: '2%', 
        containLabel: true 
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: true,
        axisLine: { lineStyle: { color: '#1e293b' } },
        axisTick: { alignWithLabel: true, lineStyle: { color: '#334155' } },
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
          name: 'DISP. %',
          nameTextStyle: { color: '#64748b', fontSize: 9, align: 'right', padding: [0, 6, 0, 0] },
          min: 0,
          max: 100,
          axisLabel: { color: '#64748b', fontSize: 10, formatter: '{value}%' },
          splitLine: { 
            lineStyle: { color: 'rgba(30, 41, 59, 0.7)', type: 'dashed' } 
          }
        },
        {
          type: 'value',
          name: 'EFECTIVOS',
          nameTextStyle: { color: '#64748b', fontSize: 9, align: 'left', padding: [0, 0, 0, 6] },
          axisLabel: { color: '#64748b', fontSize: 10 },
          splitLine: { show: false }
        }
      ],
      series: [
        // 1. Barras Columnar Tácticas de Fondo (Personal Disponible)
        {
          name: 'Personal Disponible',
          type: 'bar',
          yAxisIndex: 1,
          data: disponibles,
          barWidth: 12,
          itemStyle: { 
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(16, 185, 129, 0.45)' },
              { offset: 0.8, color: 'rgba(16, 185, 129, 0.12)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.02)' }
            ]),
            borderRadius: [2, 2, 0, 0],
            borderColor: 'rgba(16, 185, 129, 0.6)',
            borderWidth: 1
          },
          z: 1
        },
        // 2. Línea Neón Angular de Disponibilidad (%)
        {
          name: 'Disponibilidad %',
          type: 'line',
          data: disponibilidades,
          smooth: false, // Trazo angular y nítido militar
          step: false,
          symbol: 'diamond',
          symbolSize: 7,
          lineStyle: { 
            width: 3, 
            color: '#06b6d4',
            shadowColor: 'rgba(6, 182, 212, 0.75)',
            shadowBlur: 14
          },
          itemStyle: { 
            color: '#06b6d4', 
            borderWidth: 1.5, 
            borderColor: '#ffffff',
            shadowColor: 'rgba(6, 182, 212, 0.9)',
            shadowBlur: 8
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(6, 182, 212, 0.32)' },
              { offset: 0.7, color: 'rgba(6, 182, 212, 0.06)' },
              { offset: 1, color: 'rgba(6, 182, 212, 0.0)' }
            ])
          },
          z: 3,
          // Líneas de umbral táctico operativo
          markLine: {
            silent: true,
            symbol: ['none', 'none'],
            data: [
              {
                yAxis: 80,
                lineStyle: { color: 'rgba(52, 211, 153, 0.65)', type: 'dashed', width: 1.2 },
                label: {
                  show: true,
                  position: 'insideEndTop',
                  formatter: '80% ÓPTIMO',
                  color: '#34d399',
                  fontSize: 9,
                  fontFamily: 'monospace',
                  padding: [0, 4, 2, 0]
                }
              },
              {
                yAxis: 60,
                lineStyle: { color: 'rgba(251, 191, 36, 0.65)', type: 'dashed', width: 1.2 },
                label: {
                  show: true,
                  position: 'insideEndBottom',
                  formatter: '60% ALERTA',
                  color: '#fbbf24',
                  fontSize: 9,
                  fontFamily: 'monospace',
                  padding: [2, 4, 0, 0]
                }
              }
            ]
          },
          // Marcadores pico Máx / Mín
          markPoint: {
            symbol: 'pin',
            symbolSize: 36,
            data: [
              {
                type: 'max',
                name: 'Máximo',
                itemStyle: { color: '#06b6d4', shadowColor: 'rgba(6, 182, 212, 0.8)', shadowBlur: 10 },
                label: { color: '#0f172a', fontWeight: 'bold', fontSize: 9 }
              },
              {
                type: 'min',
                name: 'Mínimo',
                itemStyle: { color: '#f59e0b', shadowColor: 'rgba(245, 158, 11, 0.8)', shadowBlur: 10 },
                label: { color: '#0f172a', fontWeight: 'bold', fontSize: 9 }
              }
            ]
          }
        }
      ]
    })
  } catch (error) {
    console.error('Error cargando gráfico de evolución táctico:', error)
  }
}

watch(() => [props.month, props.day], () => {
  renderChart()
})

onMounted(() => {
  renderChart()
})
</script>
