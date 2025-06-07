<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'

// Register the required components
use([
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  SVGRenderer
])

interface ValueData {
  value: string
  count: number | string
  description: string
}

interface Props {
  valueData: ValueData[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Response Counts'
})

// Filter and prepare data for the chart
const chartData = computed(() => {
  return props.valueData
    .filter(item => typeof item.count === 'number' && item.count > 0)
    .map(item => ({
      value: item.value,
      count: item.count as number,
      description: item.description
    }))
})

// Truncate long descriptions for x-axis labels
const truncateLabel = (text: string, maxLength: number = 15) => {
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// ECharts configuration
const chartOption = computed<EChartsOption>(() => ({
  title: {
    text: props.title,
    textStyle: {
      fontSize: 14,
      fontWeight: 'normal',
      color: '#374151' // gray-700
    },
    left: 'center',
    top: 10
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: (params: any) => {
      const data = Array.isArray(params) ? params[0] : params
      const originalItem = chartData.value[data.dataIndex]
      return `
        <div style="font-size: 12px; max-width: 250px;">
          <div style="font-weight: bold; margin-bottom: 4px; color: #1e40af;">
            Value: ${originalItem.value}
          </div>
          <div style="margin-bottom: 6px; line-height: 1.4;">
            ${originalItem.description}
          </div>
          <div style="color: #059669; font-weight: bold;">
            Count: ${data.value.toLocaleString()}
          </div>
        </div>
      `
    }
  },
  grid: {
    left: '10%',
    right: '10%',
    bottom: '20%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.value.map(item => item.value),
    axisLabel: {
      fontSize: 10,
      color: '#6b7280', // gray-500
      interval: 0,
      rotate: chartData.value.length > 5 ? 45 : 0
    },
    axisTick: {
      show: false
    },
    axisLine: {
      lineStyle: {
        color: '#e5e7eb' // gray-200
      }
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      fontSize: 10,
      color: '#6b7280', // gray-500
      formatter: (value: number) => value.toLocaleString()
    },
    axisTick: {
      show: false
    },
    axisLine: {
      show: false
    },
    splitLine: {
      lineStyle: {
        color: '#f3f4f6' // gray-100
      }
    }
  },
  series: [{
    type: 'bar',
    data: chartData.value.map(item => item.count),
    itemStyle: {
      color: '#1e40af', // blue-800
      borderRadius: [2, 2, 0, 0]
    },
    emphasis: {
      itemStyle: {
        color: '#1e3a8a' // blue-900
      }
    },
    label: {
      show: true,
      position: 'top',
      fontSize: 10,
      color: '#1e40af',
      formatter: (params: any) => params.value.toLocaleString()
    }
  }, {
    type: 'bar',
    data: chartData.value.map(() => 0), // Invisible series for description labels
    itemStyle: {
      color: 'transparent'
    },
    label: {
      show: true,
      position: 'inside',
      fontSize: 9,
      color: '#ffffff',
      fontWeight: 'bold',
      formatter: (params: any) => {
        const item = chartData.value[params.dataIndex]
        return truncateLabel(item.description, 20)
      }
    },
    tooltip: {
      show: false
    },
    silent: true
  }]
}))

// Chart height based on number of items
const chartHeight = computed(() => {
  const baseHeight = 300
  const itemCount = chartData.value.length
  return Math.max(baseHeight, Math.min(500, baseHeight + (itemCount * 10)))
})
</script>

<template>
  <div v-if="chartData.length > 0" class="w-full">
    <VChart 
      :option="chartOption" 
      :init-options="{ 
        width: 'auto', 
        height: chartHeight 
      }"
      autoresize
      :style="{ height: `${chartHeight}px`, minHeight: '300px' }"
    />
  </div>
  <div v-else class="text-center py-8 text-gray-500 text-sm">
    No response data available for visualization
  </div>
</template>