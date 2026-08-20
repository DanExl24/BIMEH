import { ref, onMounted, onBeforeUnmount, shallowRef, type Ref } from 'vue'
import * as echarts from 'echarts'

export interface UseEChartsOptions {
  autoResize?: boolean
}

export function useECharts(options: UseEChartsOptions = { autoResize: true }) {
  const chartDom: Ref<HTMLDivElement | null> = ref(null)
  const chartInstance = shallowRef<echarts.ECharts | null>(null)

  const initChart = (): echarts.ECharts | null => {
    if (!chartDom.value) return null
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }
    const instance = echarts.init(chartDom.value)
    chartInstance.value = instance
    return instance
  }

  const setOption = (option: echarts.EChartsOption, notMerge?: boolean) => {
    if (!chartInstance.value) {
      initChart()
    }
    chartInstance.value?.setOption(option, notMerge)
  }

  const resize = () => {
    chartInstance.value?.resize()
  }

  const dispose = () => {
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
    }
  }

  const handleResize = () => {
    resize()
  }

  onMounted(() => {
    if (options.autoResize) {
      window.addEventListener('resize', handleResize)
    }
  })

  onBeforeUnmount(() => {
    if (options.autoResize) {
      window.removeEventListener('resize', handleResize)
    }
    dispose()
  })

  return {
    chartDom,
    chartInstance,
    initChart,
    setOption,
    resize,
    dispose
  }
}
