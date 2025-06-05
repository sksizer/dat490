<script setup lang="ts">
interface ColumnOrder {
  columnId: string
  direction: 'asc' | 'desc'
}

interface Props {
  visibleColumns: string[]
  columnOrdering: ColumnOrder[]
  columns: Array<{ accessorKey?: string; header?: string }>
}

const props = defineProps<Props>()
const emit = defineEmits(['update:visibleColumns', 'update:columnOrdering', 'reset'])

// State for expanding/collapsing
const isExpanded = ref(false)

// Get column display name
const getColumnLabel = (columnId: string) => {
  const column = props.columns.find(col => col.accessorKey === columnId)
  return column?.header || columnId
}

// Get sort state for a column
const getColumnSort = (columnId: string) => {
  return props.columnOrdering.find(order => order.columnId === columnId)
}

// Toggle column visibility
const toggleVisibility = (columnId: string) => {
  const currentVisible = [...props.visibleColumns]
  const index = currentVisible.indexOf(columnId)
  
  if (index > -1) {
    currentVisible.splice(index, 1)
  } else {
    currentVisible.push(columnId)
  }
  
  emit('update:visibleColumns', currentVisible)
}

// Handle sort cycling: none → asc → desc → none
const cycleSorting = (columnId: string) => {
  const currentOrdering = [...props.columnOrdering]
  const existingIndex = currentOrdering.findIndex(order => order.columnId === columnId)
  
  if (existingIndex > -1) {
    const currentOrder = currentOrdering[existingIndex]
    if (currentOrder.direction === 'asc') {
      // Change to descending
      currentOrdering[existingIndex] = { ...currentOrder, direction: 'desc' }
    } else {
      // Remove sorting (desc → none)
      currentOrdering.splice(existingIndex, 1)
    }
  } else {
    // Add ascending sort
    currentOrdering.push({ columnId, direction: 'asc' })
  }
  
  emit('update:columnOrdering', currentOrdering)
}

// Get visible column count
const visibleColumnCount = computed(() => props.visibleColumns.length)

// Get active sort count
const activeSortCount = computed(() => props.columnOrdering.length)

// Remove specific column from visibility
const removeColumn = (columnId: string) => {
  const currentVisible = props.visibleColumns.filter(id => id !== columnId)
  emit('update:visibleColumns', currentVisible)
}

// Reset to initial state
const resetToDefaults = () => {
  emit('reset')
}
</script>

<template>
  <div class="mb-4">
    <div class="flex items-center justify-between">
      <!-- Left side: Visible column badges -->
      <div class="flex items-center gap-2 flex-wrap flex-1">
        <span class="text-sm font-medium text-gray-700 mr-2">Columns:</span>
        <UBadge 
          v-for="columnId in visibleColumns" 
          :key="columnId"
          color="primary"
          variant="soft"
          class="flex items-center gap-1"
        >
          {{ getColumnLabel(columnId) }}
          
          <!-- Sort indicator/toggle -->
          <UButton
            @click.stop="cycleSorting(columnId)"
            variant="ghost"
            size="2xs"
            :padded="false"
            :icon="getColumnSort(columnId)?.direction === 'asc' ? 'i-heroicons-arrow-up' : 
                   getColumnSort(columnId)?.direction === 'desc' ? 'i-heroicons-arrow-down' : 
                   'i-heroicons-arrows-up-down'"
            :class="[
              'ml-1 rounded',
              getColumnSort(columnId) ? 'text-primary-600 hover:bg-primary-100' : 'text-gray-400 hover:bg-gray-200'
            ]"
            :title="getColumnSort(columnId)?.direction === 'asc' ? 'Sorted ascending - click for descending' :
                    getColumnSort(columnId)?.direction === 'desc' ? 'Sorted descending - click to remove sort' :
                    'Click to sort ascending'"
          />
          
          <!-- Remove button -->
          <UButton
            @click.stop="removeColumn(columnId)"
            variant="ghost"
            size="2xs"
            :padded="false"
            icon="i-heroicons-x-mark"
            class="ml-1 hover:bg-gray-200 rounded"
            title="Hide column"
          />
        </UBadge>
      </div>
      
      <!-- Right side: Controls -->
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-500">
          {{ visibleColumnCount }} visible
          <span v-if="activeSortCount > 0">, {{ activeSortCount }} sorted</span>
        </span>
        <UButton
          @click="resetToDefaults"
          variant="ghost"
          size="sm"
          icon="i-heroicons-arrow-path"
          title="Reset to default columns and sorting"
        >
          Reset
        </UButton>
        <UButton
          @click="isExpanded = !isExpanded"
          variant="ghost"
          size="sm"
          :icon="isExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
        >
          {{ isExpanded ? 'Hide' : 'Manage' }}
        </UButton>
      </div>
    </div>
    
    <!-- Expanded column management -->
    <div v-if="isExpanded" class="mt-3 pt-3 border-t border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
        <div 
          v-for="column in columns"
          :key="column.accessorKey"
          class="flex items-center gap-2 p-2 rounded hover:bg-gray-50"
        >
          <!-- Visibility checkbox -->
          <UCheckbox
            :model-value="visibleColumns.includes(column.accessorKey!)"
            @update:model-value="toggleVisibility(column.accessorKey!)"
          />
          
          <!-- Column name -->
          <span class="text-sm flex-1">{{ column.header }}</span>
          
          <!-- Sort controls -->
          <div class="flex items-center gap-1">
            <UButton
              @click="cycleSorting(column.accessorKey!)"
              variant="ghost"
              size="2xs"
              :padded="false"
              :icon="getColumnSort(column.accessorKey!)?.direction === 'asc' ? 'i-heroicons-arrow-up' : 
                     getColumnSort(column.accessorKey!)?.direction === 'desc' ? 'i-heroicons-arrow-down' : 
                     'i-heroicons-arrows-up-down'"
              :class="[
                'rounded',
                getColumnSort(column.accessorKey!) ? 'text-primary-600 hover:bg-primary-100' : 'text-gray-400 hover:bg-gray-200'
              ]"
              :title="getColumnSort(column.accessorKey!)?.direction === 'asc' ? 'Sorted ascending' :
                      getColumnSort(column.accessorKey!)?.direction === 'desc' ? 'Sorted descending' :
                      'Not sorted'"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>