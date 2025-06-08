<script setup lang="ts">
interface Props {
  modelData: any
  featureImportanceData?: any
}

const props = defineProps<Props>()

// Calculate metadata statistics
const stats = computed(() => {
  if (!props.modelData?.columns) {
    return {
      totalColumns: 0,
      computedColumns: 0,
      sections: 0,
      typesOfVariables: 0,
      demographicAnalyses: 0
    }
  }

  const columns = Object.values(props.modelData.columns)
  const computedColumns = columns.filter((col: any) => col.computed).length
  const sections = new Set(columns.map((col: any) => col.section_name).filter(Boolean))
  const variableTypes = new Set(columns.map((col: any) => col.type_of_variable).filter(Boolean))
  
  // Count columns with demographic analysis scores
  const demographicAnalyses = columns.filter((col: any) => 
    col.demographic_analysis_score !== null && col.demographic_analysis_score !== undefined
  ).length

  return {
    totalColumns: columns.length,
    computedColumns,
    sections: sections.size,
    typesOfVariables: variableTypes.size,
    demographicAnalyses
  }
})

// Calculate demographic analysis summary stats
const demographicStats = computed(() => {
  if (!props.featureImportanceData) {
    return {
      successfulAnalyses: stats.value.demographicAnalyses,
      averageAccuracy: null,
      topFeatureName: null
    }
  }
  
  return {
    successfulAnalyses: props.featureImportanceData.successful_analyses,
    averageAccuracy: props.featureImportanceData.average_accuracy,
    topFeatureName: props.featureImportanceData.top_features?.[0]?.feature || null
  }
})
</script>

<template>
  <UCard class="mb-3">
    <div class="grid grid-cols-1 md:grid-cols-5 gap-3">
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Columns</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.totalColumns }}</p>
      </div>
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Computed Columns</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.computedColumns }}</p>
      </div>
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Sections</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.sections }}</p>
      </div>
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Variable Types</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.typesOfVariables }}</p>
      </div>
      <NuxtLink 
        to="/demographic-analysis"
        class="group cursor-pointer hover:bg-blue-50 rounded-lg p-2 -m-2 transition-colors"
        :title="demographicStats.averageAccuracy ? `Average accuracy: ${(demographicStats.averageAccuracy * 100).toFixed(1)}%. Click to view detailed analysis.` : 'Click to view demographic analysis details.'"
      >
        <div>
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400 group-hover:text-blue-600 transition-colors flex items-center gap-1">
            Demographic Analyses
            <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
          </p>
          <p class="mt-1 text-2xl font-semibold group-hover:text-blue-700 transition-colors">
            {{ demographicStats.successfulAnalyses }}
          </p>
          <p v-if="demographicStats.averageAccuracy" class="text-xs text-gray-500 group-hover:text-blue-500 transition-colors">
            {{ (demographicStats.averageAccuracy * 100).toFixed(1) }}% avg accuracy
          </p>
        </div>
      </NuxtLink>
    </div>
  </UCard>
</template>