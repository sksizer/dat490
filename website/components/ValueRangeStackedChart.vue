<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent
} from 'echarts/components'
import { SVGRenderer } from 'echarts/renderers'

// Register the required components
use([
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  ToolboxComponent,
  SVGRenderer
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
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Value Distribution by Feature'
})

// Process data to create stacked chart structure
const chartData = computed(() => {
  const features = []
  const valueCategories = new Set<string>()
  const valueDetails = new Map<string, { value: string, description: string }>()
  
  // First pass: collect all unique value categories and process features
  for (const column of props.data) {
    if (!column.value_ranges || column.value_ranges.length === 0) continue
    
    const featureData = {
      key: column.key,
      label: column.label || column.key,
      values: new Map<string, number>(),
      valueDetails: new Map<string, { value: string, description: string }>(),
      totalCount: 0
    }
    
    for (const valueItem of column.value_ranges) {
      if ('count' in valueItem && valueItem.count > 0) {
        // Create a category name from the description (truncated)
        const categoryName = valueItem.description.length > 20 
          ? valueItem.description.substring(0, 20) + '...'
          : valueItem.description
        
        // Store the original value and full description
        const originalValue = 'start' in valueItem 
          ? (valueItem.start === valueItem.end ? valueItem.start.toString() : `${valueItem.start}-${valueItem.end}`)
          : 'N/A'
        
        valueCategories.add(categoryName)
        valueDetails.set(categoryName, { value: originalValue, description: valueItem.description })
        featureData.values.set(categoryName, valueItem.count)
        featureData.valueDetails.set(categoryName, { value: originalValue, description: valueItem.description })
        featureData.totalCount += valueItem.count
      }
    }
    
    if (featureData.totalCount > 0) {
      features.push(featureData)
    }
  }
  
  // Sort features by total count (descending)
  features.sort((a, b) => b.totalCount - a.totalCount)
  
  return {
    features: features.slice(0, 50), // Limit to top 50 features for performance
    categories: Array.from(valueCategories).sort(),
    valueDetails
  }
})

// Generate colors for different value categories
const generateColors = (count: number) => {
  const colors = [
    '#1e40af', '#dc2626', '#059669', '#d97706', '#7c3aed',
    '#db2777', '#0891b2', '#65a30d', '#c2410c', '#9333ea',
    '#be185d', '#0284c7', '#84cc16', '#ea580c', '#a855f7',
    '#be123c', '#0369a1', '#a3e635', '#f97316', '#8b5cf6',
    '#9f1239', '#075985', '#bef264', '#fb923c', '#7c2d12'
  ]
  
  const result = []
  for (let i = 0; i < count; i++) {
    result.push(colors[i % colors.length])
  }
  return result
}

// ECharts configuration
const chartOption = computed<EChartsOption>(() => {
  const { features, categories } = chartData.value
  const colors = generateColors(categories.length)
  
  return {
    title: {
      text: `${props.title} (Top ${features.length} features)`,
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
        if (!Array.isArray(params)) return ''
        
        const featureIndex = params[0].dataIndex
        const feature = features[featureIndex]
        
        let tooltip = `
          <div style="font-size: 12px; max-width: 300px;">
            <div style="font-weight: bold; margin-bottom: 4px; color: #1e40af;">
              ${feature.key}
            </div>
            <div style="margin-bottom: 6px; line-height: 1.4;">
              ${feature.label}
            </div>
            <div style="margin-bottom: 4px; font-weight: bold;">
              Total: ${feature.totalCount.toLocaleString()}
            </div>
            <div style="border-top: 1px solid #e5e7eb; padding-top: 4px;">
        `
        
        // Show value breakdown
        params.forEach((param: any) => {
          if (param.value > 0) {
            const percentage = ((param.value / feature.totalCount) * 100).toFixed(1)
            const valueDetail = feature.valueDetails.get(param.seriesName)
            const valueDisplay = valueDetail ? valueDetail.value : 'N/A'
            const fullDescription = valueDetail ? valueDetail.description : param.seriesName
            
            tooltip += `
              <div style="margin: 2px 0; display: flex; align-items: center;">
                <div style="width: 12px; height: 12px; background-color: ${param.color}; margin-right: 6px; border-radius: 2px;"></div>
                <span style="font-size: 11px;">
                  <strong>${valueDisplay}</strong>: ${fullDescription}<br/>
                  <span style="color: #059669; font-weight: bold; margin-left: 18px;">
                    ${param.value.toLocaleString()} (${percentage}%)
                  </span>
                </span>
              </div>
            `
          }
        })
        
        tooltip += `</div></div>`
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
      right: 15,
      top: 10
    },
    legend: {
      type: 'scroll',
      bottom: 10,
      data: categories,
      textStyle: {
        fontSize: 10
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '25%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: features.map(f => f.key),
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
    series: categories.map((category, index) => ({
      name: category,
      type: 'bar',
      stack: 'total',
      data: features.map(feature => feature.values.get(category) || 0),
      itemStyle: {
        color: colors[index]
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      }
    }))
  }
})

// Fixed chart height
const chartHeight = 400
</script>

<template>
  <div v-if="chartData.features.length > 0" class="w-full">
    <VChart 
      :option="chartOption" 
      :init-options="{ 
        width: 'auto', 
        height: chartHeight 
      }"
      autoresize
      :style="{ height: `${chartHeight}px` }"
    />
  </div>
  <div v-else class="text-center py-8 text-gray-500 text-sm">
    No value range data available for visualization
  </div>
</template>