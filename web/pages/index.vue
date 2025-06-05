<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'

// Fetch the model data
const { data: modelData } = await useAsyncData('model', () => {
  const val = queryCollection('columns').first()
return val; }
)

// Transform the columns object into an array for the table
const tableData = computed(() => {
  if (!modelData.value?.columns) return []
  
  return Object.entries(modelData.value.columns).map(([key, value]) => ({
    key,
    ...value
  }))
})

// Define table columns
const columns: ColumnDef<any>[] = [
  {
    accessorKey: 'key',
    header: 'Variable Name',
    cell: ({ row }) => h('span', { class: 'font-mono text-sm' }, row.original.key),
  },
  {
    accessorKey: 'label',
    header: 'Label',
  },
  {
    accessorKey: 'sas_variable_name',
    header: 'SAS Variable',
    cell: ({ row }) => h('span', { class: 'font-mono text-sm' }, row.original.sas_variable_name),
  },
  {
    accessorKey: 'section_name',
    header: 'Section',
    cell: ({ row }) => row.original.section_name || '-',
  },
  {
    accessorKey: 'type_of_variable',
    header: 'Type',
    cell: ({ row }) => row.original.type_of_variable || '-',
  },
  {
    accessorKey: 'question',
    header: 'Question',
    cell: ({ row }) => {
      const question = row.original.question
      if (!question) return '-'
      // Truncate long questions
      return question.length > 100 ? question.substring(0, 100) + '...' : question
    },
  },
  {
    accessorKey: 'computed',
    header: 'Computed',
    cell: ({ row }) => h('span', { 
      class: row.original.computed ? 'text-green-600' : 'text-gray-500' 
    }, row.original.computed ? 'Yes' : 'No'),
  },
]

// Search state
const search = ref('')

// Filtered data based on search
const filteredData = computed(() => {
  if (!search.value) return tableData.value
  
  const searchLower = search.value.toLowerCase()
  return tableData.value.filter(item => 
    item.key.toLowerCase().includes(searchLower) ||
    item.label.toLowerCase().includes(searchLower) ||
    item.sas_variable_name.toLowerCase().includes(searchLower) ||
    (item.question && item.question.toLowerCase().includes(searchLower)) ||
    (item.section_name && item.section_name.toLowerCase().includes(searchLower))
  )
})
</script>

<template>
  <div class="container mx-auto py-8">
    <h1 class="text-3xl font-bold mb-6">BRFSS Model Columns</h1>
    
    <ModelMetadataSummary :model-data="modelData" />
    
    <div class="mb-6">
      <UInput 
        v-model="search" 
        placeholder="Search columns..." 
        icon="i-heroicons-magnifying-glass"
        size="lg"
        class="max-w-md"
      />
    </div>

    <UCard>
      <UTable
        :data="filteredData"
        :columns="columns"
        :loading="!modelData"
        class="w-full"
      >
        <template #empty-state>
          <div class="text-center py-8">
            <p class="text-gray-500">No columns found</p>
          </div>
        </template>
      </UTable>
    </UCard>
  </div>
</template>

<style scoped>
</style>