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
const emit = defineEmits(['update:visibleColumns', 'update:columnOrdering', 'reset', 'update:columnOrder'])

// State for expanding/collapsing
const isExpanded = ref(false)

// Drag and drop state
const draggedItem = ref<string | null>(null)
const dragOverItem = ref<string | null>(null)

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

// Drag and drop handlers
const handleDragStart = (e: DragEvent, columnId: string) => {
  draggedItem.value = columnId
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', columnId)
  }
}

const handleDragOver = (e: DragEvent, columnId: string) => {
  e.preventDefault()
  if (e.dataTransfer) {
    e.dataTransfer.dropEffect = 'move'
  }
  dragOverItem.value = columnId
}

const handleDragLeave = () => {
  dragOverItem.value = null
}

const handleDrop = (e: DragEvent, targetColumnId: string) => {
  e.preventDefault()
  
  if (!draggedItem.value || draggedItem.value === targetColumnId) {
    draggedItem.value = null
    dragOverItem.value = null
    return
  }
  
  // Reorder the columns array
  const newColumns = [...props.columns]
  const draggedIndex = newColumns.findIndex(col => col.accessorKey === draggedItem.value)
  const targetIndex = newColumns.findIndex(col => col.accessorKey === targetColumnId)
  
  if (draggedIndex !== -1 && targetIndex !== -1) {
    // Remove the dragged item
    const [draggedColumn] = newColumns.splice(draggedIndex, 1)
    // Insert it at the target position
    newColumns.splice(targetIndex, 0, draggedColumn)
    
    // Emit the reordered columns
    emit('update:columnOrder', newColumns)
  }
  
  draggedItem.value = null
  dragOverItem.value = null
}

const handleDragEnd = () => {
  draggedItem.value = null
  dragOverItem.value = null
}
</script>

<template>
  <div>
    <!-- Control buttons -->
    <div class="flex items-center justify-end gap-2">
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
    
    <!-- Expanded column management -->
    <div v-if="isExpanded" class="mt-2 pt-2 border-t border-gray-200">
      <div class="text-xs text-gray-500 mb-1">Drag to reorder • Click checkbox to show/hide • Click arrows to sort</div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-1">
        <div 
          v-for="column in columns"
          :key="column.accessorKey"
          :draggable="true"
          @dragstart="handleDragStart($event, column.accessorKey!)"
          @dragover="handleDragOver($event, column.accessorKey!)"
          @dragleave="handleDragLeave"
          @drop="handleDrop($event, column.accessorKey!)"
          @dragend="handleDragEnd"
          :class="[
            'flex items-center gap-1 p-1 rounded cursor-move transition-all duration-150 text-xs',
            draggedItem === column.accessorKey ? 'opacity-50 scale-95' : '',
            dragOverItem === column.accessorKey ? 'bg-blue-50 border-2 border-blue-200' : 'hover:bg-gray-50 border-2 border-transparent'
          ]"
        >
          <!-- Drag handle -->
          <div class="text-gray-400 hover:text-gray-600">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M7 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM7 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4zM13 14a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/>
            </svg>
          </div>
          
          <!-- Visibility checkbox -->
          <UCheckbox
            :model-value="visibleColumns.includes(column.accessorKey!)"
            @update:model-value="toggleVisibility(column.accessorKey!)"
          />
          
          <!-- Column name -->
          <span class="text-sm flex-1 select-none">{{ column.header }}</span>
          
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