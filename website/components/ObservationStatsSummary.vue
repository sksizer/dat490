<script setup lang="ts">
interface ColumnStatistics {
  count: number
  missing_count: number
  null_count: number
  total_responses: number
}

interface ColumnData {
  key: string
  label?: string
  statistics?: ColumnStatistics
}

interface Props {
  data: ColumnData[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Data Completeness Analysis'
})

// Calculate aggregated statistics
const statsAnalysis = computed(() => {
  const validColumns = props.data.filter(item => item.statistics)
  
  if (validColumns.length === 0) {
    return null
  }
  
  // Calculate totals
  const totalValidResponses = validColumns.reduce((sum, item) => sum + (item.statistics?.count || 0), 0)
  const totalMissingResponses = validColumns.reduce((sum, item) => sum + (item.statistics?.missing_count || 0), 0)
  const totalNullResponses = validColumns.reduce((sum, item) => sum + (item.statistics?.null_count || 0), 0)
  
  // Get total possible responses (should be consistent across columns)
  const totalPossibleResponses = validColumns[0]?.statistics?.total_responses || 0
  const totalPossibleAcrossAllColumns = totalPossibleResponses * validColumns.length
  
  // Calculate semantic nulls (missing + null)
  const totalSemanticNulls = totalMissingResponses + totalNullResponses
  
  // Calculate percentages
  const validResponseRate = totalPossibleAcrossAllColumns > 0 ? (totalValidResponses / totalPossibleAcrossAllColumns) * 100 : 0
  const missingResponseRate = totalPossibleAcrossAllColumns > 0 ? (totalMissingResponses / totalPossibleAcrossAllColumns) * 100 : 0
  const nullResponseRate = totalPossibleAcrossAllColumns > 0 ? (totalNullResponses / totalPossibleAcrossAllColumns) * 100 : 0
  const semanticNullRate = totalPossibleAcrossAllColumns > 0 ? (totalSemanticNulls / totalPossibleAcrossAllColumns) * 100 : 0
  
  // Calculate per-column averages
  const avgValidPerColumn = validColumns.length > 0 ? totalValidResponses / validColumns.length : 0
  const avgMissingPerColumn = validColumns.length > 0 ? totalMissingResponses / validColumns.length : 0
  const avgNullPerColumn = validColumns.length > 0 ? totalNullResponses / validColumns.length : 0
  
  // Find columns with highest/lowest completion rates
  const columnCompletionRates = validColumns.map(item => ({
    key: item.key,
    label: item.label || item.key,
    validCount: item.statistics?.count || 0,
    missingCount: item.statistics?.missing_count || 0,
    nullCount: item.statistics?.null_count || 0,
    totalResponses: item.statistics?.total_responses || 0,
    completionRate: item.statistics?.total_responses ? ((item.statistics.count || 0) / item.statistics.total_responses) * 100 : 0
  })).sort((a, b) => b.completionRate - a.completionRate)
  
  const highestCompletion = columnCompletionRates[0]
  const lowestCompletion = columnCompletionRates[columnCompletionRates.length - 1]
  
  // Distribution analysis
  const completionBuckets = {
    excellent: columnCompletionRates.filter(c => c.completionRate >= 95).length,
    good: columnCompletionRates.filter(c => c.completionRate >= 80 && c.completionRate < 95).length,
    fair: columnCompletionRates.filter(c => c.completionRate >= 60 && c.completionRate < 80).length,
    poor: columnCompletionRates.filter(c => c.completionRate < 60).length
  }
  
  return {
    columnCount: validColumns.length,
    totalPossibleResponses,
    totalPossibleAcrossAllColumns,
    totalValidResponses,
    totalMissingResponses,
    totalNullResponses,
    totalSemanticNulls,
    validResponseRate,
    missingResponseRate,
    nullResponseRate,
    semanticNullRate,
    avgValidPerColumn,
    avgMissingPerColumn,
    avgNullPerColumn,
    highestCompletion,
    lowestCompletion,
    completionBuckets,
    columnCompletionRates
  }
})
</script>

<template>
  <UCard v-if="statsAnalysis" :ui="{ body: { padding: 'p-4' }, header: { padding: 'p-4' } }">
    <template #header>
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold">{{ title }}</h3>
        <UBadge color="blue" variant="soft">
          {{ statsAnalysis.columnCount }} feature{{ statsAnalysis.columnCount !== 1 ? 's' : '' }}
        </UBadge>
      </div>
    </template>
    
    <!-- Key Metrics Grid -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="text-center p-3 bg-green-50 rounded-lg border border-green-200">
        <div class="text-lg font-bold text-green-700">
          {{ statsAnalysis.validResponseRate.toFixed(1) }}%
        </div>
        <div class="text-sm text-green-600">Valid Responses</div>
        <div class="text-xs text-gray-500 mt-1">
          {{ statsAnalysis.totalValidResponses.toLocaleString() }} total
        </div>
      </div>
      
      <div class="text-center p-3 bg-yellow-50 rounded-lg border border-yellow-200">
        <div class="text-lg font-bold text-yellow-700">
          {{ statsAnalysis.missingResponseRate.toFixed(1) }}%
        </div>
        <div class="text-sm text-yellow-600">Missing/Refused</div>
        <div class="text-xs text-gray-500 mt-1">
          {{ statsAnalysis.totalMissingResponses.toLocaleString() }} total
        </div>
      </div>
      
      <div class="text-center p-3 bg-red-50 rounded-lg border border-red-200">
        <div class="text-lg font-bold text-red-700">
          {{ statsAnalysis.nullResponseRate.toFixed(1) }}%
        </div>
        <div class="text-sm text-red-600">Null Values</div>
        <div class="text-xs text-gray-500 mt-1">
          {{ statsAnalysis.totalNullResponses.toLocaleString() }} total
        </div>
      </div>
      
      <div class="text-center p-3 bg-gray-50 rounded-lg border border-gray-200">
        <div class="text-lg font-bold text-gray-700">
          {{ statsAnalysis.semanticNullRate.toFixed(1) }}%
        </div>
        <div class="text-sm text-gray-600">Semantic Nulls</div>
        <div class="text-xs text-gray-500 mt-1">
          Combined missing + null
        </div>
      </div>
    </div>
    
    <!-- Distribution Analysis -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Completion Rate Distribution -->
      <div>
        <h4 class="font-medium text-gray-900 mb-3">Data Completeness Distribution</h4>
        <div class="space-y-2">
          <div class="flex items-center justify-between p-2 bg-green-50 rounded border border-green-200">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-green-500 rounded-full"></div>
              <span class="text-sm font-medium">Excellent (≥95%)</span>
            </div>
            <UBadge color="green" variant="soft">{{ statsAnalysis.completionBuckets.excellent }}</UBadge>
          </div>
          
          <div class="flex items-center justify-between p-2 bg-blue-50 rounded border border-blue-200">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span class="text-sm font-medium">Good (80-95%)</span>
            </div>
            <UBadge color="blue" variant="soft">{{ statsAnalysis.completionBuckets.good }}</UBadge>
          </div>
          
          <div class="flex items-center justify-between p-2 bg-yellow-50 rounded border border-yellow-200">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span class="text-sm font-medium">Fair (60-80%)</span>
            </div>
            <UBadge color="yellow" variant="soft">{{ statsAnalysis.completionBuckets.fair }}</UBadge>
          </div>
          
          <div class="flex items-center justify-between p-2 bg-red-50 rounded border border-red-200">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 bg-red-500 rounded-full"></div>
              <span class="text-sm font-medium">Poor (<60%)</span>
            </div>
            <UBadge color="red" variant="soft">{{ statsAnalysis.completionBuckets.poor }}</UBadge>
          </div>
        </div>
      </div>
      
      <!-- Extremes -->
      <div>
        <h4 class="font-medium text-gray-900 mb-3">Completion Rate Extremes</h4>
        <div class="space-y-3">
          <div class="p-3 bg-green-50 rounded-lg border border-green-200">
            <div class="text-sm font-medium text-green-800 mb-1">Highest Completion</div>
            <div class="font-mono text-xs text-primary-600">{{ statsAnalysis.highestCompletion.key }}</div>
            <div class="text-sm text-gray-700 mt-1">{{ statsAnalysis.highestCompletion.completionRate.toFixed(1) }}% complete</div>
            <div class="text-xs text-gray-500">{{ statsAnalysis.highestCompletion.validCount.toLocaleString() }} valid responses</div>
          </div>
          
          <div class="p-3 bg-red-50 rounded-lg border border-red-200">
            <div class="text-sm font-medium text-red-800 mb-1">Lowest Completion</div>
            <div class="font-mono text-xs text-primary-600">{{ statsAnalysis.lowestCompletion.key }}</div>
            <div class="text-sm text-gray-700 mt-1">{{ statsAnalysis.lowestCompletion.completionRate.toFixed(1) }}% complete</div>
            <div class="text-xs text-gray-500">{{ statsAnalysis.lowestCompletion.validCount.toLocaleString() }} valid responses</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Per-Column Averages -->
    <div class="mt-6 p-3 bg-gray-50 rounded-lg">
      <h4 class="font-medium text-gray-900 mb-2">Average Per Feature</h4>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div>
          <div class="text-sm font-medium text-gray-700">Valid Responses</div>
          <div class="text-lg font-bold text-green-600">{{ Math.round(statsAnalysis.avgValidPerColumn).toLocaleString() }}</div>
        </div>
        <div>
          <div class="text-sm font-medium text-gray-700">Missing/Refused</div>
          <div class="text-lg font-bold text-yellow-600">{{ Math.round(statsAnalysis.avgMissingPerColumn).toLocaleString() }}</div>
        </div>
        <div>
          <div class="text-sm font-medium text-gray-700">Null Values</div>
          <div class="text-lg font-bold text-red-600">{{ Math.round(statsAnalysis.avgNullPerColumn).toLocaleString() }}</div>
        </div>
      </div>
    </div>
  </UCard>
</template>