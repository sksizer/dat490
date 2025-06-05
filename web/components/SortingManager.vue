<script setup lang="ts">
export interface ColumnOrder {
  columnId: string
  direction: 'asc' | 'desc'
}

interface Props {
  columnOrdering: ColumnOrder[]
  columns: Array<{ accessorKey?: string; header?: string }>
}

const props = defineProps<Props>()
const emit = defineEmits(['update:columnOrdering'])

// No expansion needed as parent handles it

// Get column display name
const getColumnLabel = (columnId: string) => {
  const column = props.columns.find(col => col.accessorKey === columnId)
  return column?.header || columnId
}

// Get sort state for a column
const getColumnSort = (columnId: string) => {
  return props.columnOrdering.find(order => order.columnId === columnId)
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

// Get active sort count
const activeSortCount = computed(() => props.columnOrdering.length)

// Remove specific column from sorting
const removeSort = (columnId: string) => {
  const currentOrdering = props.columnOrdering.filter(order => order.columnId !== columnId)
  emit('update:columnOrdering', currentOrdering)
}
</script>

<template>
  <div class="w-full">
    <!-- Active sort display -->
    <div v-if="columnOrdering.length > 0" class="mb-2 flex flex-wrap gap-1">
      <UBadge
        v-for="order in columnOrdering"
        :key="order.columnId"
        color="primary"
        variant="soft"
        class="flex items-center gap-1"
      >
        {{ getColumnLabel(order.columnId) }}
        <UIcon 
          :name="order.direction === 'asc' ? 'i-heroicons-arrow-up' : 'i-heroicons-arrow-down'"
          class="w-3 h-3"
        />
        <UButton
          @click="removeSort(order.columnId)"
          variant="ghost"
          size="2xs"
          :padded="false"
          icon="i-heroicons-x-mark"
          class="ml-1 hover:bg-gray-200 rounded"
        />
      </UBadge>
    </div>
    
    <div class="text-xs text-gray-500 mb-1">Click to change sort order</div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-1">
        <div 
          v-for="column in columns"
          :key="column.accessorKey"
          class="flex items-center gap-1 p-1 rounded hover:bg-gray-50 border-2 border-transparent text-xs"
        >
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
</template>