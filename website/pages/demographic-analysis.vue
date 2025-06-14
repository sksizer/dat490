<script setup lang="ts">
// Fetch feature importance summary data
const { data: featureImportanceData } = await useAsyncData('feature-importance', () => {
  return queryCollection('feature_importance_summary').first()
})

// Fetch the model data for analyzed features
const { data: modelData } = await useAsyncData('model', () => {
  const val = queryCollection('columns').first()
  return val
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

// Create analyzed features data for the table
const analyzedFeatures = computed(() => {
  if (!modelData.value?.columns) return []
  
  return Object.entries(modelData.value.columns)
    .filter(([key, column]) => column.demographic_analysis_score !== null && column.demographic_analysis_score !== undefined)
    .map(([key, column]) => ({
      key,
      question: column.question || column.label || key,
      accuracy: column.demographic_analysis_score,
      section: column.section_name || 'Unknown',
      label: column.label || key,
      sas_variable_name: column.sas_variable_name || key
    }))
    .sort((a, b) => (b.accuracy || 0) - (a.accuracy || 0)) // Sort by accuracy desc
})

// Search and filtering for analyzed features
const searchAnalyzed = ref('')
const filteredAnalyzedFeatures = computed(() => {
  if (!searchAnalyzed.value) return analyzedFeatures.value
  
  const searchLower = searchAnalyzed.value.toLowerCase()
  return analyzedFeatures.value.filter(feature => 
    feature.key.toLowerCase().includes(searchLower) ||
    feature.question.toLowerCase().includes(searchLower) ||
    feature.section.toLowerCase().includes(searchLower)
  )
})

// Helper function to get accuracy color class
const getAccuracyColor = (accuracy: number) => {
  if (accuracy >= 0.8) return 'text-green-700 bg-green-50'
  if (accuracy >= 0.6) return 'text-yellow-700 bg-yellow-50'
  return 'text-red-700 bg-red-50'
}
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

      <!-- Analyzed Features Table -->
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-lg font-semibold">All Analyzed Features</h3>
              <p class="text-sm text-gray-600 mt-1">
                Complete list of {{ analyzedFeatures.length }} health variables analyzed for demographic predictability
              </p>
            </div>
            <UBadge color="blue" variant="soft">
              {{ filteredAnalyzedFeatures.length }} feature{{ filteredAnalyzedFeatures.length !== 1 ? 's' : '' }}
            </UBadge>
          </div>
        </template>

        <!-- Search Bar -->
        <div class="mb-4">
          <UInput 
            v-model="searchAnalyzed" 
            placeholder="Search by column name, question, or section..." 
            icon="i-heroicons-magnifying-glass"
            size="sm"
            class="max-w-md"
          />
        </div>

        <!-- Features Table -->
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200">
                <th class="text-left py-2 px-3 font-medium text-gray-700">Column</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">Question/Label</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">Accuracy</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">Section</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="feature in filteredAnalyzedFeatures" 
                :key="feature.key"
                class="border-b border-gray-100 hover:bg-gray-50"
              >
                <!-- Column Name -->
                <td class="py-3 px-3">
                  <NuxtLink 
                    :to="`/columns/${feature.sas_variable_name}`"
                    class="font-mono text-sm text-primary-600 hover:text-primary-700 hover:underline transition-colors"
                    :title="`View details for ${feature.key}`"
                  >
                    {{ feature.key }}
                  </NuxtLink>
                </td>

                <!-- Question/Label -->
                <td class="py-3 px-3">
                  <div class="max-w-md">
                    <span 
                      v-if="feature.question.length <= 100"
                      class="text-gray-700"
                    >
                      {{ feature.question }}
                    </span>
                    <span 
                      v-else
                      :title="feature.question"
                      class="text-gray-700 cursor-help"
                    >
                      {{ feature.question.substring(0, 100) }}...
                    </span>
                  </div>
                </td>

                <!-- Accuracy Score -->
                <td class="py-3 px-3">
                  <div class="flex items-center gap-2">
                    <span 
                      :class="`px-2 py-1 rounded-full text-sm font-medium ${getAccuracyColor(feature.accuracy)}`"
                    >
                      {{ (feature.accuracy * 100).toFixed(1) }}%
                    </span>
                  </div>
                </td>

                <!-- Section -->
                <td class="py-3 px-3">
                  <NuxtLink 
                    :to="`/columns?section=${encodeURIComponent(feature.section)}`"
                    class="text-sm text-gray-600 hover:text-primary-600 hover:underline transition-colors"
                    :title="`View all features in ${feature.section} section`"
                  >
                    {{ feature.section }}
                  </NuxtLink>
                </td>

                <!-- Actions -->
                <td class="py-3 px-3">
                  <div class="flex items-center gap-2">
                    <NuxtLink 
                      :to="`/columns/${feature.sas_variable_name}`"
                      target="_blank"
                      class="text-gray-500 hover:text-primary-600 transition-colors"
                      :title="`View ${feature.key} details in new tab`"
                    >
                      <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4" />
                    </NuxtLink>
                    <NuxtLink 
                      :to="`/columns/${feature.sas_variable_name}/demographic-analysis`"
                      target="_blank"
                      class="text-gray-500 hover:text-green-600 transition-colors"
                      :title="`View ${feature.key} demographic analysis in new tab`"
                    >
                      <UIcon name="i-heroicons-chart-bar" class="w-4 h-4" />
                    </NuxtLink>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Empty State -->
        <div v-if="filteredAnalyzedFeatures.length === 0 && searchAnalyzed" class="text-center py-8">
          <UIcon name="i-heroicons-magnifying-glass" class="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p class="text-gray-500">No features match your search</p>
          <UButton 
            @click="searchAnalyzed = ''" 
            variant="ghost" 
            size="sm" 
            class="mt-2"
          >
            Clear search
          </UButton>
        </div>

        <!-- Table Footer with Summary -->
        <div class="mt-4 pt-4 border-t border-gray-200">
          <div class="flex items-center justify-between text-sm text-gray-600">
            <div>
              Showing {{ filteredAnalyzedFeatures.length }} of {{ analyzedFeatures.length }} analyzed features
            </div>
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-1">
                <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                <span>≥80% accuracy</span>
              </div>
              <div class="flex items-center gap-1">
                <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span>60-80% accuracy</span>
              </div>
              <div class="flex items-center gap-1">
                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                <span><60% accuracy</span>
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
            <p class="text-xs text-gray-500 mb-2">
              Click any section to view its features in the columns browser
            </p>
            <div class="space-y-2">
              <NuxtLink 
                v-for="section in featureImportanceData.sections_analyzed" 
                :key="section"
                :to="`/columns?section=${encodeURIComponent(section)}`"
                target="_blank"
                class="block text-sm font-medium text-gray-800 p-3 bg-green-50 rounded-lg border border-green-200 hover:bg-green-100 hover:border-green-300 hover:shadow-sm transition-all duration-200 cursor-pointer group"
              >
                <div class="flex items-center justify-between">
                  <span class="text-green-800 group-hover:text-green-900">{{ section }}</span>
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-green-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      View features
                    </span>
                    <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity text-green-600" />
                  </div>
                </div>
              </NuxtLink>
            </div>
          </div>

          <!-- Sections Excluded -->
          <div>
            <h4 class="font-medium text-gray-900 mb-2">Health Sections Excluded</h4>
            <p class="text-xs text-gray-500 mb-2">
              Click any section to view its features (excluded from demographic analysis)
            </p>
            <div class="space-y-2">
              <NuxtLink 
                v-for="section in featureImportanceData.sections_excluded" 
                :key="section"
                :to="`/columns?section=${encodeURIComponent(section)}`"
                target="_blank"
                class="block text-sm font-medium text-gray-800 p-3 bg-red-50 rounded-lg border border-red-200 hover:bg-red-100 hover:border-red-300 hover:shadow-sm transition-all duration-200 cursor-pointer group"
              >
                <div class="flex items-center justify-between">
                  <span class="text-red-800 group-hover:text-red-900">{{ section }}</span>
                  <div class="flex items-center gap-1">
                    <span class="text-xs text-red-600 opacity-0 group-hover:opacity-100 transition-opacity">
                      View features
                    </span>
                    <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-4 h-4 opacity-60 group-hover:opacity-100 transition-opacity text-red-600" />
                  </div>
                </div>
              </NuxtLink>
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