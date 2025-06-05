<script setup lang="ts">
interface FilterOptions {
  sections: string[]
  types: string[]
  computed: string[]
}

interface Props {
  modelValue: {
    sections: string[]
    types: string[]
    computed: string[]
  }
  options: FilterOptions
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

// State for expanding/collapsing
const isExpanded = ref(false)

// Handle filter changes
const updateFilter = (filterType: keyof FilterOptions, value: string, checked: boolean) => {
  const currentFilters = { ...props.modelValue }
  
  if (checked) {
    if (!currentFilters[filterType].includes(value)) {
      currentFilters[filterType] = [...currentFilters[filterType], value]
    }
  } else {
    currentFilters[filterType] = currentFilters[filterType].filter(item => item !== value)
  }
  
  emit('update:modelValue', currentFilters)
}

// Clear all filters
const clearAllFilters = () => {
  emit('update:modelValue', {
    sections: [],
    types: [],
    computed: []
  })
}

// Check if any filters are active
const hasActiveFilters = computed(() => {
  return props.modelValue.sections.length > 0 || 
         props.modelValue.types.length > 0 || 
         props.modelValue.computed.length > 0
})

// Get active filter count
const activeFilterCount = computed(() => {
  return props.modelValue.sections.length + 
         props.modelValue.types.length + 
         props.modelValue.computed.length
})

// Remove specific filter
const removeFilter = (filterType: keyof FilterOptions, value: string) => {
  updateFilter(filterType, value, false)
}

// Check if all items in a filter category are selected
const isAllSelected = (filterType: keyof FilterOptions) => {
  const available = props.options[filterType]
  const selected = props.modelValue[filterType]
  return available.length > 0 && selected.length === available.length
}

// Check if some but not all items in a filter category are selected
const isSomeSelected = (filterType: keyof FilterOptions) => {
  const available = props.options[filterType]
  const selected = props.modelValue[filterType]
  return selected.length > 0 && selected.length < available.length
}

// Select all items in a filter category
const selectAll = (filterType: keyof FilterOptions) => {
  const currentFilters = { ...props.modelValue }
  currentFilters[filterType] = [...props.options[filterType]]
  emit('update:modelValue', currentFilters)
}

// Deselect all items in a filter category
const selectNone = (filterType: keyof FilterOptions) => {
  const currentFilters = { ...props.modelValue }
  currentFilters[filterType] = []
  emit('update:modelValue', currentFilters)
}

// Handle select all/none toggle
const toggleSelectAll = (filterType: keyof FilterOptions) => {
  if (isAllSelected(filterType)) {
    selectNone(filterType)
  } else {
    selectAll(filterType)
  }
}
</script>

<template>
  <UCard class="mb-4" :ui="{ body: { padding: 'p-3' } }">
    <div class="flex items-center justify-between">
      <!-- Left side: Active filters or placeholder -->
      <div class="flex items-center gap-2 flex-wrap flex-1">
        <span class="text-sm font-medium text-gray-700 mr-2">Filters:</span>
        
        <template v-if="hasActiveFilters">
          <!-- Section filters -->
          <UBadge 
            v-for="section in modelValue.sections"
            :key="`section-${section}`"
            color="blue"
            variant="soft"
            class="flex items-center gap-1"
          >
            Section: {{ section }}
            <UButton
              @click="removeFilter('sections', section)"
              variant="ghost"
              size="2xs"
              :padded="false"
              icon="i-heroicons-x-mark"
              class="ml-1 hover:bg-gray-200 rounded"
            />
          </UBadge>
          
          <!-- Type filters -->
          <UBadge 
            v-for="type in modelValue.types"
            :key="`type-${type}`"
            color="green"
            variant="soft"
            class="flex items-center gap-1"
          >
            Type: {{ type }}
            <UButton
              @click="removeFilter('types', type)"
              variant="ghost"
              size="2xs"
              :padded="false"
              icon="i-heroicons-x-mark"
              class="ml-1 hover:bg-gray-200 rounded"
            />
          </UBadge>
          
          <!-- Computed filters -->
          <UBadge 
            v-for="computed in modelValue.computed"
            :key="`computed-${computed}`"
            color="purple"
            variant="soft"
            class="flex items-center gap-1"
          >
            Computed: {{ computed }}
            <UButton
              @click="removeFilter('computed', computed)"
              variant="ghost"
              size="2xs"
              :padded="false"
              icon="i-heroicons-x-mark"
              class="ml-1 hover:bg-gray-200 rounded"
            />
          </UBadge>
          
          <button
            v-if="hasActiveFilters"
            @click="clearAllFilters"
            class="text-xs text-gray-500 hover:text-gray-700 ml-2"
          >
            Clear all
          </button>
        </template>
        
        <span v-else class="text-sm text-gray-500">No filters applied</span>
      </div>
      
      <!-- Right side: Expand button -->
      <div class="flex items-center gap-2">
        <span v-if="activeFilterCount > 0" class="text-xs text-gray-500">
          {{ activeFilterCount }} active
        </span>
        <UButton
          @click="isExpanded = !isExpanded"
          variant="ghost"
          size="sm"
          :icon="isExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
        >
          {{ isExpanded ? 'Hide' : 'Filter' }}
        </UButton>
      </div>
    </div>
    
    <!-- Expanded filter options -->
    <div v-if="isExpanded" class="mt-3 pt-3 border-t border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Section filters -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-medium text-gray-700">Section</h4>
            <div class="flex items-center gap-1">
              <input
                type="checkbox"
                :checked="isAllSelected('sections')"
                :indeterminate="isSomeSelected('sections')"
                @change="toggleSelectAll('sections')"
                title="Select all sections / Deselect all"
                class="rounded border-gray-300 text-xs"
              />
              <span class="text-xs text-gray-500">All</span>
            </div>
          </div>
          <div class="space-y-1 max-h-40 overflow-y-auto">
            <label 
              v-for="section in options.sections"
              :key="section"
              class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
            >
              <UCheckbox
                :model-value="modelValue.sections.includes(section)"
                @update:model-value="(checked) => updateFilter('sections', section, checked)"
              />
              <span class="text-sm">{{ section || 'No section' }}</span>
            </label>
          </div>
        </div>
        
        <!-- Type filters -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-medium text-gray-700">Type</h4>
            <div class="flex items-center gap-1">
              <input
                type="checkbox"
                :checked="isAllSelected('types')"
                :indeterminate="isSomeSelected('types')"
                @change="toggleSelectAll('types')"
                title="Select all types / Deselect all"
                class="rounded border-gray-300 text-xs"
              />
              <span class="text-xs text-gray-500">All</span>
            </div>
          </div>
          <div class="space-y-1 max-h-40 overflow-y-auto">
            <label 
              v-for="type in options.types"
              :key="type"
              class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
            >
              <UCheckbox
                :model-value="modelValue.types.includes(type)"
                @update:model-value="(checked) => updateFilter('types', type, checked)"
              />
              <span class="text-sm">{{ type || 'No type' }}</span>
            </label>
          </div>
        </div>
        
        <!-- Computed filters -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-medium text-gray-700">Computed</h4>
            <div class="flex items-center gap-1">
              <input
                type="checkbox"
                :checked="isAllSelected('computed')"
                :indeterminate="isSomeSelected('computed')"
                @change="toggleSelectAll('computed')"
                title="Select all computed options / Deselect all"
                class="rounded border-gray-300 text-xs"
              />
              <span class="text-xs text-gray-500">All</span>
            </div>
          </div>
          <div class="space-y-1">
            <label 
              v-for="computed in options.computed"
              :key="computed"
              class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
            >
              <UCheckbox
                :model-value="modelValue.computed.includes(computed)"
                @update:model-value="(checked) => updateFilter('computed', computed, checked)"
              />
              <span class="text-sm">{{ computed }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>