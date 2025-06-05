<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import type { ColumnOrder } from '~/components/OrderingSelector.vue'

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

// Ordering state
const columnOrdering = ref<ColumnOrder[]>([])

// Add or toggle column ordering when header is clicked
const handleHeaderClick = (columnId: string) => {
  const existingIndex = columnOrdering.value.findIndex(order => order.columnId === columnId)
  
  if (existingIndex > -1) {
    // Column already in ordering - toggle direction
    const currentOrder = columnOrdering.value[existingIndex]
    if (currentOrder.direction === 'asc') {
      columnOrdering.value[existingIndex] = { ...currentOrder, direction: 'desc' }
    } else {
      // Remove from ordering if already desc
      columnOrdering.value.splice(existingIndex, 1)
    }
  } else {
    // Add new ordering
    columnOrdering.value.push({ columnId, direction: 'asc' })
  }
}

// Helper to create sortable header
const createSortableHeader = (columnId: string, label: string) => {
  return () => {
    const orderInfo = columnOrdering.value.find(o => o.columnId === columnId)
    return h('button', {
      class: 'flex items-center gap-1 hover:text-gray-900 transition-colors',
      onClick: () => handleHeaderClick(columnId)
    }, [
      h('span', label),
      orderInfo && h('span', { class: 'text-xs' }, 
        orderInfo.direction === 'asc' ? '↑' : '↓'
      )
    ])
  }
}

// Column metadata for labels
const columnMetadata = {
  key: 'Column/Feature',
  label: 'Label',
  sas_variable_name: 'SAS Variable',
  section_name: 'Section',
  type_of_variable: 'Type',
  question: 'Question',
  computed: 'Computed'
}

// Define table columns
const columns: ColumnDef<any>[] = [
  {
    accessorKey: 'key',
    header: createSortableHeader('key', 'Column/Feature'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm' }, row.original.key),
  },
  {
    accessorKey: 'label',
    header: createSortableHeader('label', 'Label'),
  },
  {
    accessorKey: 'sas_variable_name',
    header: createSortableHeader('sas_variable_name', 'SAS Variable'),
    cell: ({ row }) => h('span', { class: 'font-mono text-sm' }, row.original.sas_variable_name),
  },
  {
    accessorKey: 'section_name',
    header: createSortableHeader('section_name', 'Section'),
    cell: ({ row }) => row.original.section_name || '-',
  },
  {
    accessorKey: 'type_of_variable',
    header: createSortableHeader('type_of_variable', 'Type'),
    cell: ({ row }) => row.original.type_of_variable || '-',
  },
  {
    accessorKey: 'question',
    header: createSortableHeader('question', 'Question'),
    cell: ({ row }) => {
      const question = row.original.question
      if (!question) return '-'
      // Truncate long questions
      return question.length > 100 ? question.substring(0, 100) + '...' : question
    },
  },
  {
    accessorKey: 'computed',
    header: createSortableHeader('computed', 'Computed'),
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

// Generate pandas snippet based on filtered columns
const pandasSnippet = computed(() => {
  const columnKeys = filteredData.value.map(item => `'${item.key}'`)
  if (columnKeys.length === 0) return ''
  
  // Format for readability - if more than 5 columns, use multiline format
  if (columnKeys.length > 5) {
    const formattedColumns = columnKeys.map(col => `    ${col}`).join(',\n')
    return `# Extract ${columnKeys.length} columns from DataFrame
selected_columns = [
${formattedColumns}
]
df_filtered = df[selected_columns]`
  } else {
    return `# Extract ${columnKeys.length} columns from DataFrame
selected_columns = [${columnKeys.join(', ')}]
df_filtered = df[selected_columns]`
  }
})

// Copy to clipboard function
const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(pandasSnippet.value)
    // You might want to add a toast notification here
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// State for expanding/collapsing the snippet
const isSnippetExpanded = ref(false)

// Generate truncated version of the snippet
const truncatedSnippet = computed(() => {
  const columnKeys = filteredData.value.map(item => `'${item.key}'`)
  if (columnKeys.length === 0) return ''
  
  // For truncated version, show first 3 columns
  const displayColumns = columnKeys.slice(0, 3)
  const remainingCount = columnKeys.length - 3
  
  if (columnKeys.length <= 3) {
    return `selected_columns = [${displayColumns.join(', ')}]`
  } else {
    return `selected_columns = [${displayColumns.join(', ')}, ... # +${remainingCount} more]`
  }
})

// Visible columns state - all except SAS Variable by default
const visibleColumns = ref([
  'key',
  'label',
  // 'sas_variable_name', // Excluded by default
  'section_name',
  'type_of_variable',
  'question',
  'computed'
])

// Filter columns based on visibility
const visibleTableColumns = computed(() => {
  return columns.filter(col => 
    visibleColumns.value.includes(col.accessorKey as string)
  )
})

// Columns with string headers for selector components
const columnsForSelectors = computed(() => {
  return columns.map(col => ({
    accessorKey: col.accessorKey,
    header: columnMetadata[col.accessorKey as keyof typeof columnMetadata]
  }))
})

// Apply sorting to filtered data
const sortedFilteredData = computed(() => {
  if (columnOrdering.value.length === 0) return filteredData.value
  
  const sorted = [...filteredData.value]
  
  // Sort by each column in order
  sorted.sort((a, b) => {
    for (const order of columnOrdering.value) {
      const aVal = a[order.columnId]
      const bVal = b[order.columnId]
      
      // Handle null/undefined
      if (aVal == null && bVal == null) continue
      if (aVal == null) return order.direction === 'asc' ? 1 : -1
      if (bVal == null) return order.direction === 'asc' ? -1 : 1
      
      // Compare values
      let comparison = 0
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.toLowerCase().localeCompare(bVal.toLowerCase())
      } else {
        comparison = aVal > bVal ? 1 : aVal < bVal ? -1 : 0
      }
      
      if (comparison !== 0) {
        return order.direction === 'asc' ? comparison : -comparison
      }
    }
    return 0
  })
  
  return sorted
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

    <!-- Pandas DataFrame Snippet -->
    <div v-if="pandasSnippet" class="mb-6">
      <UCard>
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-semibold text-gray-700">Pandas DataFrame Extraction</h3>
          <div class="flex items-center gap-2">
            <UButton 
              v-if="filteredData.length > 3"
              @click="isSnippetExpanded = !isSnippetExpanded" 
              variant="ghost" 
              size="sm"
              :icon="isSnippetExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
            >
              {{ isSnippetExpanded ? 'Collapse' : 'Expand' }}
            </UButton>
            <UButton 
              @click="copyToClipboard" 
              variant="ghost" 
              size="sm"
              icon="i-heroicons-clipboard-document"
            >
              Copy
            </UButton>
          </div>
        </div>
        <pre class="bg-gray-100 p-4 rounded-md overflow-x-auto text-sm"><code>{{ isSnippetExpanded ? pandasSnippet : truncatedSnippet }}</code></pre>
      </UCard>
    </div>

    <!-- Column Selector -->
    <ColumnSelector 
      v-model="visibleColumns"
      :columns="columnsForSelectors"
    />

    <!-- Ordering Selector -->
    <OrderingSelector
      v-model="columnOrdering"
      :columns="columnsForSelectors"
    />

    <UCard>
      <UTable
        :key="`${visibleColumns.join(',')}-${columnOrdering.map(o => `${o.columnId}:${o.direction}`).join(',')}`"
        :data="sortedFilteredData"
        :columns="visibleTableColumns"
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