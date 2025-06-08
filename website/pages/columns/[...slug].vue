<script setup lang="ts">
// Get the column identifier from the route
const route = useRoute()
const columnId = route.params.slug?.[0]

// Fetch the model data
const { data: modelData } = await useAsyncData('model', () => {
  return queryCollection('columns').first()
})

// Fetch demographic analysis data for this column
const { data: demographicAnalysis } = await useAsyncData(`demographic-analysis-${columnId}`, async () => {
  try {
    // Search for files with stem matching the pattern
    const stem = `${columnId}_demographic_analysis`
    const analysis = await queryCollection('demographic_analysis')
      .where('stem', '=', stem)
      .first()
    
    return analysis || null
  } catch (err) {
    // Return null if no analysis found
    return null
  }
})

// Find the specific column by sas_variable_name or key
const columnData = computed(() => {
  if (!modelData.value?.columns || !columnId) return null
  
  // First try to find by exact key match
  if (modelData.value.columns[columnId]) {
    return {
      key: columnId,
      ...modelData.value.columns[columnId]
    }
  }
  
  // Then try to find by sas_variable_name
  const entry = Object.entries(modelData.value.columns).find(([key, col]: [string, any]) => 
    col.sas_variable_name === columnId
  )
  
  if (entry) {
    return {
      key: entry[0],
      ...entry[1]
    }
  }
  
  return null
})

// Helper to format boolean values
const formatBoolean = (value: boolean | undefined) => {
  if (value === undefined) return 'Not specified'
  return value ? 'Yes' : 'No'
}

// Helper to format array values
const formatArray = (value: any[] | undefined) => {
  if (!value || value.length === 0) return 'None'
  return value.join(', ')
}

// Reference to the iframe component
const iframeComponent = ref()

// Reset codebook iframe to the correct anchor location
const resetCodebook = () => {
  if (iframeComponent.value) {
    iframeComponent.value.reset()
  }
}

// Transform value_ranges into table data
const valueLookupTableData = computed(() => {
  if (!columnData.value?.value_ranges) return []
  
  return columnData.value.value_ranges.map((value, index) => {
    // Handle ValueRange (has start and end properties)
    if ('start' in value && 'end' in value) {
      return {
        value: value.start === value.end ? value.start.toString() : `${value.start} - ${value.end}`,
        count: 'count' in value ? value.count : 0,
        description: value.description,
        indicates_missing: value.indicates_missing || false
      }
    } 
    // Handle ValueDef (only has description)
    else {
      return {
        value: `#${index + 1}`,
        count: '-',
        description: value.description,
        indicates_missing: value.indicates_missing || false
      }
    }
  })
})

// Define columns for the value lookup table - use simple string array
const valueLookupColumns = ['value', 'count', 'description']

// Track highlighted value for chart-table interaction
const highlightedValue = ref<string | null>(null)

/**
 * Scroll to absolute top of page - handles complex Nuxt/Vue layouts
 * 
 * Problem: Standard window.scrollTo(0, 0) was not working because the actual 
 * scrolling was being handled by CSS overflow containers rather than the main window.
 * 
 * Solution: This function resets scroll position on multiple possible scroll containers:
 * 1. Standard DOM elements (document.documentElement, document.body)
 * 2. The window object itself
 * 3. Any CSS containers with overflow properties that might be handling scroll
 * 
 * Why this was needed:
 * - Modern CSS frameworks (Tailwind) and component libraries (Nuxt UI) often use
 *   overflow containers for layout and responsive design
 * - The page scroll might be handled by a parent container with overflow-y-auto
 *   rather than the browser's native window scroll
 * - Standard anchor navigation and window.scrollTo() only work on window-level scroll
 * 
 * Debugging approach used:
 * - Added console.log to verify function was being called
 * - Logged current scroll positions to identify which element was actually scrolled
 * - Used querySelector to find all possible scrollable containers
 * - Reset scroll on any container that had a scroll position > 0
 * 
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollTop
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Window/scrollTo
 */
const scrollToTop = () => {
  // Reset scroll on standard DOM elements (covers most cases)
  document.documentElement.scrollTop = 0
  document.body.scrollTop = 0
  window.scrollTo(0, 0)
  
  // Handle CSS overflow containers that might control page scroll
  // This targets elements with overflow CSS properties that could be scrollable
  const containers = document.querySelectorAll('[style*="overflow"], .overflow-auto, .overflow-y-auto, .overflow-scroll, .overflow-y-scroll')
  containers.forEach((container: Element) => {
    container.scrollTop = 0
  })
}

// Set dynamic breadcrumbs based on column data
const { setBreadcrumbs, clearBreadcrumbs } = usePageTitle()

// Watch for column data changes and update breadcrumbs
watchEffect(() => {
  if (columnData.value) {
    const title = columnData.value.label || columnData.value.key
    setBreadcrumbs([
      {
        label: 'Features',
        to: '/columns'
      },
      {
        label: title,
        icon: 'i-heroicons-chart-bar'
      }
    ])
  }
})

// Clear breadcrumbs when leaving the page
onUnmounted(() => {
  clearBreadcrumbs()
})

// Scroll to top when component mounts
onMounted(() => {
  // Use nextTick to ensure DOM is fully rendered
  nextTick(() => {
    scrollToTop()
  })
})
</script>

<template>
  <div class="container mx-auto py-2 mobile-compact">
    <div v-if="columnData" id="top">
      <!-- Header -->
      <div class="mb-3">
        <h1 class="text-xl font-bold mb-3">{{ columnData.label || columnData.key }}</h1>
        
        <!-- Table of Contents -->
        <div class="mb-3 sticky top-0 z-10 bg-white border-b border-gray-200">
          <nav class="flex items-center gap-3 py-2 overflow-x-auto">
            <button 
              @click="scrollToTop"
              class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 decoration-primary-300 whitespace-nowrap transition-colors cursor-pointer bg-transparent border-none p-0"
            >
              Basic
            </button>
            <a 
              v-if="columnData.valid_values && Object.keys(columnData.valid_values).length > 0"
              href="#valid-values" 
              class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 decoration-primary-300 whitespace-nowrap transition-colors"
            >
              Valid Values
            </a>
            <a 
              v-if="columnData.statistics || (columnData.value_ranges && columnData.value_ranges.length > 0)"
              href="#statistics" 
              class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 decoration-primary-300 whitespace-nowrap transition-colors"
            >
              Statistics
            </a>
            <a 
              v-if="demographicAnalysis"
              href="#demographic-analysis" 
              class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 decoration-primary-300 whitespace-nowrap transition-colors"
            >
              Demographic Analysis
            </a>
            <a 
              v-if="columnData.html_name"
              href="#codebook" 
              class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 decoration-primary-300 whitespace-nowrap transition-colors"
            >
              Codebook
            </a>
            <a 
              href="#json-data" 
              class="text-xs font-medium text-primary-600 hover:text-primary-700 underline underline-offset-2 decoration-primary-300 whitespace-nowrap transition-colors"
            >
              JSON Data
            </a>
          </nav>
        </div>
        
        <div class="bg-gray-50 rounded-lg p-3">
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
            <span>
              <span class="text-gray-500 uppercase text-[10px] tracking-wider">Variable</span>
              <span class="font-mono text-gray-900 font-semibold ml-1">{{ columnData.key }}</span>
            </span>
            <span v-if="columnData.sas_variable_name">
              <span class="text-gray-500 uppercase text-[10px] tracking-wider">SAS</span>
              <span class="font-mono text-gray-900 font-semibold ml-1">{{ columnData.sas_variable_name }}</span>
            </span>
            <span v-if="columnData.section_name">
              <span class="text-gray-500 uppercase text-[10px] tracking-wider">Section</span>
              <span class="text-gray-900 font-semibold ml-1">{{ columnData.section_name }}</span>
            </span>
            <span v-if="columnData.type_of_variable">
              <span class="text-gray-500 uppercase text-[10px] tracking-wider">Type</span>
              <span class="text-gray-900 font-semibold ml-1">{{ columnData.type_of_variable }}</span>
            </span>
            <span v-if="columnData.computed">
              <span class="text-gray-500 uppercase text-[10px] tracking-wider">Computed</span>
              <span class="text-green-600 font-semibold ml-1">Yes</span>
            </span>
            <span v-if="columnData.suppress">
              <span class="text-gray-500 uppercase text-[10px] tracking-wider">Suppress</span>
              <span class="text-orange-600 font-semibold ml-1">Yes</span>
            </span>
          </div>
          <div v-if="columnData.question" class="mt-2">
            <span class="text-gray-500 uppercase text-[10px] tracking-wider block mb-1">Question</span>
            <span class="text-sm text-gray-900">"{{ columnData.question }}"</span>
          </div>
        </div>
      </div>
      
      <!-- Main details -->
      <div class="grid gap-2">
        <!-- Valid Values -->
        <UCard id="valid-values" v-if="columnData.valid_values && Object.keys(columnData.valid_values).length > 0" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">Valid Values</h2>
          </template>
          
          <div class="space-y-0.5">
            <div 
              v-for="(label, value) in columnData.valid_values" 
              :key="value"
              class="flex items-start gap-2 py-0.5 border-b border-gray-100 last:border-0 text-sm"
            >
              <span class="font-mono text-xs text-gray-600 min-w-[2.5rem]">{{ value }}</span>
              <span class="text-gray-900 text-xs">{{ label }}</span>
            </div>
          </div>
        </UCard>
        
        <!-- Statistics -->
        <UCard id="statistics" v-if="columnData.statistics || (columnData.value_ranges && columnData.value_ranges.length > 0)" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">Statistics</h2>
          </template>
          
          <div class="space-y-1">
            <!-- Enhanced response statistics -->
            <div v-if="columnData.statistics" class="bg-gray-50 rounded p-2">
              <h3 class="text-xs font-medium text-gray-700 mb-1">Response Summary</h3>
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-x-3 gap-y-1">
                <div>
                  <span class="text-xs text-gray-600">Valid</span>
                  <p class="text-gray-900 text-sm font-medium">{{ columnData.statistics.count.toLocaleString() }}</p>
                </div>
                
                <div>
                  <span class="text-xs text-gray-600">Total</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.total_responses.toLocaleString() }}</p>
                </div>
                
                <div v-if="columnData.statistics.missing_count > 0">
                  <span class="text-xs text-gray-600">Missing</span>
                  <p class="text-orange-600 text-sm">
                    {{ columnData.statistics.missing_count.toLocaleString() }} 
                    ({{ ((columnData.statistics.missing_count / columnData.statistics.total_responses) * 100).toFixed(1) }}%)
                  </p>
                </div>
                
                <div v-if="columnData.statistics.null_count > 0">
                  <span class="text-xs text-gray-600">Null</span>
                  <p class="text-gray-500 text-sm">{{ columnData.statistics.null_count.toLocaleString() }}</p>
                </div>
                
                <div v-if="columnData.statistics.unique_count !== undefined">
                  <span class="text-xs text-gray-600">Unique</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.unique_count.toLocaleString() }}</p>
                </div>
              </div>
            </div>
            
            <!-- Numeric statistics -->
            <div v-if="columnData.statistics && 'mean' in columnData.statistics" class="bg-blue-50 rounded p-2">
              <h3 class="text-xs font-medium text-gray-700 mb-1">Numeric Distribution</h3>
              
              <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-x-3 gap-y-1">
                <div v-if="columnData.statistics.mean !== undefined && columnData.statistics.mean !== null">
                  <span class="text-xs text-gray-600">Mean</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.mean.toLocaleString(undefined, {maximumFractionDigits: 4}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.median !== undefined && columnData.statistics.median !== null">
                  <span class="text-xs text-gray-600">Median</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.median.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.std !== undefined && columnData.statistics.std !== null">
                  <span class="text-xs text-gray-600">Std Dev</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.std.toLocaleString(undefined, {maximumFractionDigits: 4}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.min !== undefined && columnData.statistics.min !== null">
                  <span class="text-xs text-gray-600">Min</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.min.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.q25 !== undefined && columnData.statistics.q25 !== null">
                  <span class="text-xs text-gray-600">25th %</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.q25.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.median !== undefined && columnData.statistics.median !== null">
                  <span class="text-xs text-gray-600">50th %</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.median.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.q75 !== undefined && columnData.statistics.q75 !== null">
                  <span class="text-xs text-gray-600">75th %</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.q75.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.max !== undefined && columnData.statistics.max !== null">
                  <span class="text-xs text-gray-600">Max</span>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.max.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
              </div>
            </div>
            
            <!-- Categorical statistics -->
            <div v-if="columnData.statistics && 'top_values' in columnData.statistics && columnData.statistics.top_values.length > 0" class="bg-green-50 rounded p-2">
              <h3 class="text-xs font-medium text-gray-700 mb-1">Top Values</h3>
              
              <div class="space-y-0.5">
                <div 
                  v-for="(valueInfo, index) in columnData.statistics.top_values.slice(0, 8)" 
                  :key="index"
                  class="flex items-start gap-2 py-0.5 border-b border-green-100 last:border-0"
                >
                  <span class="font-mono text-xs text-gray-600 min-w-[4rem] whitespace-nowrap">
                    {{ valueInfo.value }} ({{ valueInfo.count.toLocaleString() }})
                  </span>
                  <span v-if="valueInfo.description" class="text-gray-900 text-xs">
                    {{ valueInfo.description }}
                  </span>
                </div>
              </div>
              <div v-if="columnData.statistics.top_values.length > 8" class="text-xs text-gray-500 mt-0.5">
                Showing 8 of {{ columnData.statistics.top_values.length }} values
              </div>
            </div>
            
            <!-- Response Values -->
            <div v-if="columnData.value_ranges && columnData.value_ranges.length > 0" class="bg-purple-50 rounded p-2">
              <h3 class="text-xs font-medium text-gray-700 mb-2">Response Values</h3>
              
              <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
                <!-- Chart Section -->
                <div v-if="valueLookupTableData.length > 0">
                  <div class="bg-white rounded p-2">
                    <ResponseChartHorizontal 
                      :value-data="valueLookupTableData" 
                      title="Response Distribution"
                      @highlight-value="highlightedValue = $event"
                    />
                  </div>
                </div>
                
                <!-- Table Section -->
                <div>
                  <div class="overflow-x-auto bg-white rounded p-2">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead>
                        <tr>
                          <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Value</th>
                          <th class="px-2 py-1 text-right text-xs font-medium text-gray-700">Count</th>
                          <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Description</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-200">
                        <tr 
                          v-for="(row, index) in valueLookupTableData" 
                          :key="index"
                          :class="{
                            'bg-blue-100 border-l-4 border-blue-500': highlightedValue === row.value,
                            'bg-red-50 hover:bg-red-100': row.indicates_missing && highlightedValue !== row.value,
                            'hover:bg-gray-50': !row.indicates_missing && highlightedValue !== row.value
                          }"
                        >
                          <td class="px-2 py-1 text-xs font-mono text-gray-900">{{ row.value }}</td>
                          <td class="px-2 py-1 text-xs text-right">
                            <span v-if="row.count !== '-'" class="text-gray-900">
                              {{ typeof row.count === 'number' ? row.count.toLocaleString() : row.count }}
                            </span>
                            <span v-else class="text-gray-400">
                              {{ row.count }}
                            </span>
                          </td>
                          <td class="px-2 py-1 text-xs text-gray-900">{{ row.description }}</td>
                        </tr>
                      </tbody>
                    </table>
                    
                    <!-- Legend for missing values -->
                    <div v-if="valueLookupTableData.some(row => row.indicates_missing)" class="mt-2 p-2 bg-gray-50 rounded">
                      <div class="flex items-center gap-2 text-xs">
                        <div class="flex items-center gap-1">
                          <div class="w-3 h-3 bg-red-100 border border-red-200 rounded"></div>
                          <span class="text-gray-600">Missing/Refused/Unknown values</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </UCard>
        
        <!-- Demographic Analysis -->
        <UCard id="demographic-analysis" v-if="demographicAnalysis" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-base font-semibold">Demographic Analysis</h2>
              <NuxtLink 
                :to="`/columns/${columnId}/demographic-analysis`"
                class="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-0.5"
              >
                View full analysis
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3 h-3" />
              </NuxtLink>
            </div>
          </template>
          
          <div class="space-y-3">
            <!-- Summary Stats -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <div class="text-lg font-bold text-blue-700">
                  {{ (demographicAnalysis.accuracy * 100).toFixed(1) }}%
                </div>
                <div class="text-xs text-blue-600">Model Accuracy</div>
              </div>
              <div class="text-center p-3 bg-green-50 rounded-lg">
                <div class="text-lg font-bold text-green-700">
                  {{ demographicAnalysis.analysis_metadata.training_samples.toLocaleString() }}
                </div>
                <div class="text-xs text-green-600">Training Samples</div>
              </div>
              <div class="text-center p-3 bg-purple-50 rounded-lg">
                <div class="text-lg font-bold text-purple-700">
                  {{ demographicAnalysis.analysis_metadata.test_samples.toLocaleString() }}
                </div>
                <div class="text-xs text-purple-600">Test Samples</div>
              </div>
              <div class="text-center p-3 bg-orange-50 rounded-lg">
                <div class="text-lg font-bold text-orange-700">
                  {{ demographicAnalysis.analysis_metadata.analysis_time_seconds.toFixed(1) }}s
                </div>
                <div class="text-xs text-orange-600">Analysis Time</div>
              </div>
            </div>

            <!-- Top Features -->
            <div>
              <h3 class="text-sm font-medium text-gray-700 mb-2">Top Predictive Features</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div 
                  v-for="feature in demographicAnalysis.feature_importance.slice(0, 8)" 
                  :key="feature.feature" 
                  class="flex justify-between items-center p-2 bg-gray-50 rounded text-xs"
                >
                  <span class="font-mono">{{ feature.feature }}</span>
                  <span class="font-medium">{{ (feature.importance * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>

            <!-- Quick Performance Summary -->
            <div>
              <h3 class="text-sm font-medium text-gray-700 mb-2">Model Performance</h3>
              <div class="bg-gray-50 rounded-lg p-3 text-xs">
                <p class="text-gray-600 mb-1">
                  Random Forest model trained on {{ demographicAnalysis.analysis_metadata.features_used.length }} demographic features 
                  to predict {{ columnData?.label || columnId }} values.
                </p>
                <p class="text-gray-600">
                  Achieved {{ (demographicAnalysis.accuracy * 100).toFixed(1) }}% accuracy on 
                  {{ demographicAnalysis.analysis_metadata.test_samples.toLocaleString() }} test samples.
                </p>
              </div>
            </div>
          </div>
        </UCard>
        
        <!-- Codebook -->
        <UCard id="codebook" v-if="columnData.html_name" :ui="{ body: { padding: 'p-1' }, header: { padding: 'p-2' } }">
          <template #header>
            <div class="flex items-center justify-between">
              <h2 class="text-base font-semibold">Codebook</h2>
              <div class="flex items-center gap-0.5">
                <UButton
                  @click="resetCodebook"
                  variant="ghost"
                  size="xs"
                  icon="i-heroicons-arrow-path"
                  title="Reset to column location"
                >
                  Reset
                </UButton>
                <NuxtLink 
                  :to="`/html/codebook_USCODE23_LLCP_021924.HTML#${columnData.html_name}`"
                  target="_blank"
                  class="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-0.5"
                >
                  Open in new tab
                  <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3 h-3" />
                </NuxtLink>
              </div>
            </div>
          </template>
          
          <IframeComponent
            ref="iframeComponent"
            src="/html/codebook_USCODE23_LLCP_021924.HTML"
            :anchor="columnData.html_name"
            :title="`Codebook for ${columnData.label || columnData.key}`"
          />
        </UCard>
        
        <!-- JSON Data -->
        <UCard id="json-data" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">JSON Data</h2>
          </template>
          
          <JSONView :data="columnData" max-height="400px" />
        </UCard>
      </div>
    </div>
    
    <!-- Not found state -->
    <div v-else class="text-center py-12">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-10 h-10 text-gray-400 mx-auto mb-3" />
      <h2 class="text-lg font-semibold text-gray-900 mb-2">Column not found</h2>
      <p class="text-gray-600 mb-4 text-sm">The column "{{ columnId }}" could not be found in the model.</p>
      <NuxtLink to="/columns" class="text-primary-600 hover:text-primary-700 text-sm">
        Return to columns list
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
html {
  scroll-behavior: smooth;
}
</style>