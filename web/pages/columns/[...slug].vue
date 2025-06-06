<script setup lang="ts">
// Get the column identifier from the route
const route = useRoute()
const columnId = route.params.slug?.[0]

// Fetch the model data
const { data: modelData } = await useAsyncData('model', () => {
  return queryCollection('columns').first()
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

// Reference to the iframe element
const codebookIframe = ref<HTMLIFrameElement>()

// Reset codebook iframe to the correct anchor location
const resetCodebook = () => {
  if (codebookIframe.value && columnData.value?.html_name) {
    codebookIframe.value.src = `/html/codebook_USCODE23_LLCP_021924.HTML#${columnData.value.html_name}`
  }
}

// Transform value_lookup into table data
const valueLookupTableData = computed(() => {
  if (!columnData.value?.value_lookup) return []
  
  return columnData.value.value_lookup.map((value, index) => {
    // Handle ValueRange (has start and end properties)
    if ('start' in value && 'end' in value) {
      return {
        value: value.start === value.end ? value.start.toString() : `${value.start} - ${value.end}`,
        count: 'count' in value ? value.count : 0,
        description: value.description
      }
    } 
    // Handle ValueDef (only has description)
    else {
      return {
        value: `#${index + 1}`,
        count: '-',
        description: value.description
      }
    }
  })
})

// Define columns for the value lookup table - use simple string array
const valueLookupColumns = ['value', 'count', 'description']

// Define chart tabs for UTabs component
const chartTabs = [
  { label: 'Vertical Chart', value: 'vertical', icon: 'i-heroicons-chart-bar' },
  { label: 'Horizontal Chart', value: 'horizontal', icon: 'i-heroicons-chart-bar-square' }
]

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
</script>

<template>
  <div class="container mx-auto py-2 mobile-compact">
    <!-- Back button -->
    <NuxtLink 
      to="/columns" 
      class="inline-flex items-center gap-2 mb-2 text-gray-600 hover:text-gray-900 transition-colors">
    >
      <UIcon name="i-heroicons-arrow-left" />
      Back to features
    </NuxtLink>
    
    <div v-if="columnData" id="top">
      <!-- Header -->
      <div class="mb-3">
        <h1 class="text-xl font-bold mb-1">{{ columnData.label || columnData.key }}</h1>
        <div class="flex items-center gap-3 text-gray-600 text-sm">
          <span class="font-mono text-xs">{{ columnData.key }}</span>
          <span v-if="columnData.sas_variable_name" class="text-xs">
            SAS: <span class="font-mono text-xs">{{ columnData.sas_variable_name }}</span>
          </span>
        </div>
      </div>
      
      <!-- Table of Contents -->
      <div class="mb-3 sticky top-0 z-10 bg-white border-b border-gray-200">
        <nav class="flex items-center gap-3 py-2 overflow-x-auto">
          <button 
            @click="scrollToTop"
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors cursor-pointer bg-transparent border-none p-0"
          >
            Start
          </button>
          <a 
            href="#basic-information" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Basic Information
          </a>
          <a 
            v-if="columnData.valid_values && Object.keys(columnData.valid_values).length > 0"
            href="#valid-values" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Valid Values
          </a>
          <a 
            v-if="columnData.value_lookup && columnData.value_lookup.length > 0"
            href="#value-lookup" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Values
          </a>
          <a 
            v-if="columnData.statistics"
            href="#statistics" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Statistics
          </a>
          <a 
            href="#technical-details" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Technical Details
          </a>
          <a 
            v-if="columnData.html_name"
            href="#codebook" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Codebook
          </a>
          <a 
            href="#json-data" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            JSON Data
          </a>
        </nav>
      </div>
      
      <!-- Main details -->
      <div class="grid gap-2">
        <!-- Basic Information -->
        <UCard id="basic-information" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">Basic Information</h2>
          </template>
          
          <div class="space-y-1">
            <div v-if="columnData.question">
              <h3 class="text-xs font-medium text-gray-700 mb-0.5">Question</h3>
              <p class="text-gray-900 text-sm">{{ columnData.question }}</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-2">
              <div>
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Section</h3>
                <p class="text-gray-900 text-sm">{{ columnData.section_name || 'Not specified' }}</p>
              </div>
              
              <div>
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Type</h3>
                <p class="text-gray-900 text-sm">{{ columnData.type_of_variable || 'Not specified' }}</p>
              </div>
              
              <div>
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Computed</h3>
                <p class="text-gray-900 text-sm">{{ formatBoolean(columnData.computed) }}</p>
              </div>
              
              <div>
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Suppress</h3>
                <p class="text-gray-900 text-sm">{{ formatBoolean(columnData.suppress) }}</p>
              </div>
            </div>
          </div>
        </UCard>
        
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
        
        <!-- Value Lookup -->
        <UCard id="value-lookup" v-if="columnData.value_lookup && columnData.value_lookup.length > 0" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">Values</h2>
          </template>
          
          <!-- Charts Section -->
          <div v-if="valueLookupTableData.some(item => typeof item.count === 'number' && item.count > 0)" class="mb-4">
            <UTabs 
              :items="[
                { label: 'Vertical Chart', slot: 'vertical', icon: 'i-heroicons-chart-bar' },
                { label: 'Horizontal Chart', slot: 'horizontal', icon: 'i-heroicons-chart-bar-square' }
              ]"
              class="mb-3"
            >
              <template #vertical>
                <div class="bg-gray-50 rounded-lg p-3">
                  <ResponseChartVertical 
                    :value-data="valueLookupTableData" 
                    title="Response Counts by Value"
                  />
                </div>
              </template>
              
              <template #horizontal>
                <div class="bg-gray-50 rounded-lg p-3">
                  <ResponseChartHorizontal 
                    :value-data="valueLookupTableData" 
                    title="Response Distribution"
                  />
                </div>
              </template>
            </UTabs>
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Value</th>
                  <th class="px-2 py-1 text-right text-xs font-medium text-gray-700">Count</th>
                  <th class="px-2 py-1 text-left text-xs font-medium text-gray-700">Description</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="(row, index) in valueLookupTableData" :key="index">
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
          </div>
        </UCard>
        
        <!-- Statistics -->
        <UCard id="statistics" v-if="columnData.statistics" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">Statistics</h2>
          </template>
          
          <div class="space-y-2">
            <!-- Basic statistics (common to both types) -->
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-2">
              <div>
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Count</h3>
                <p class="text-gray-900 text-sm">{{ columnData.statistics.count.toLocaleString() }}</p>
              </div>
              
              <div>
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Null Count</h3>
                <p class="text-gray-900 text-sm">{{ columnData.statistics.null_count.toLocaleString() }}</p>
              </div>
              
              <div v-if="columnData.statistics.unique_count !== undefined">
                <h3 class="text-xs font-medium text-gray-700 mb-0.5">Unique Values</h3>
                <p class="text-gray-900 text-sm">{{ columnData.statistics.unique_count.toLocaleString() }}</p>
              </div>
            </div>
            
            <!-- Numeric statistics -->
            <div v-if="'mean' in columnData.statistics" class="mt-3">
              <h3 class="text-xs font-medium text-gray-700 mb-1">Numeric Distribution</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-2">
                <div v-if="columnData.statistics.mean !== undefined && columnData.statistics.mean !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">Mean</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.mean.toLocaleString(undefined, {maximumFractionDigits: 4}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.median !== undefined && columnData.statistics.median !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">Median</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.median.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.std !== undefined && columnData.statistics.std !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">Std Dev</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.std.toLocaleString(undefined, {maximumFractionDigits: 4}) }}</p>
                </div>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-5 gap-2 mt-2">
                <div v-if="columnData.statistics.min !== undefined && columnData.statistics.min !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">Min</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.min.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.q25 !== undefined && columnData.statistics.q25 !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">25th %</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.q25.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.median !== undefined && columnData.statistics.median !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">50th %</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.median.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.q75 !== undefined && columnData.statistics.q75 !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">75th %</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.q75.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
                
                <div v-if="columnData.statistics.max !== undefined && columnData.statistics.max !== null">
                  <h3 class="text-xs font-medium text-gray-700 mb-0.5">Max</h3>
                  <p class="text-gray-900 text-sm">{{ columnData.statistics.max.toLocaleString(undefined, {maximumFractionDigits: 2}) }}</p>
                </div>
              </div>
            </div>
            
            <!-- Categorical statistics -->
            <div v-if="'top_values' in columnData.statistics && columnData.statistics.top_values.length > 0" class="mt-3">
              <h3 class="text-xs font-medium text-gray-700 mb-1">Top Values</h3>
              
              <div class="space-y-0.5">
                <div 
                  v-for="(valueInfo, index) in columnData.statistics.top_values.slice(0, 10)" 
                  :key="index"
                  class="flex items-start gap-2 py-0.5 border-b border-gray-100 last:border-0 text-sm"
                >
                  <span class="font-mono text-xs text-gray-600 min-w-[6rem] whitespace-nowrap">
                    {{ valueInfo.value }} ({{ valueInfo.count.toLocaleString() }})
                  </span>
                  <span v-if="valueInfo.description" class="text-gray-900 text-xs">
                    {{ valueInfo.description }}
                  </span>
                </div>
              </div>
              <div v-if="columnData.statistics.top_values.length > 10" class="text-xs text-gray-500 mt-1">
                Showing 10 of {{ columnData.statistics.top_values.length }} values
              </div>
            </div>
          </div>
        </UCard>
        
        <!-- Technical Details -->
        <UCard id="technical-details" :ui="{ body: { padding: 'p-2' }, header: { padding: 'p-2' } }">
          <template #header>
            <h2 class="text-base font-semibold">Technical Details</h2>
          </template>
          
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-2">
            <div v-if="columnData.sas_type">
              <h3 class="text-xs font-medium text-gray-700 mb-0.5">SAS Type</h3>
              <p class="text-gray-900 font-mono text-xs">{{ columnData.sas_type }}</p>
            </div>
            
            <div v-if="columnData.df_type">
              <h3 class="text-xs font-medium text-gray-700 mb-0.5">DataFrame Type</h3>
              <p class="text-gray-900 font-mono text-xs">{{ columnData.df_type }}</p>
            </div>
            
            <div v-if="columnData.tags">
              <h3 class="text-xs font-medium text-gray-700 mb-0.5">Tags</h3>
              <p class="text-gray-900 text-xs">{{ formatArray(columnData.tags) }}</p>
            </div>
            
            <div v-if="columnData.column_order !== undefined">
              <h3 class="text-xs font-medium text-gray-700 mb-0.5">Column Order</h3>
              <p class="text-gray-900 text-xs">{{ columnData.column_order }}</p>
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
          
          <div class="bg-gray-50 rounded-lg p-0.5">
            <iframe
              ref="codebookIframe"
              :src="`/html/codebook_USCODE23_LLCP_021924.HTML#${columnData.html_name}`"
              class="w-full h-[600px] bg-white rounded border border-gray-200"
              :title="`Codebook for ${columnData.label || columnData.key}`"
            />
          </div>
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