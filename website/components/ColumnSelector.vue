<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'

interface Props {
  columns: ColumnDef<any>[]
  modelValue: string[]
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

// State for expanding/collapsing
const isExpanded = ref(false)

// Get column display names
const columnOptions = computed(() => {
  return props.columns.map(col => ({
    id: col.accessorKey as string,
    label: col.header as string
  }))
})

// Handle column visibility toggle
const toggleColumn = (columnId: string) => {
  const currentVisible = [...props.modelValue]
  const index = currentVisible.indexOf(columnId)
  
  if (index > -1) {
    currentVisible.splice(index, 1)
  } else {
    currentVisible.push(columnId)
  }
  
  emit('update:modelValue', currentVisible)
}

// Remove column from visible list
const removeColumn = (columnId: string) => {
  const currentVisible = props.modelValue.filter(id => id !== columnId)
  emit('update:modelValue', currentVisible)
}

// Get label for column ID
const getColumnLabel = (columnId: string) => {
  const column = columnOptions.value.find(col => col.id === columnId)
  return column?.label || columnId
}
</script>

<template>
  <div class="mb-4">
    <div class="flex items-center justify-between">
      <!-- Left side: Column badges -->
      <div class="flex items-center gap-2 flex-wrap flex-1">
        <span class="text-sm font-medium text-gray-700 mr-2">Columns:</span>
        <UBadge 
          v-for="columnId in modelValue" 
          :key="columnId"
          color="primary"
          variant="soft"
          class="flex items-center gap-1"
        >
          {{ getColumnLabel(columnId) }}
          <UButton
            @click.stop="removeColumn(columnId)"
            variant="ghost"
            size="2xs"
            :padded="false"
            icon="i-heroicons-x-mark"
            class="ml-1 hover:bg-gray-200 rounded"
          />
        </UBadge>
      </div>
      
      <!-- Right side: Expand button -->
      <UButton
        @click="isExpanded = !isExpanded"
        variant="ghost"
        size="sm"
        :icon="isExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
      >
        {{ isExpanded ? 'Hide' : 'Select' }}
      </UButton>
    </div>
    
    <!-- Expanded checklist -->
    <div v-if="isExpanded" class="mt-3 pt-3 border-t border-gray-200">
      <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
        <label 
          v-for="option in columnOptions" 
          :key="option.id"
          class="flex items-center gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded"
        >
          <UCheckbox
            :model-value="modelValue.includes(option.id)"
            @update:model-value="toggleColumn(option.id)"
          />
          <span class="text-sm">{{ option.label }}</span>
        </label>
      </div>
    </div>
  </div>
</template>