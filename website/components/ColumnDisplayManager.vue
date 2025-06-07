<script setup lang="ts">
interface Props {
  visibleColumns: string[]
  columns: Array<{ accessorKey?: string; header?: string }>
  columnDisplayOrder: string[]
}

const props = defineProps<Props>()
const emit = defineEmits(['update:visibleColumns', 'update:columnDisplayOrder'])

// No expansion needed as parent handles it

// Drag and drop state
const draggedItem = ref<string | null>(null)
const dragOverItem = ref<string | null>(null)

// Get column display name
const getColumnLabel = (columnId: string) => {
  const column = props.columns.find(col => col.accessorKey === columnId)
  return column?.header || columnId
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

// Get visible column count
const visibleColumnCount = computed(() => props.visibleColumns.length)

// Reset to initial state (handled by parent)
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
    
    // Create new display order from the reordered columns
    const newDisplayOrder = newColumns.map(col => col.accessorKey!).filter(Boolean)
    emit('update:columnDisplayOrder', newDisplayOrder)
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
  <div class="w-full">
    <div class="text-xs text-gray-500 mb-1">Drag to reorder • Click checkbox to show/hide</div>
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
        </div>
      </div>
  </div>
</template>