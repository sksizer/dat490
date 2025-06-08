<script setup lang="ts">
// Fetch feature importance summary data
const { data: featureImportanceData } = await useAsyncData('feature-importance', () => {
  return queryCollection('feature_importance_summary').first()
})

// Set the breadcrumbs
const { setBreadcrumbs, clearBreadcrumbs } = usePageTitle()

// Set breadcrumbs when component mounts
onMounted(() => {
  setBreadcrumbs([
    {
      label: 'BFRSS Features',
      to: '/columns'
    },
    {
      label: 'Demographic Analysis',
      to: '/demographic-analysis'
    }
  ])
})

// Clear breadcrumbs when component unmounts
onUnmounted(() => {
  clearBreadcrumbs()
})

// Handle image loading errors for demographic analysis charts
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  
  // Show fallback message
  const container = img.parentElement
  if (container) {
    container.innerHTML = '<div class="text-gray-500 text-center p-4 text-sm">Visualization not available</div>'
  }
}

// Group features by importance ranges for additional insights
const featureGroups = computed(() => {
  if (!featureImportanceData.value?.top_features) return { high: [], medium: [], low: [] }
  
  const features = featureImportanceData.value.top_features
  
  return {
    high: features.filter(f => f.average_importance >= 0.15),
    medium: features.filter(f => f.average_importance >= 0.05 && f.average_importance < 0.15),
    low: features.filter(f => f.average_importance < 0.05)
  }
})

// Calculate additional insights
const insights = computed(() => {
  if (!featureImportanceData.value) return null
  
  const data = featureImportanceData.value
  const totalAnalyses = data.total_analyses
  const successRate = (data.successful_analyses / totalAnalyses * 100)
  
  // Find most consistent predictor (highest frequency in top 5)
  const mostConsistent = data.top_features.reduce((prev, current) => 
    (current.frequency > prev.frequency) ? current : prev, data.top_features[0]
  )
  
  // Find accuracy range with most analyses
  const accuracyEntries = Object.entries(data.accuracy_distribution)
  const mostCommonRange = accuracyEntries.reduce((prev, current) => 
    current[1] > prev[1] ? current : prev, accuracyEntries[0]
  )
  
  return {
    successRate,
    mostConsistent,
    mostCommonAccuracyRange: mostCommonRange[0],
    mostCommonAccuracyCount: mostCommonRange[1]
  }
})
</script>

<template>
  <div class="container mx-auto py-4">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Demographic Analysis</h1>
      <p class="text-gray-600">
        Comprehensive analysis of which demographic variables best predict health outcomes across the BRFSS dataset.
        <NuxtLink to="/demographic_analysis" class="text-primary-600 hover:text-primary-700 ml-1">
          View methodology →
        </NuxtLink>
      </p>
    </div>

    <div v-if="!featureImportanceData" class="text-center py-12">
      <UIcon name="i-heroicons-chart-bar" class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <p class="text-gray-500">No demographic analysis data available</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Key Insights Overview -->
      <UCard>
        <template #header>
          <h2 class="text-lg font-semibold">Analysis Overview</h2>
        </template>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-700">
              {{ (featureImportanceData.average_accuracy * 100).toFixed(1) }}%
            </div>
            <div class="text-sm text-blue-600">Average Accuracy</div>
            <div class="text-xs text-gray-500 mt-1">
              Across {{ featureImportanceData.successful_analyses }} analyses
            </div>
          </div>
          
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-700">
              {{ insights?.successRate.toFixed(1) }}%
            </div>
            <div class="text-sm text-green-600">Success Rate</div>
            <div class="text-xs text-gray-500 mt-1">
              {{ featureImportanceData.successful_analyses }}/{{ featureImportanceData.total_analyses }} analyses
            </div>
          </div>
          
          <div class="text-center p-4 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-700">
              {{ featureImportanceData.sections_analyzed.length }}
            </div>
            <div class="text-sm text-purple-600">Health Sections</div>
            <div class="text-xs text-gray-500 mt-1">
              Analyzed for demographic patterns
            </div>
          </div>
          
          <div class="text-center p-4 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-700">
              {{ featureImportanceData.top_features.length }}
            </div>
            <div class="text-sm text-orange-600">Demographic Features</div>
            <div class="text-xs text-gray-500 mt-1">
              Used as predictors
            </div>
          </div>
        </div>

        <!-- Key Insights -->
        <div v-if="insights" class="bg-gray-50 rounded-lg p-4 space-y-2">
          <h3 class="font-medium text-gray-900">Key Insights</h3>
          <ul class="text-sm text-gray-700 space-y-1">
            <li>
              <strong>Most consistent predictor:</strong> 
              <NuxtLink :to="`/columns/${insights.mostConsistent.feature}`" class="text-primary-600 hover:text-primary-700 font-mono">
                {{ insights.mostConsistent.feature }}
              </NuxtLink>
              (appears in top-5 for {{ insights.mostConsistent.frequency }} analyses)
            </li>
            <li>
              <strong>Most common accuracy range:</strong> {{ insights.mostCommonAccuracyRange }} 
              ({{ insights.mostCommonAccuracyCount }} analyses)
            </li>
            <li>
              <strong>Sections excluded:</strong> {{ featureImportanceData.sections_excluded.join(', ') }}
            </li>
          </ul>
        </div>
      </UCard>

      <!-- Large Visualizations -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <!-- Feature Importance Ranking -->
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">Top Demographic Predictors</h3>
            <p class="text-sm text-gray-600 mt-1">
              Average feature importance across {{ featureImportanceData.successful_analyses }} Random Forest models
            </p>
          </template>
          
          <div class="flex justify-center">
            <img 
              src="/images/feature_importance_ranking.svg"
              alt="Top demographic features by importance"
              class="max-w-full h-auto"
              @error="handleImageError"
            />
          </div>
        </UCard>

        <!-- Accuracy Distribution -->
        <UCard>
          <template #header>
            <h3 class="text-lg font-semibold">Accuracy Distribution</h3>
            <p class="text-sm text-gray-600 mt-1">
              How well demographics predict various health outcomes
            </p>
          </template>
          
          <div class="flex justify-center">
            <img 
              src="/images/analysis_accuracy_distribution.svg"
              alt="Distribution of analysis accuracy scores"
              class="max-w-full h-auto"
              @error="handleImageError"
            />
          </div>
        </UCard>
      </div>

      <!-- Detailed Feature Breakdown -->
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Feature Importance Breakdown</h3>
          <p class="text-sm text-gray-600 mt-1">
            All {{ featureImportanceData.top_features.length }} demographic features ranked by predictive power
          </p>
        </template>

        <!-- Feature Groups -->
        <div class="space-y-6">
          <!-- High Importance Features -->
          <div v-if="featureGroups.high.length > 0">
            <h4 class="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <div class="w-3 h-3 bg-red-500 rounded-full"></div>
              High Importance Features (≥15%)
              <UBadge color="red" variant="soft">{{ featureGroups.high.length }}</UBadge>
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div 
                v-for="(feature, index) in featureGroups.high" 
                :key="feature.feature"
                class="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-200"
              >
                <div class="flex items-center gap-2">
                  <span class="w-6 h-6 bg-red-100 text-red-800 rounded-full flex items-center justify-center text-xs font-bold">
                    {{ feature.rank }}
                  </span>
                  <NuxtLink 
                    :to="`/columns/${feature.feature}`"
                    class="font-mono text-sm text-primary-600 hover:text-primary-700 hover:underline transition-colors"
                    :title="`View details for ${feature.feature}`"
                  >
                    {{ feature.feature }}
                  </NuxtLink>
                </div>
                <div class="text-right">
                  <div class="font-medium text-sm">{{ (feature.average_importance * 100).toFixed(1) }}%</div>
                  <div class="text-xs text-gray-500">{{ feature.frequency }}x top-5</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Medium Importance Features -->
          <div v-if="featureGroups.medium.length > 0">
            <h4 class="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
              Medium Importance Features (5-15%)
              <UBadge color="yellow" variant="soft">{{ featureGroups.medium.length }}</UBadge>
            </h4>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              <div 
                v-for="(feature, index) in featureGroups.medium" 
                :key="feature.feature"
                class="flex justify-between items-center p-3 bg-yellow-50 rounded-lg border border-yellow-200"
              >
                <div class="flex items-center gap-2">
                  <span class="w-5 h-5 bg-yellow-100 text-yellow-800 rounded-full flex items-center justify-center text-xs font-bold">
                    {{ feature.rank }}
                  </span>
                  <NuxtLink 
                    :to="`/columns/${feature.feature}`"
                    class="font-mono text-xs text-primary-600 hover:text-primary-700 hover:underline transition-colors"
                    :title="`View details for ${feature.feature}`"
                  >
                    {{ feature.feature }}
                  </NuxtLink>
                </div>
                <div class="text-right">
                  <div class="font-medium text-xs">{{ (feature.average_importance * 100).toFixed(1) }}%</div>
                  <div class="text-xs text-gray-500">{{ feature.frequency }}x</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Low Importance Features -->
          <div v-if="featureGroups.low.length > 0">
            <h4 class="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <div class="w-3 h-3 bg-gray-400 rounded-full"></div>
              Lower Importance Features (<5%)
              <UBadge color="gray" variant="soft">{{ featureGroups.low.length }}</UBadge>
            </h4>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
              <div 
                v-for="(feature, index) in featureGroups.low" 
                :key="feature.feature"
                class="flex justify-between items-center p-2 bg-gray-50 rounded border border-gray-200"
              >
                <div class="flex items-center gap-1">
                  <span class="w-4 h-4 bg-gray-100 text-gray-600 rounded-full flex items-center justify-center text-xs font-bold">
                    {{ feature.rank }}
                  </span>
                  <NuxtLink 
                    :to="`/columns/${feature.feature}`"
                    class="font-mono text-xs text-primary-600 hover:text-primary-700 hover:underline transition-colors"
                    :title="`View details for ${feature.feature}`"
                  >
                    {{ feature.feature }}
                  </NuxtLink>
                </div>
                <div class="text-xs text-gray-500">
                  {{ (feature.average_importance * 100).toFixed(1) }}%
                </div>
              </div>
            </div>
          </div>
        </div>
      </UCard>

      <!-- Analysis Details -->
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">Analysis Details</h3>
        </template>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Sections Analyzed -->
          <div>
            <h4 class="font-medium text-gray-900 mb-2">Health Sections Analyzed</h4>
            <div class="space-y-1">
              <div 
                v-for="section in featureImportanceData.sections_analyzed" 
                :key="section"
                class="text-sm text-gray-700 p-2 bg-green-50 rounded border border-green-200"
              >
                {{ section }}
              </div>
            </div>
          </div>

          <!-- Sections Excluded -->
          <div>
            <h4 class="font-medium text-gray-900 mb-2">Health Sections Excluded</h4>
            <div class="space-y-1">
              <div 
                v-for="section in featureImportanceData.sections_excluded" 
                :key="section"
                class="text-sm text-gray-700 p-2 bg-red-50 rounded border border-red-200"
              >
                {{ section }}
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-2">
              These sections were excluded to focus on genuine health outcomes rather than calculated variables.
            </p>
          </div>
        </div>
      </UCard>

      <!-- Call to Action -->
      <UCard>
        <div class="text-center py-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Explore Individual Features</h3>
          <p class="text-gray-600 mb-4">
            View detailed demographic analysis results for specific health variables
          </p>
          <div class="flex justify-center gap-4">
            <UButton to="/columns" variant="solid" color="primary">
              Browse All Features
            </UButton>
            <UButton to="/demographic_analysis" variant="outline" color="primary">
              View Methodology
            </UButton>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
</style>