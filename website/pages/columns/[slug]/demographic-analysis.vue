<template>
  <div class="min-h-screen bg-gray-50">
    <div class="container mx-auto px-4 py-6">
      <div v-if="pending" class="flex items-center justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin text-gray-500" />
        <span class="ml-2 text-gray-600">Loading analysis...</span>
      </div>

      <div v-else-if="error" class="text-center py-8">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Analysis Not Available</h2>
        <p class="text-gray-600 mb-4">{{ error.message || 'No demographic analysis found for this column.' }}</p>
        <UButton @click="$router.go(-1)" variant="outline">
          <UIcon name="i-heroicons-arrow-left" class="w-4 h-4 mr-2" />
          Go Back
        </UButton>
      </div>

      <div v-else-if="analysisData" class="space-y-6">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Demographic Analysis</h1>
              <p class="text-lg text-gray-700">{{ columnData?.label || route.params.slug }}</p>
              <p class="text-sm text-gray-600 font-mono">{{ route.params.slug }}</p>
            </div>
            <div class="flex gap-2">
              <UButton @click="$router.go(-1)" variant="outline" size="sm">
                <UIcon name="i-heroicons-arrow-left" class="w-4 h-4 mr-2" />
                Back to Columns
              </UButton>
              <UButton 
                :to="`/columns/${route.params.slug}`" 
                variant="outline" 
                size="sm"
              >
                <UIcon name="i-heroicons-information-circle" class="w-4 h-4 mr-2" />
                Column Details
              </UButton>
            </div>
          </div>

          <!-- Summary Stats -->
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <div class="text-2xl font-bold text-blue-700">
                {{ (analysisData.accuracy * 100).toFixed(1) }}%
              </div>
              <div class="text-sm text-blue-600">Model Accuracy</div>
            </div>
            <div class="text-center p-4 bg-green-50 rounded-lg">
              <div class="text-2xl font-bold text-green-700">
                {{ analysisData.analysis_metadata.training_samples.toLocaleString() }}
              </div>
              <div class="text-sm text-green-600">Training Samples</div>
            </div>
            <div class="text-center p-4 bg-purple-50 rounded-lg">
              <div class="text-2xl font-bold text-purple-700">
                {{ analysisData.analysis_metadata.test_samples.toLocaleString() }}
              </div>
              <div class="text-sm text-purple-600">Test Samples</div>
            </div>
            <div class="text-center p-4 bg-orange-50 rounded-lg">
              <div class="text-2xl font-bold text-orange-700">
                {{ analysisData.analysis_metadata.analysis_time_seconds.toFixed(1) }}s
              </div>
              <div class="text-sm text-orange-600">Analysis Time</div>
            </div>
          </div>
        </div>

        <!-- Visualizations -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Confusion Matrix -->
          <div class="bg-white rounded-lg shadow-sm border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Confusion Matrix</h3>
            <div class="flex justify-center">
              <img 
                :src="`/images/${route.params.slug}_demographic_analysis_confusion_matrix.svg`"
                :alt="`Confusion matrix for ${route.params.slug} demographic analysis`"
                class="max-w-full h-auto"
                @error="handleImageError"
              />
            </div>
          </div>

          <!-- Feature Importance -->
          <div class="bg-white rounded-lg shadow-sm border p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Feature Importance</h3>
            <div class="flex justify-center">
              <img 
                :src="`/images/${route.params.slug}_demographic_analysis_feature_importance.svg`"
                :alt="`Feature importance for ${route.params.slug} demographic analysis`"
                class="max-w-full h-auto"
                @error="handleImageError"
              />
            </div>
          </div>
        </div>

        <!-- Model Performance Details -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Classification Report</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Class</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precision</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Recall</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">F1-Score</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Support</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(classData, className) in classificationReport" :key="className">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ getClassLabel(className) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatMetric(classData.precision) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatMetric(classData.recall) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatMetric(classData['f1-score']) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ classData.support?.toLocaleString() || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Feature Details -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Top Features Used</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="feature in topFeatures" :key="feature.feature" 
                 class="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span class="font-mono text-sm">{{ feature.feature }}</span>
              <span class="text-sm font-medium">{{ (feature.importance * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <!-- All Features Used -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">All Features Used in Analysis</h3>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            <div v-for="feature in analysisData.analysis_metadata.features_used" :key="feature" 
                 class="p-2 bg-gray-50 rounded text-sm font-mono text-center">
              {{ feature }}
            </div>
          </div>
          <p class="text-sm text-gray-600 mt-4">
            Total: {{ analysisData.analysis_metadata.features_used.length }} features
          </p>
        </div>

        <!-- Analysis Metadata -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Analysis Details</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong>Model Parameters:</strong>
              <ul class="mt-2 space-y-1 text-gray-600">
                <li v-for="(value, key) in analysisData.model_parameters" :key="key">
                  <span class="font-mono">{{ key }}:</span> {{ value }}
                </li>
              </ul>
            </div>
            <div>
              <strong>Dataset Info:</strong>
              <ul class="mt-2 space-y-1 text-gray-600">
                <li><span class="font-mono">Total samples:</span> {{ analysisData.analysis_metadata.total_samples.toLocaleString() }}</li>
                <li><span class="font-mono">Features used:</span> {{ analysisData.analysis_metadata.features_used.length }}</li>
                <li><span class="font-mono">Features dropped:</span> {{ analysisData.analysis_metadata.features_dropped_missing }}</li>
                <li><span class="font-mono">Target missing:</span> {{ analysisData.analysis_metadata.target_missing_dropped.toLocaleString() }}</li>
                <li><span class="font-mono">Hyperparameter tuning:</span> {{ analysisData.analysis_metadata.hyperparameter_tuning ? 'Yes' : 'No' }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()

// Page metadata
usePageTitle(`Demographic Analysis - ${route.params.slug}`)

// Fetch the demographic analysis data from individual JSON files
const { data: analysisData, pending, error } = await useAsyncData(
  `demographic-analysis-${route.params.slug}`,
  async () => {
    try {
      // Import the specific demographic analysis file directly
      const fileName = `${route.params.slug}_demographic_analysis.json`
      const data = await import(`~/content/${fileName}`)
      
      if (!data || !data.default) {
        throw createError({
          statusCode: 404,
          statusMessage: `No demographic analysis found for column: ${route.params.slug}`
        })
      }
      
      return data.default
    } catch (err) {
      if (err.statusCode) {
        throw err
      }
      throw createError({
        statusCode: 404,
        statusMessage: `No demographic analysis found for column: ${route.params.slug}`
      })
    }
  }
)

// Also fetch the column metadata for context
const { data: columnData } = await useAsyncData('model', async () => {
  const modelData = await queryCollection('columns').first()
  if (!modelData?.columns || !route.params.slug) return null
  
  // Find the specific column
  const column = modelData.columns[route.params.slug] || 
    Object.entries(modelData.columns).find(([key, col]: [string, any]) => 
      col.sas_variable_name === route.params.slug
    )?.[1]
  
  return column
})

// Computed properties for processed data
const classificationReport = computed(() => {
  if (!analysisData.value?.classification_report) return {}
  
  // Filter out summary metrics
  const report = { ...analysisData.value.classification_report }
  delete report.accuracy
  delete report['macro avg']
  delete report['weighted avg']
  
  return report
})

const topFeatures = computed(() => {
  if (!analysisData.value?.feature_importance) return []
  
  // Show top 10 features
  return analysisData.value.feature_importance.slice(0, 10)
})

// Helper functions
const getClassLabel = (className: string) => {
  if (!analysisData.value?.class_labels) return className
  
  const index = parseFloat(className) - 1
  if (index >= 0 && index < analysisData.value.class_labels.length) {
    return `${className}: ${analysisData.value.class_labels[index]}`
  }
  
  return className
}

const formatMetric = (value: number | undefined) => {
  if (value === undefined || value === null) return '-'
  return value.toFixed(3)
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  
  // Show fallback message
  const container = img.parentElement
  if (container) {
    container.innerHTML = '<div class="text-gray-500 text-center p-8">Visualization not available</div>'
  }
}
</script>