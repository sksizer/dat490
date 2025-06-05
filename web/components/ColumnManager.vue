<script setup lang="ts">
import type { ColumnOrder } from './SortingManager.vue'

interface Props {
  visibleColumns: string[]
  columnOrdering: ColumnOrder[]
  columns: Array<{ accessorKey?: string; header?: string }>
  columnDisplayOrder: string[]
  totalFeatures: number
  filteredFeatures: number
  selectedFeatures: number
}

const props = defineProps<Props>()
const emit = defineEmits(['update:visibleColumns', 'update:columnOrdering', 'reset', 'update:columnDisplayOrder'])

// State for expanding/collapsing
const isExpanded = ref(false)

// Forward updates from column display manager
const handleVisibleColumnsUpdate = (newColumns: string[]) => {
  emit('update:visibleColumns', newColumns)
}

// Forward updates from column display order
const handleColumnDisplayOrderUpdate = (newOrder: string[]) => {
  emit('update:columnDisplayOrder', newOrder)
}

// Forward updates from sorting manager
const handleColumnOrderingUpdate = (newOrdering: ColumnOrder[]) => {
  emit('update:columnOrdering', newOrdering)
}

// Reset to initial state
const resetToDefaults = () => {
  emit('reset')
}

// Get visible column count
const visibleColumnCount = computed(() => props.visibleColumns.length)

// Get active sort count
const activeSortCount = computed(() => props.columnOrdering.length)
</script>

<template>
  <div class="w-full">
    <!-- Control header -->
    <div class="flex items-center justify-between w-full">
      <!-- Left side: feature count information -->
      <div class="flex items-center gap-3 text-xs text-gray-600">
        <span>
          Showing {{ filteredFeatures }} of {{ totalFeatures }} features
        </span>
        <span v-if="selectedFeatures > 0" class="font-medium text-primary-600 text-xs">
          {{ selectedFeatures }} selected for extraction
        </span>
      </div>
      
      <!-- Right side: controls -->
      <div class="flex items-center gap-2">
        <span class="text-sm text-gray-600">
          {{ visibleColumnCount }} visible
          <span v-if="activeSortCount > 0">, {{ activeSortCount }} sorted</span>
        </span>
        <UButton
          @click="resetToDefaults"
          variant="ghost"
          size="xs"
          icon="i-heroicons-arrow-path"
          title="Reset to default columns and sorting"
        >
          Reset
        </UButton>
        <UButton
          @click="isExpanded = !isExpanded"
          variant="ghost"
          size="xs"
          :icon="isExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
        >
          {{ isExpanded ? 'Hide' : 'Manage' }}
        </UButton>
      </div>
    </div>
    
    <!-- Expanded management section -->
    <div v-if="isExpanded" class="mt-2 pt-2 border-t border-gray-200 w-full">
      <div class="flex flex-col gap-6 w-full">
        <!-- Column Display Manager -->
        <div class="w-full">
          <h3 class="text-sm font-medium mb-2">Column Display</h3>
          <ColumnDisplayManager
            :visible-columns="visibleColumns"
            :columns="columns"
            :column-display-order="columnDisplayOrder"
            @update:visible-columns="handleVisibleColumnsUpdate"
            @update:column-display-order="handleColumnDisplayOrderUpdate"
          />
        </div>
        
        <!-- Sorting Manager -->
        <div class="w-full">
          <h3 class="text-sm font-medium mb-2">Sorting</h3>
          <SortingManager
            :column-ordering="columnOrdering"
            :columns="columns"
            @update:column-ordering="handleColumnOrderingUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>