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
    const sortStatus = orderInfo 
      ? `Sorted ${orderInfo.direction === 'asc' ? 'ascending' : 'descending'}`
      : 'Click to sort'
    
    return h('button', {
      class: 'flex items-center gap-1 hover:text-gray-900 transition-colors',
      onClick: () => handleHeaderClick(columnId),
      title: `${label} - ${sortStatus}`
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
    accessorKey: '_navigation',
    header: () => h('div', { 
      title: 'Open column details in new tab',
      class: 'flex items-center justify-center'
    }, [
      h(resolveComponent('UIcon'), { 
        name: 'i-heroicons-arrow-top-right-on-square',
        class: 'w-4 h-4 text-gray-500'
      })
    ]),
    cell: ({ row }) => h(resolveComponent('NuxtLink'), {
      to: `/columns/${row.original.sas_variable_name || row.original.key}`,
      target: '_blank',
      class: 'inline-flex items-center justify-center p-1 rounded hover:bg-gray-100 transition-colors',
      title: `View details for ${row.original.label || row.original.key}`
    }, () => h(resolveComponent('UIcon'), { 
      name: 'i-heroicons-arrow-top-right-on-square',
      class: 'w-4 h-4 text-gray-600'
    })),
  },
  {
    accessorKey: '_selection',
    header: () => {
      return h('div', { class: 'relative inline-block' }, [
        h('input', {
          type: 'checkbox',
          checked: allVisibleSelected.value,
          indeterminate: someVisibleSelected.value,
          onChange: (e: Event) => {
            const target = e.target as HTMLInputElement
            if (target.checked) {
              selectAllVisible()
            } else {
              deselectAll()
            }
          },
          title: 'Select columns for Pandas DataFrame extraction\n\n• Check to select all visible columns\n• Uncheck to deselect all\n• Selected columns will appear in the Pandas extraction code above',
          class: 'rounded border-gray-300 cursor-pointer'
        })
      ])
    },
    cell: ({ row }) => h('input', {
      type: 'checkbox',
      checked: selectedRows.value.has(row.original.key),
      onChange: () => toggleRowSelection(row.original.key),
      class: 'rounded border-gray-300'
    }),
  },
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

// Selection state - tracks which row keys are selected
const selectedRows = ref<Set<string>>(new Set())

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

// Get selected rows that are currently visible (filtered)
const selectedVisibleRows = computed(() => {
  const visibleKeys = new Set(filteredData.value.map(item => item.key))
  return Array.from(selectedRows.value).filter(key => visibleKeys.has(key))
})

// Watch for filter changes and deselect hidden rows
watch(filteredData, (newFilteredData) => {
  const visibleKeys = new Set(newFilteredData.map(item => item.key))
  const currentSelected = Array.from(selectedRows.value)
  
  // Remove any selected rows that are no longer visible
  currentSelected.forEach(key => {
    if (!visibleKeys.has(key)) {
      selectedRows.value.delete(key)
    }
  })
})

// Helper functions for selection
const toggleRowSelection = (key: string) => {
  if (selectedRows.value.has(key)) {
    selectedRows.value.delete(key)
  } else {
    selectedRows.value.add(key)
  }
}

const selectAllVisible = () => {
  filteredData.value.forEach(item => {
    selectedRows.value.add(item.key)
  })
}

const deselectAll = () => {
  selectedRows.value.clear()
}

// Check if all visible rows are selected
const allVisibleSelected = computed(() => {
  if (filteredData.value.length === 0) return false
  return filteredData.value.every(item => selectedRows.value.has(item.key))
})

// Check if some but not all visible rows are selected
const someVisibleSelected = computed(() => {
  if (filteredData.value.length === 0) return false
  const selectedCount = filteredData.value.filter(item => selectedRows.value.has(item.key)).length
  return selectedCount > 0 && selectedCount < filteredData.value.length
})

// Generate pandas snippet based on selected columns
const pandasSnippet = computed(() => {
  // Use selected visible rows, or fall back to all filtered data if none selected
  const rowsToUse = selectedVisibleRows.value.length > 0 
    ? filteredData.value.filter(item => selectedVisibleRows.value.includes(item.key))
    : filteredData.value
    
  const columnKeys = rowsToUse.map(item => `'${item.key}'`)
  if (columnKeys.length === 0) return ''
  
  // Add comment about selection
  const selectionComment = selectedVisibleRows.value.length > 0 
    ? `# Extract ${columnKeys.length} selected columns from DataFrame`
    : `# Extract ${columnKeys.length} columns from DataFrame (select specific columns for custom extraction)`
  
  // Format for readability - if more than 5 columns, use multiline format
  if (columnKeys.length > 5) {
    const formattedColumns = columnKeys.map(col => `    ${col}`).join(',\n')
    return `${selectionComment}
selected_columns = [
${formattedColumns}
]
df_filtered = df[selected_columns]`
  } else {
    return `${selectionComment}
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
  // Use selected visible rows, or fall back to all filtered data if none selected
  const rowsToUse = selectedVisibleRows.value.length > 0 
    ? filteredData.value.filter(item => selectedVisibleRows.value.includes(item.key))
    : filteredData.value
    
  const columnKeys = rowsToUse.map(item => `'${item.key}'`)
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

// Filter columns based on visibility - always include _navigation and _selection columns
const visibleTableColumns = computed(() => {
  return columns.filter(col => 
    col.accessorKey === '_navigation' || 
    col.accessorKey === '_selection' || 
    visibleColumns.value.includes(col.accessorKey as string)
  )
})

// Columns with string headers for selector components - exclude _navigation and _selection columns
const columnsForSelectors = computed(() => {
  return columns
    .filter(col => col.accessorKey !== '_selection' && col.accessorKey !== '_navigation')
    .map(col => ({
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
  <div class="container mx-auto py-4">
    <h1 class="text-2xl font-bold mb-3">BRFSS Model Columns</h1>
    <UContainer id="bfrssLinks">Links: <ul><li><ULink to='/html/codebook_USCODE23_LLCP_021924.HTML' target="_blank">Codebook</ULink></li></ul></UContainer>
    
    <ModelMetadataSummary :model-data="modelData" />
    
    <div class="mb-4">
      <UInput 
        v-model="search" 
        placeholder="Search columns..." 
        icon="i-heroicons-magnifying-glass"
        size="md"
        class="max-w-md"
      />
    </div>

    <!-- Pandas DataFrame Snippet -->
    <div v-if="pandasSnippet" class="mb-4">
      <UCard :ui="{ body: { padding: 'p-3' } }">
        <div class="flex items-center justify-between mb-1">
          <div class="flex items-center gap-3">
            <h3 class="text-sm font-semibold text-gray-700">Pandas DataFrame Extraction</h3>
            <div v-if="selectedVisibleRows.length > 0" class="flex items-center gap-2">
              <UBadge color="primary" variant="soft">
                {{ selectedVisibleRows.length }} column{{ selectedVisibleRows.length !== 1 ? 's' : '' }} selected
              </UBadge>
              <button
                @click="deselectAll"
                class="text-xs text-gray-500 hover:text-gray-700"
              >
                Clear selection
              </button>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <UButton 
              v-if="filteredData.length > 3 || selectedVisibleRows.length > 3"
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
        <pre class="bg-gray-100 p-2 rounded-md overflow-x-auto text-sm"><code>{{ isSnippetExpanded ? pandasSnippet : truncatedSnippet }}</code></pre>
      </UCard>
    </div>

    <!-- Ordering Selector -->
    <OrderingSelector
      v-model="columnOrdering"
      :columns="columnsForSelectors"
    />

    <!-- Column Selector -->
    <ColumnSelector 
      v-model="visibleColumns"
      :columns="columnsForSelectors"
    />

    <UCard :ui="{ body: { padding: 'p-3' } }">
      <div v-if="filteredData.length > 0" class="flex items-center justify-between mb-2 text-sm text-gray-600">
        <span>
          Showing {{ filteredData.length }} of {{ tableData.length }} columns
        </span>
        <span v-if="selectedVisibleRows.length > 0" class="font-medium text-primary-600">
          {{ selectedVisibleRows.length }} selected for extraction
        </span>
      </div>
      
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