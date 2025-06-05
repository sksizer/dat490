<script setup lang="ts">
export interface ColumnOrder {
  columnId: string
  direction: 'asc' | 'desc'
}

interface Props {
  columns: Array<{ accessorKey?: string; header?: string }>
  modelValue: ColumnOrder[]
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

// Get label for column ID
const getColumnLabel = (columnId: string) => {
  const column = props.columns.find(col => col.accessorKey === columnId)
  return column?.header || columnId
}

// Remove ordering for a column
const removeOrdering = (columnId: string) => {
  const newOrdering = props.modelValue.filter(order => order.columnId !== columnId)
  emit('update:modelValue', newOrdering)
}

// Toggle direction for a column
const toggleDirection = (columnId: string) => {
  const newOrdering = props.modelValue.map(order => {
    if (order.columnId === columnId) {
      return {
        ...order,
        direction: order.direction === 'asc' ? 'desc' : 'asc'
      }
    }
    return order
  })
  emit('update:modelValue', newOrdering)
}
</script>

<template>
  <UCard v-if="modelValue.length > 0" class="mb-4" :ui="{ body: { padding: 'p-3' } }">
    <div class="flex items-center gap-2 flex-wrap">
      <span class="text-sm font-medium text-gray-700 mr-2">Sort by:</span>
      
      <div
        v-for="(order, index) in modelValue"
        :key="order.columnId"
        class="flex items-center gap-1"
      >
        <UBadge
          color="primary"
          variant="soft"
          class="flex items-center gap-1"
        >
          <span>{{ getColumnLabel(order.columnId) }}</span>
          
          <!-- Direction indicator/toggle -->
          <UButton
            @click="toggleDirection(order.columnId)"
            variant="ghost"
            size="2xs"
            :padded="false"
            :icon="order.direction === 'asc' ? 'i-heroicons-arrow-up' : 'i-heroicons-arrow-down'"
            class="ml-1 hover:bg-gray-200 rounded"
          />
          
          <!-- Remove button -->
          <UButton
            @click="removeOrdering(order.columnId)"
            variant="ghost"
            size="2xs"
            :padded="false"
            icon="i-heroicons-x-mark"
            class="ml-1 hover:bg-gray-200 rounded"
          />
        </UBadge>
        
        <!-- Add comma between items except last -->
        <span v-if="index < modelValue.length - 1" class="text-gray-500 text-sm">,</span>
      </div>
    </div>
  </UCard>
</template>