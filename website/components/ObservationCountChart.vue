<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  ToolboxComponent
} from 'echarts/components'
import { SVGRenderer, CanvasRenderer } from 'echarts/renderers'

// Register the required components
use([
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  ToolboxComponent,
  SVGRenderer,
  CanvasRenderer
])

interface ValueRange {
  start: number
  end: number
  count: number
  description: string
}

interface ValueDef {
  description: string
}

interface ColumnData {
  key: string
  label?: string
  value_ranges?: (ValueRange | ValueDef)[]
  statistics?: {
    count: number
  }
}

interface Props {
  data: ColumnData[]
  title?: string
  filterZeroCounts?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Observation Counts by Feature',
  filterZeroCounts: true
})

// Renderer toggle state - default to Canvas
const useCanvasRenderer = ref(true)

// Prepare chart data from the sorted and filtered column data
const chartData = computed(() => {
  let filteredData = props.data
  
  // Only filter out zero counts if explicitly requested
  if (props.filterZeroCounts) {
    filteredData = filteredData.filter(item => item.statistics?.count && item.statistics.count > 0)
  }
  
  return filteredData
    .filter(item => item.statistics?.count != null) // Ensure statistics and count exist
    .map(item => {
      // Process value ranges for tooltip
      const valueRanges = []
      if (item.value_ranges) {
        for (const valueItem of item.value_ranges) {
          if ('count' in valueItem && valueItem.count > 0) {
            const value = 'start' in valueItem 
              ? (valueItem.start === valueItem.end ? valueItem.start.toString() : `${valueItem.start}-${valueItem.end}`)
              : 'N/A'
            
            valueRanges.push({
              value,
              count: valueItem.count,
              description: valueItem.description
            })
          }
        }
      }
      
      // Sort value ranges by count descending
      valueRanges.sort((a, b) => b.count - a.count)
      
      return {
        key: item.key,
        label: item.label || item.key,
        count: item.statistics.count,
        valueRanges
      }
    })
})

// Handle bar click to navigate to column details
const handleBarClick = (params: any) => {
  if (params.componentType === 'series') {
    const item = chartData.value[params.dataIndex]
    if (item) {
      // Navigate to column details page using the key or sas_variable_name
      const columnId = item.key
      const url = `/columns/${columnId}`
      window.open(url, '_blank')
    }
  }
}

// Calculate bar width and spacing based on available space
const barSettings = computed(() => {
  const featureCount = chartData.value.length
  if (featureCount === 0) return { barWidth: 'auto', barGap: '20%', debug: 'no-features' }
  
  // Estimate available chart width (rough calculation)
  // Chart container is roughly 70% of window width after containers/padding
  const estimatedChartWidth = typeof window !== 'undefined' ? window.innerWidth * 0.7 : 1000
  const availableBarSpace = estimatedChartWidth * 0.85 // Account for y-axis and padding
  
  // Calculate pixels per bar if we used all available space
  const pixelsPerBar = availableBarSpace / featureCount
  
  // Debug info
  const debugInfo = {
    featureCount,
    windowWidth: typeof window !== 'undefined' ? window.innerWidth : 'SSR',
    estimatedChartWidth,
    availableBarSpace,
    pixelsPerBar: pixelsPerBar.toFixed(2)
  }
  
  // Much more aggressive thresholds for dense data
  if (pixelsPerBar < 1) {
    console.log('Bar spacing: 0% gap (ultra-dense)', debugInfo)
    return { barWidth: 1, barGap: '0%', debug: debugInfo }
  }
  else if (pixelsPerBar < 2) {
    console.log('Bar spacing: 0% gap (very dense)', debugInfo)
    return { barWidth: 'auto', barGap: '0%', debug: debugInfo }
  }
  else if (pixelsPerBar < 4) {
    console.log('Bar spacing: 0% gap (dense)', debugInfo)
    return { barWidth: 'auto', barGap: '0%', debug: debugInfo }
  }
  else if (pixelsPerBar < 8) {
    console.log('Bar spacing: 5% gap (medium)', debugInfo)
    return { barWidth: 'auto', barGap: '5%', debug: debugInfo }
  }
  else if (pixelsPerBar < 15) {
    console.log('Bar spacing: 10% gap (sparse)', debugInfo)
    return { barWidth: 'auto', barGap: '10%', debug: debugInfo }
  }
  else {
    console.log('Bar spacing: 20% gap (very sparse)', debugInfo)
    return { barWidth: 'auto', barGap: '20%', debug: debugInfo }
  }
})

// ECharts configuration
const chartOption = computed<EChartsOption>(() => ({
  title: {
    text: `${props.title} (${chartData.value.length} features) • Click any bar to view feature details`,
    textStyle: {
      fontSize: 14,
      fontWeight: 'normal',
      color: '#374151' // gray-700
    },
    left: 10,
    top: 10
  },
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'shadow'
    },
    formatter: (params: any) => {
      const data = params[0]
      const originalItem = chartData.value[data.dataIndex]
      
      let tooltip = `
        <div style="font-size: 12px; max-width: 300px;">
          <div style="font-weight: bold; margin-bottom: 4px; color: #1e40af;">
            ${originalItem.key}
          </div>
          <div style="margin-bottom: 6px; line-height: 1.4;">
            ${originalItem.label}
          </div>
          <div style="color: #059669; font-weight: bold; margin-bottom: 6px;">
            Total Count: ${data.value.toLocaleString()}
          </div>
      `
      
      // Add value ranges if available
      if (originalItem.valueRanges && originalItem.valueRanges.length > 0) {
        tooltip += `
          <div style="border-top: 1px solid #e5e7eb; padding-top: 6px;">
            <div style="font-weight: bold; margin-bottom: 4px; color: #374151; font-size: 11px;">
              Value Breakdown:
            </div>
        `
        
        // Show top 5 value ranges to avoid overwhelming the tooltip
        const topRanges = originalItem.valueRanges.slice(0, 5)
        topRanges.forEach((range: any) => {
          const percentage = ((range.count / originalItem.count) * 100).toFixed(1)
          // Truncate description to 80 characters
          const truncatedDescription = range.description.length > 80 
            ? range.description.substring(0, 80) + '...'
            : range.description
          
          tooltip += `
            <div style="margin: 2px 0; font-size: 11px; line-height: 1.3;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <span style="font-weight: bold; color: #1e40af; margin-right: 8px;">
                  ${range.value}:
                </span>
                <span style="color: #059669; font-weight: bold;">
                  ${range.count.toLocaleString()} (${percentage}%)
                </span>
              </div>
              <div style="color: #6b7280; margin-left: 0px; margin-top: 1px;">
                ${truncatedDescription}
              </div>
            </div>
          `
        })
        
        // Show indication if there are more ranges
        if (originalItem.valueRanges.length > 5) {
          tooltip += `
            <div style="font-size: 10px; color: #9ca3af; margin-top: 4px; font-style: italic;">
              ... and ${originalItem.valueRanges.length - 5} more values
            </div>
          `
        }
        
        tooltip += `</div>`
      }
      
      tooltip += `</div>`
      return tooltip
    }
  },
  toolbox: {
    feature: {
      saveAsImage: {
        pixelRatio: 2,
        title: 'Save as Image'
      }
    },
    right: 120,
    top: 10
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '15%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: chartData.value.map(item => item.key),
    axisLabel: {
      show: false
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
    barWidth: barSettings.value.barWidth,
    barGap: barSettings.value.barGap,
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
      show: false
    },
    // Set `large` for performance with many data points
    large: chartData.value.length > 100,
    // Make bars clickable with pointer cursor
    cursor: 'pointer'
  }]
}))

// Fixed chart height - let y-axis scale handle data range
const chartHeight = 400
</script>

<template>
  <div class="w-full relative" :style="{ height: `${chartHeight}px` }">
    <!-- Renderer Toggle positioned inline with chart title -->
    <div v-if="chartData.length > 0" class="absolute top-2 right-3 z-10">
      <div class="flex items-center gap-1">
        <span class="text-xs text-gray-500">SVG</span>
        <USwitch v-model="useCanvasRenderer" size="xs" />
        <span class="text-xs text-gray-500">Canvas</span>
      </div>
    </div>
    
    <VChart 
      v-if="chartData.length > 0"
      :key="useCanvasRenderer ? 'canvas' : 'svg'"
      :option="chartOption" 
      :init-options="{ 
        width: 'auto', 
        height: chartHeight,
        renderer: useCanvasRenderer ? 'canvas' : 'svg'
      }"
      autoresize
      :style="{ height: `${chartHeight}px` }"
      @click="handleBarClick"
    />
    <div 
      v-else 
      class="flex items-center justify-center text-gray-500 text-sm"
      :style="{ height: `${chartHeight}px` }"
    >
      No features match current filters
    </div>
  </div>
</template>