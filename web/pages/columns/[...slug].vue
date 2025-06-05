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
          <a 
            href="#top" 
            class="text-xs font-medium text-gray-600 hover:text-gray-900 whitespace-nowrap transition-colors"
          >
            Start
          </a>
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
            Value Lookup
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
            <h2 class="text-base font-semibold">Value Lookup</h2>
          </template>
          
          <div class="space-y-0.5">
            <div 
              v-for="(value, index) in columnData.value_lookup" 
              :key="index"
              class="flex items-start gap-2 py-0.5 border-b border-gray-100 last:border-0 text-sm"
            >
              <!-- ValueRange has start and end properties -->
              <template v-if="'start' in value && 'end' in value">
                <span class="font-mono text-xs text-gray-600 min-w-[6rem]">
                  {{ value.start === value.end ? value.start : `${value.start} - ${value.end}` }}
                </span>
              </template>
              <!-- ValueDef has only description -->
              <template v-else>
                <span class="font-mono text-xs text-gray-600 min-w-[2.5rem]">{{ index + 1 }}</span>
              </template>
              <span class="text-gray-900 text-xs">{{ value.description }}</span>
            </div>
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