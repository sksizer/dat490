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

// Include all table rows in chart - even with zero counts
const chartData = computed(() => {
  return props.valueData.map(item => ({
    value: item.value,
    count: typeof item.count === 'number' ? item.count : 0,
    description: item.description,
    indicates_missing: item.indicates_missing || false
  }))
  // Keep the same order as the table (by value order, not count)
})

// Truncate long descriptions for better display
const truncateDescription = (text: string, maxLength: number = 50) => {
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

// Define emits
const emit = defineEmits<{
  highlightValue: [value: string | null]
}>()

// ECharts configuration
const chartOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: (params: any) => {
      const data = Array.isArray(params) ? params[0] : params
      const originalItem = chartData.value[data.dataIndex]
      const isMissing = originalItem.indicates_missing
      const titleColor = isMissing ? '#dc2626' : '#1e40af' // red-600 for missing, blue-800 for normal
      const countColor = isMissing ? '#dc2626' : '#059669' // red-600 for missing, green-600 for normal
      
      return `
        <div style="font-size: 12px; max-width: 250px;">
          <div style="font-weight: bold; margin-bottom: 4px; color: ${titleColor};">
            Value: ${originalItem.value}
          </div>
          <div style="margin-bottom: 6px; line-height: 1.4;">
            ${originalItem.description}
          </div>
          <div style="color: ${countColor}; font-weight: bold;">
            Count: ${data.value.toLocaleString()}
          </div>
        </div>
      `
    }
  },
  grid: {
    left: '3%',
    right: '8%',
    bottom: '3%',
    top: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'value',
    axisLabel: {
      fontSize: 9,
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
  yAxis: {
    type: 'category',
    data: chartData.value.map(item => item.value),
    axisLabel: {
      fontSize: 9,
      color: '#6b7280', // gray-500
      width: 180,
      overflow: 'truncate'
    },
    axisTick: {
      show: false
    },
    axisLine: {
      lineStyle: {
        color: '#e5e7eb' // gray-200
      }
    },
    inverse: true // Reverse order to match table (first value at top)
  },
  series: [{
    type: 'bar',
    data: chartData.value.map(item => ({
      value: item.count,
      itemStyle: {
        color: item.indicates_missing ? '#fecaca' : '#1e40af', // red-200 for missing, blue-800 for normal
        borderRadius: [0, 2, 2, 0]
      },
      emphasis: {
        itemStyle: {
          color: item.indicates_missing ? '#dc2626' : '#1e3a8a' // red-600 for missing hover, blue-900 for normal hover
        }
      }
    })),
    label: {
      show: true,
      position: 'right',
      fontSize: 9,
      color: (params: any) => {
        const item = chartData.value[params.dataIndex]
        return item?.indicates_missing ? '#dc2626' : '#1e40af' // red-600 for missing, blue-800 for normal
      },
      fontWeight: 'bold',
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
      fontSize: 8,
      color: '#ffffff',
      fontWeight: 'bold',
      formatter: (params: any) => {
        const item = chartData.value[params.dataIndex]
        return truncateDescription(item.description, 25)
      }
    },
    tooltip: {
      show: false
    },
    silent: true
  }]
}))

// Chart height - calculate based on number of rows to match table
const chartHeight = computed(() => {
  const itemCount = props.valueData.length
  const rowHeight = 28 // Height per row to align with table rows
  const headerHeight = 40 // Space for axes
  const minHeight = 200 // Reasonable minimum
  const maxHeight = 600 // Maximum height limit
  
  const calculatedHeight = headerHeight + (itemCount * rowHeight)
  return Math.max(minHeight, Math.min(maxHeight, calculatedHeight))
})

// Chart event handlers
const onChartHover = (params: any) => {
  if (params.dataIndex !== undefined) {
    const item = chartData.value[params.dataIndex]
    emit('highlightValue', item.value)
  }
}

const onChartLeave = () => {
  emit('highlightValue', null)
}
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
      :style="{ height: `${chartHeight}px`, width: '100%' }"
      @mouseover="onChartHover"
      @mouseout="onChartLeave"
    />
  </div>
  <div v-else class="text-center py-8 text-gray-500 text-sm">
    No response data available for visualization
  </div>
</template>