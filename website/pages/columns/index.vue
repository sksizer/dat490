<script setup lang="ts">
import type { ColumnDef } from '@tanstack/vue-table'
import type { ColumnOrder } from '~/components/OrderingSelector.vue'
import site from '~/model/site'

// Fetch the model data
const { data: modelData } = await useAsyncData('model', () => {
  const val = queryCollection('columns').first()
return val; }
)

// Fetch feature importance summary data
const { data: featureImportanceData } = await useAsyncData('feature-importance', () => {
  return queryCollection('feature_importance_summary').first()
})

// Transform the columns object into an array for the table
const tableData = computed(() => {
  if (!modelData.value?.columns) return []
  
  return Object.entries(modelData.value.columns).map(([key, value]) => ({
    key,
    ...value
  }))
})

// Default column configuration
const defaultVisibleColumns = [
  'count',
  'key',
  'demographic_analysis_score',
  'label',
  'section_name',
  // 'sas_variable_name', // Excluded by default
  'type_of_variable',
  'question',
  'computed'
]

const defaultColumnOrdering = [
  { columnId: 'count', direction: 'desc' as const },
  { columnId: 'key', direction: 'asc' as const }
]

// Default column display order
const defaultColumnOrder = [
  'count',
  'key',
  'demographic_analysis_score',
  'label',
  'section_name',
  'sas_variable_name',
  'type_of_variable',
  'question',
  'computed'
]

// Ordering state - default to sorting by Count (desc) then Column/Feature
const columnOrdering = ref<ColumnOrder[]>([...defaultColumnOrdering])

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
      class: 'flex items-center gap-1 hover:text-gray-900 transition-colors text-xs font-medium',
      onClick: () => handleHeaderClick(columnId),
      title: `${label} - ${sortStatus}`
    }, [
      h('span', label),
      // Always show an icon, but style depends on sort status
      h(resolveComponent('UIcon'), { 
        name: orderInfo 
          ? (orderInfo.direction === 'asc' ? 'i-heroicons-arrow-up' : 'i-heroicons-arrow-down')
          : 'i-heroicons-arrows-up-down',
        class: orderInfo 
          ? 'w-3 h-3' 
          : 'w-3 h-3 text-gray-300' // Light grey for unsorted columns
      })
    ])
  }
}

// Column metadata for labels
const columnMetadata = {
  key: 'Column/Feature',
  demographic_analysis_score: 'Demographic Analysis',
  label: 'Label',
  sas_variable_name: 'SAS Variable',
  section_name: 'Section',
  type_of_variable: 'Type',
  count: 'Valid Responses',
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
        class: 'w-3 h-3 text-gray-500'
      })
    ]),
    cell: ({ row }) => h(resolveComponent('NuxtLink'), {
      to: `/columns/${row.original.sas_variable_name || row.original.key}`,
      target: '_blank',
      class: 'inline-flex items-center justify-center p-0.5 rounded hover:bg-gray-100 transition-colors',
      title: `View details for ${row.original.label || row.original.key}`
    }, () => h(resolveComponent('UIcon'), { 
      name: 'i-heroicons-arrow-top-right-on-square',
      class: 'w-3 h-3 text-gray-600'
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
          class: 'rounded border-gray-300 cursor-pointer w-3 h-3'
        })
      ])
    },
    cell: ({ row }) => h('input', {
      type: 'checkbox',
      checked: selectedRows.value.has(row.original.key),
      onChange: () => toggleRowSelection(row.original.key),
      class: 'rounded border-gray-300 w-3 h-3'
    }),
  },
  {
    accessorKey: 'key',
    header: createSortableHeader('key', 'Column/Feature'),
    cell: ({ row }) => h('span', { class: 'font-mono text-xs' }, row.original.key),
  },
  {
    accessorKey: 'demographic_analysis_score',
    header: () => {
      return h('div', { class: 'flex items-center gap-1' }, [
        createSortableHeader('demographic_analysis_score', 'Demographic Analysis')(),
        h(resolveComponent('NuxtLink'), {
          to: '/demographic_analysis',
          class: 'text-gray-400 hover:text-gray-600 transition-colors',
          title: 'Learn about demographic analysis methodology'
        }, () => h(resolveComponent('UIcon'), { 
          name: 'i-heroicons-question-mark-circle',
          class: 'w-3 h-3'
        }))
      ])
    },
    cell: ({ row }) => {
      const score = row.original.demographic_analysis_score
      const columnKey = row.original.key
      
      if (score === null || score === undefined) return '-'
      
      // Create clickable link to analysis results
      return h(resolveComponent('NuxtLink'), {
        to: `/columns/${columnKey}/demographic-analysis`,
        class: 'inline-flex items-center gap-1 font-medium text-sm text-blue-600 hover:text-blue-800 hover:underline transition-colors',
        title: `View demographic analysis details for ${columnKey}\nRandom Forest accuracy: ${(score * 100).toFixed(1)}%`
      }, [
        h('span', `${(score * 100).toFixed(1)}%`),
        h(resolveComponent('UIcon'), { 
          name: 'i-heroicons-arrow-top-right-on-square',
          class: 'w-3 h-3'
        })
      ])
    },
  },
  {
    accessorKey: 'label',
    header: createSortableHeader('label', 'Label'),
    cell: ({ row }) => {
      const label = row.original.label
      if (!label) return '-'
      
      // For long labels, show truncated text with tooltip
      if (label.length > site.columnSettings.labelTruncationLength) {
        return h('span', { 
          title: label, // Full text as tooltip
          class: 'cursor-help'
        }, label.substring(0, site.columnSettings.labelTruncationLength) + '...')
      }
      
      return label
    },
  },
  {
    accessorKey: 'sas_variable_name',
    header: createSortableHeader('sas_variable_name', 'SAS Variable'),
    cell: ({ row }) => h('span', { class: 'font-mono text-xs' }, row.original.sas_variable_name),
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
    accessorKey: 'count',
    header: createSortableHeader('count', 'Valid Responses'),
    cell: ({ row }) => {
      if (!row.original.statistics) return '-'
      
      const stats = row.original.statistics
      const validCount = stats.count
      const totalResponses = stats.total_responses
      const missingCount = stats.missing_count || 0
      
      // Show valid count prominently, with total and missing info in tooltip
      return h('span', {
        title: `Valid responses: ${validCount.toLocaleString()}\nTotal responses: ${totalResponses.toLocaleString()}\nMissing/refused: ${missingCount.toLocaleString()}\nNull values: ${stats.null_count.toLocaleString()}`,
        class: 'cursor-help'
      }, [
        h('span', { class: 'font-medium' }, validCount.toLocaleString()),
        missingCount > 0 ? h('span', { 
          class: 'text-xs text-gray-500 ml-1' 
        }, `(${totalResponses.toLocaleString()})`) : null
      ])
    },
  },
  {
    accessorKey: 'question',
    header: createSortableHeader('question', 'Question'),
    cell: ({ row }) => {
      const question = row.original.question
      if (!question) return '-'
      
      // For long questions, show truncated text with tooltip
      if (question.length > site.columnSettings.questionTruncationLength) {
        return h('span', { 
          title: question, // Full text as tooltip
          class: 'cursor-help'
        }, question.substring(0, site.columnSettings.questionTruncationLength) + '...')
      }
      
      return question
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

// URL and navigation
const route = useRoute()
const router = useRouter()

// Search state
const search = ref('')

// Selection state - tracks which row keys are selected
const selectedRows = ref<Set<string>>(new Set())

// Filter state
const filters = ref({
  sections: [] as string[],
  types: [] as string[],
  computed: [] as string[]
})

// Check if we're in section filter mode
const isFilteredBySection = computed(() => {
  return !!(route.query.section)
})

// Get the active section name
const activeSection = computed(() => {
  return route.query.section as string || null
})

// Initialize filters from URL parameter
const initializeFiltersFromURL = () => {
  const sectionParam = route.query.section as string
  if (sectionParam) {
    filters.value.sections = [sectionParam]
    // Optionally clear other filters to focus on the section
    // filters.value.types = []
    // filters.value.computed = []
  }
}

// Watch for URL parameter changes
watch(() => route.query.section, (newSection) => {
  if (newSection && typeof newSection === 'string') {
    // Update filters when URL parameter changes
    filters.value.sections = [newSection]
  } else if (!newSection) {
    // Clear section filter if parameter is removed
    filters.value.sections = []
  }
})


// Get unique filter options from data
const filterOptions = computed(() => {
  const sections = new Set<string>()
  const types = new Set<string>()
  const computed = new Set<string>()
  
  tableData.value.forEach(item => {
    if (item.section_name) sections.add(item.section_name)
    if (item.type_of_variable) types.add(item.type_of_variable)
    computed.add(item.computed ? 'Yes' : 'No')
  })
  
  return {
    sections: Array.from(sections).sort(),
    types: Array.from(types).sort(),
    computed: Array.from(computed).sort()
  }
})

// Filtered data based on search and filters
const filteredData = computed(() => {
  let data = tableData.value
  
  // Apply search filter
  if (search.value) {
    const searchLower = search.value.toLowerCase()
    data = data.filter(item => 
      item.key.toLowerCase().includes(searchLower) ||
      item.label.toLowerCase().includes(searchLower) ||
      item.sas_variable_name.toLowerCase().includes(searchLower) ||
      (item.question && item.question.toLowerCase().includes(searchLower)) ||
      (item.section_name && item.section_name.toLowerCase().includes(searchLower))
    )
  }
  
  // Apply section filter
  if (filters.value.sections.length > 0) {
    data = data.filter(item => 
      filters.value.sections.includes(item.section_name || '')
    )
  }
  
  // Apply type filter
  if (filters.value.types.length > 0) {
    data = data.filter(item => 
      filters.value.types.includes(item.type_of_variable || '')
    )
  }
  
  // Apply computed filter
  if (filters.value.computed.length > 0) {
    data = data.filter(item => {
      const computedValue = item.computed ? 'Yes' : 'No'
      return filters.value.computed.includes(computedValue)
    })
  }
  
  return data
})

// Get selected rows that are currently visible (filtered)
const selectedVisibleRows = computed(() => {
  const visibleKeys = new Set(filteredData.value.map(item => item.key))
  return Array.from(selectedRows.value).filter(key => visibleKeys.has(key))
})

// Data for observation count chart - use selected rows if any are selected, otherwise use filtered data
const observationCountData = computed(() => {
  if (selectedVisibleRows.value.length > 0) {
    // Show only selected rows
    return sortedFilteredData.value.filter(item => selectedRows.value.has(item.key))
  } else {
    // Show all filtered data
    return sortedFilteredData.value
  }
})

// Statistical analysis of observation counts including semantic nulls
const observationStatsAnalysis = computed(() => {
  const validColumns = observationCountData.value.filter(item => item.statistics != null)
  
  if (validColumns.length === 0) {
    return null
  }
  
  // Calculate totals
  const totalValidResponses = validColumns.reduce((sum, item) => sum + (item.statistics?.count || 0), 0)
  const totalMissingResponses = validColumns.reduce((sum, item) => sum + (item.statistics?.missing_count || 0), 0)
  const totalNullResponses = validColumns.reduce((sum, item) => sum + (item.statistics?.null_count || 0), 0)
  
  // Get total possible responses (should be consistent across columns)
  const totalPossibleResponses = validColumns[0]?.statistics?.total_responses || 0
  const totalPossibleAcrossAllColumns = totalPossibleResponses * validColumns.length
  
  // Calculate semantic nulls (missing + null)
  const totalSemanticNulls = totalMissingResponses + totalNullResponses
  
  // Calculate percentages per column correctly accounting for skip logic
  const columnRates = validColumns.map(item => {
    const validForColumn = item.statistics?.count || 0
    const missingForColumn = item.statistics?.missing_count || 0
    const nullForColumn = item.statistics?.null_count || 0
    const totalAsked = validForColumn + missingForColumn  // Only people who were actually asked
    const totalInDataset = 433323  // Total survey respondents
    
    return {
      // Of people asked this question, what % gave valid responses
      validRate: totalAsked > 0 ? (validForColumn / totalAsked) * 100 : 0,
      // Of people asked this question, what % refused/didn't know
      missingRate: totalAsked > 0 ? (missingForColumn / totalAsked) * 100 : 0,
      // Of all survey respondents, what % weren't asked this question
      nullRate: (nullForColumn / totalInDataset) * 100,
      // Of all survey respondents, what % have unusable data (missing + null)
      semanticNullRate: ((missingForColumn + nullForColumn) / totalInDataset) * 100
    }
  })
  
  // Average the rates across columns
  const validResponseRate = columnRates.length > 0 ? columnRates.reduce((sum, rates) => sum + rates.validRate, 0) / columnRates.length : 0
  const missingResponseRate = columnRates.length > 0 ? columnRates.reduce((sum, rates) => sum + rates.missingRate, 0) / columnRates.length : 0
  const nullResponseRate = columnRates.length > 0 ? columnRates.reduce((sum, rates) => sum + rates.nullRate, 0) / columnRates.length : 0
  const semanticNullRate = columnRates.length > 0 ? columnRates.reduce((sum, rates) => sum + rates.semanticNullRate, 0) / columnRates.length : 0
  
  // Calculate per-column averages
  const avgValidPerColumn = validColumns.length > 0 ? totalValidResponses / validColumns.length : 0
  const avgMissingPerColumn = validColumns.length > 0 ? totalMissingResponses / validColumns.length : 0
  const avgNullPerColumn = validColumns.length > 0 ? totalNullResponses / validColumns.length : 0
  
  // Find columns with highest/lowest completion rates
  const columnCompletionRates = validColumns.map(item => ({
    key: item.key,
    label: item.label || item.key,
    validCount: item.statistics?.count || 0,
    missingCount: item.statistics?.missing_count || 0,
    nullCount: item.statistics?.null_count || 0,
    totalResponses: item.statistics?.total_responses || 0,
    completionRate: item.statistics?.total_responses ? ((item.statistics.count || 0) / item.statistics.total_responses) * 100 : 0
  })).sort((a, b) => b.completionRate - a.completionRate)
  
  const highestCompletion = columnCompletionRates[0]
  const lowestCompletion = columnCompletionRates[columnCompletionRates.length - 1]
  
  // Distribution analysis
  const completionBuckets = {
    excellent: columnCompletionRates.filter(c => c.completionRate >= 95).length,
    good: columnCompletionRates.filter(c => c.completionRate >= 80 && c.completionRate < 95).length,
    fair: columnCompletionRates.filter(c => c.completionRate >= 60 && c.completionRate < 80).length,
    poor: columnCompletionRates.filter(c => c.completionRate < 60).length
  }
  
  // Calculate descriptive statistics for valid response counts
  const validCounts = validColumns.map(item => item.statistics?.count || 0)
  const sortedValidCounts = [...validCounts].sort((a, b) => a - b)
  
  const minValid = Math.min(...validCounts)
  const maxValid = Math.max(...validCounts)
  const meanValid = validCounts.reduce((sum, count) => sum + count, 0) / validCounts.length
  
  // Standard deviation calculation
  const variance = validCounts.reduce((sum, count) => sum + Math.pow(count - meanValid, 2), 0) / validCounts.length
  const stdDevValid = Math.sqrt(variance)
  
  // Median calculation
  const medianValid = sortedValidCounts.length % 2 === 0
    ? (sortedValidCounts[sortedValidCounts.length / 2 - 1] + sortedValidCounts[sortedValidCounts.length / 2]) / 2
    : sortedValidCounts[Math.floor(sortedValidCounts.length / 2)]
  
  // Quartiles
  const q1Index = Math.floor(sortedValidCounts.length * 0.25)
  const q3Index = Math.floor(sortedValidCounts.length * 0.75)
  const q1Valid = sortedValidCounts[q1Index]
  const q3Valid = sortedValidCounts[q3Index]
  
  // Completion rate statistics
  const completionRates = columnCompletionRates.map(c => c.completionRate)
  const sortedCompletionRates = [...completionRates].sort((a, b) => a - b)
  
  const minCompletion = Math.min(...completionRates)
  const maxCompletion = Math.max(...completionRates)
  const meanCompletion = completionRates.reduce((sum, rate) => sum + rate, 0) / completionRates.length
  
  const completionVariance = completionRates.reduce((sum, rate) => sum + Math.pow(rate - meanCompletion, 2), 0) / completionRates.length
  const stdDevCompletion = Math.sqrt(completionVariance)
  
  const medianCompletion = sortedCompletionRates.length % 2 === 0
    ? (sortedCompletionRates[sortedCompletionRates.length / 2 - 1] + sortedCompletionRates[sortedCompletionRates.length / 2]) / 2
    : sortedCompletionRates[Math.floor(sortedCompletionRates.length / 2)]
  
  return {
    columnCount: validColumns.length,
    totalPossibleResponses,
    totalValidResponses,
    totalMissingResponses,
    totalNullResponses,
    totalSemanticNulls,
    validResponseRate,
    missingResponseRate,
    nullResponseRate,
    semanticNullRate,
    avgValidPerColumn,
    avgMissingPerColumn,
    avgNullPerColumn,
    highestCompletion,
    lowestCompletion,
    completionBuckets,
    columnCompletionRates,
    // Descriptive statistics for valid response counts
    validCountStats: {
      min: minValid,
      max: maxValid,
      mean: meanValid,
      median: medianValid,
      stdDev: stdDevValid,
      q1: q1Valid,
      q3: q3Valid
    },
    // Descriptive statistics for completion rates
    completionRateStats: {
      min: minCompletion,
      max: maxCompletion,
      mean: meanCompletion,
      median: medianCompletion,
      stdDev: stdDevCompletion
    }
  }
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
  
  // Add comment about selection and filtering
  let selectionComment = ''
  if (selectedVisibleRows.value.length > 0) {
    selectionComment = `# Extract ${columnKeys.length} selected features from DataFrame`
  } else {
    const hasFilters = filters.value.sections.length > 0 || 
                      filters.value.types.length > 0 || 
                      filters.value.computed.length > 0 ||
                      search.value.length > 0
    
    if (hasFilters) {
      selectionComment = `# Extract ${columnKeys.length} filtered features from DataFrame`
    } else {
      selectionComment = `# Extract ${columnKeys.length} features from DataFrame (select specific features for custom extraction)`
    }
  }
  
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

// State for expanding/collapsing the snippet - default to collapsed for density
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
  
  // Add context about what type of features these are
  let prefix = ''
  if (selectedVisibleRows.value.length > 0) {
    prefix = `# ${columnKeys.length} selected features\n`
  } else {
    const hasFilters = filters.value.sections.length > 0 || 
                      filters.value.types.length > 0 || 
                      filters.value.computed.length > 0 ||
                      search.value.length > 0
    if (hasFilters) {
      prefix = `# ${columnKeys.length} filtered features\n`
    }
  }
  
  if (columnKeys.length <= 3) {
    return `${prefix}selected_columns = [${displayColumns.join(', ')}]`
  } else {
    return `${prefix}selected_columns = [${displayColumns.join(', ')}, ... # +${remainingCount} more]`
  }
})

// Visible columns state - all except SAS Variable by default
const visibleColumns = ref([...defaultVisibleColumns])

// Column display order state
const columnDisplayOrder = ref([...defaultColumnOrder])

// Filter columns based on visibility and order them according to columnDisplayOrder
const visibleTableColumns = computed(() => {
  const filteredColumns = columns.filter(col => 
    col.accessorKey === '_navigation' || 
    col.accessorKey === '_selection' || 
    visibleColumns.value.includes(col.accessorKey as string)
  )
  
  // Separate navigation/selection columns from data columns
  const navColumns = filteredColumns.filter(col => 
    col.accessorKey === '_navigation' || col.accessorKey === '_selection'
  )
  const dataColumns = filteredColumns.filter(col => 
    col.accessorKey !== '_navigation' && col.accessorKey !== '_selection'
  )
  
  // Sort data columns based on display order
  const orderedDataColumns = dataColumns.sort((a, b) => {
    const aIndex = columnDisplayOrder.value.indexOf(a.accessorKey as string)
    const bIndex = columnDisplayOrder.value.indexOf(b.accessorKey as string)
    return aIndex - bIndex
  })
  
  // Return navigation/selection columns first, then ordered data columns
  return [...navColumns, ...orderedDataColumns]
})

// Columns with string headers for selector components - exclude _navigation and _selection columns
// Ordered based on the current display order
const columnsForSelectors = computed(() => {
  const baseColumns = columns
    .filter(col => col.accessorKey !== '_selection' && col.accessorKey !== '_navigation')
    .map(col => ({
      accessorKey: col.accessorKey,
      header: columnMetadata[col.accessorKey as keyof typeof columnMetadata]
    }))
  
  // Sort based on the current display order
  return baseColumns.sort((a, b) => {
    const aIndex = columnDisplayOrder.value.indexOf(a.accessorKey!)
    const bIndex = columnDisplayOrder.value.indexOf(b.accessorKey!)
    return aIndex - bIndex
  })
})

// Apply sorting to filtered data
const sortedFilteredData = computed(() => {
  if (columnOrdering.value.length === 0) return filteredData.value
  
  const sorted = [...filteredData.value]
  
  // Sort by each column in order
  sorted.sort((a, b) => {
    for (const order of columnOrdering.value) {
      let aVal, bVal;
      
      // Special handling for nested properties like statistics.count
      if (order.columnId === 'count') {
        aVal = a.statistics?.count
        bVal = b.statistics?.count
      } else {
        aVal = a[order.columnId]
        bVal = b[order.columnId]
      }
      
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

// Reset columns and sorting to default state
const resetColumnsToDefault = () => {
  visibleColumns.value = [...defaultVisibleColumns]
  columnOrdering.value = [...defaultColumnOrdering]
  columnDisplayOrder.value = [...defaultColumnOrder]
}

// Handle column reordering from drag and drop
const handleColumnReorder = (newColumnOrder: string[]) => {
  columnDisplayOrder.value = newColumnOrder
}

// Set the breadcrumbs
const { setBreadcrumbs, clearBreadcrumbs } = usePageTitle()

// Update breadcrumbs based on section filter
const updateBreadcrumbs = () => {
  const baseBreadcrumbs = [
    {
      label: 'BFRSS Features',
      to: '/columns'
    }
  ]
  
  const sectionParam = route.query.section as string
  if (sectionParam) {
    baseBreadcrumbs.push({
      label: `Section: ${sectionParam}`,
      to: `/columns?section=${encodeURIComponent(sectionParam)}`
    })
  }
  
  setBreadcrumbs(baseBreadcrumbs)
}

// Set breadcrumbs when component mounts
onMounted(() => {
  initializeFiltersFromURL()
  updateBreadcrumbs()
})

// Watch for section parameter changes to update breadcrumbs
watch(() => route.query.section, () => {
  updateBreadcrumbs()
})

// Clear breadcrumbs when component unmounts
onUnmounted(() => {
  clearBreadcrumbs()
})

// Handle image loading errors for demographic analysis charts
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  
  // Show fallback message
  const container = img.parentElement
  if (container) {
    container.innerHTML = '<div class="text-gray-500 text-center p-4 text-xs">Visualization not available</div>'
  }
}
</script>

<template>
  <div class="container mx-auto py-2 mobile-compact">
<!--    <h1 class="text-2xl font-bold mb-2">BRFSS Feature Metadatas</h1>-->
<!--    <UContainer id="bfrssLinks">Links: <ul><li><ULink to='/html/codebook_USCODE23_LLCP_021924.HTML' target="_blank">Codebook</ULink></li></ul></UContainer>-->
<!--    -->
    <!-- Only show metadata summary when not filtering by section -->
    <ModelMetadataSummary 
      v-if="!isFilteredBySection" 
      :model-data="modelData" 
      :feature-importance-data="featureImportanceData" 
    />
    
    <!-- Observation Count Chart -->
    <div class="mb-4">
      <UCard :ui="{ body: { padding: 'p-3' }, header: { padding: 'p-3' } }">
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-base font-semibold">Observation Counts</h2>
            <UBadge 
              :color="selectedVisibleRows.length > 0 ? 'primary' : 'gray'" 
              variant="soft"
            >
              {{ sortedFilteredData.length }} feature{{ sortedFilteredData.length !== 1 ? 's' : '' }}
              <span v-if="selectedVisibleRows.length > 0">
                ({{ selectedVisibleRows.length }} selected)
              </span>
              <span v-else-if="filters.sections.length > 0 || filters.types.length > 0 || filters.computed.length > 0 || search.length > 0">
                (filtered)
              </span>
            </UBadge>
          </div>
        </template>
        
        <!-- Statistical Analysis Summary -->
        <div v-if="observationStatsAnalysis" class="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <h4 class="font-medium text-blue-900 mb-3">Data Completeness Analysis</h4>
          
          <!-- Key Metrics Grid -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div class="text-center p-2 bg-green-50 rounded border border-green-200">
              <div class="text-sm font-bold text-green-700">
                {{ observationStatsAnalysis.validResponseRate.toFixed(1) }}%
              </div>
              <div class="text-xs text-green-600">Valid Responses</div>
            </div>
            
            <div class="text-center p-2 bg-yellow-50 rounded border border-yellow-200">
              <div class="text-sm font-bold text-yellow-700">
                {{ observationStatsAnalysis.missingResponseRate.toFixed(1) }}%
              </div>
              <div class="text-xs text-yellow-600">Missing/Refused</div>
            </div>
            
            <div class="text-center p-2 bg-red-50 rounded border border-red-200">
              <div class="text-sm font-bold text-red-700">
                {{ observationStatsAnalysis.nullResponseRate.toFixed(1) }}%
              </div>
              <div class="text-xs text-red-600">Null Values</div>
            </div>
            
            <div class="text-center p-2 bg-gray-50 rounded border border-gray-200">
              <div class="text-sm font-bold text-gray-700">
                {{ observationStatsAnalysis.semanticNullRate.toFixed(1) }}%
              </div>
              <div class="text-xs text-gray-600">Semantic Nulls</div>
            </div>
          </div>
          
          <!-- Descriptive Statistics -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Valid Response Count Statistics -->
            <div class="p-2 bg-white rounded border">
              <h5 class="font-medium text-gray-800 mb-2 text-sm">Valid Response Count Statistics</h5>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-600">Mean:</span>
                  <span class="font-mono">{{ Math.round(observationStatsAnalysis.validCountStats.mean).toLocaleString() }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Std Dev:</span>
                  <span class="font-mono">{{ Math.round(observationStatsAnalysis.validCountStats.stdDev).toLocaleString() }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Median:</span>
                  <span class="font-mono">{{ Math.round(observationStatsAnalysis.validCountStats.median).toLocaleString() }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">IQR:</span>
                  <span class="font-mono">{{ Math.round(observationStatsAnalysis.validCountStats.q1).toLocaleString() }}-{{ Math.round(observationStatsAnalysis.validCountStats.q3).toLocaleString() }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Min:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.validCountStats.min.toLocaleString() }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Max:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.validCountStats.max.toLocaleString() }}</span>
                </div>
              </div>
            </div>
            
            <!-- Completion Rate Statistics -->
            <div class="p-2 bg-white rounded border">
              <h5 class="font-medium text-gray-800 mb-2 text-sm">Completion Rate Statistics</h5>
              <div class="grid grid-cols-2 gap-2 text-xs">
                <div class="flex justify-between">
                  <span class="text-gray-600">Mean:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.completionRateStats.mean.toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Std Dev:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.completionRateStats.stdDev.toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Median:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.completionRateStats.median.toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Range:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.completionRateStats.min.toFixed(1) }}%-{{ observationStatsAnalysis.completionRateStats.max.toFixed(1) }}%</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Excellent:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.completionBuckets.excellent }} (≥95%)</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-600">Poor:</span>
                  <span class="font-mono">{{ observationStatsAnalysis.completionBuckets.poor }} (<60%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bg-gray-50 rounded-lg p-3">
          <ObservationCountChart 
            :data="observationCountData" 
            :title="`Observation Counts${selectedVisibleRows.length > 0 ? ` (${selectedVisibleRows.length} selected)` : isFilteredBySection ? ` - ${activeSection}` : (filters.sections.length > 0 || filters.types.length > 0 || filters.computed.length > 0 || search.length > 0 ? ' (Filtered)' : '')}`"
            :filter-zero-counts="false"
          />
        </div>
      </UCard>
    </div>


    <div class="mb-2">
      <UInput 
        v-model="search" 
        placeholder="Search features..." 
        icon="i-heroicons-magnifying-glass"
        size="sm"
        class="max-w-sm"
      />
    </div>

    <!-- Section Filter Indicator -->
    <div v-if="isFilteredBySection" class="mb-2">
      <UAlert 
        color="blue" 
        variant="soft"
        :title="`Filtered by Section: ${activeSection}`"
        :description="`Showing ${sortedFilteredData.length} features from this section`"
        :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'gray', variant: 'link', padded: false }"
        @close="router.push('/columns')"
      />
    </div>

    <!-- Column Filter -->
    <ColumnFilter 
      v-model="filters"
      :options="filterOptions"
    />

    <!-- Pandas DataFrame Snippet -->
    <div v-if="pandasSnippet" class="mb-2">
      <UCard :ui="{ body: { padding: 'p-2' } }">
        <div class="flex items-center justify-between mb-1">
          <div class="flex items-center gap-2">
            <h3 class="text-xs font-semibold text-gray-700">Pandas DataFrame Extraction</h3>
            <div class="flex items-center gap-1">
              <UBadge 
                :color="selectedVisibleRows.length > 0 ? 'primary' : 'gray'" 
                variant="soft"
              >
                {{ filteredData.length }} feature{{ filteredData.length !== 1 ? 's' : '' }}
                <span v-if="selectedVisibleRows.length > 0">
                  ({{ selectedVisibleRows.length }} selected)
                </span>
                <span v-else-if="filters.sections.length > 0 || filters.types.length > 0 || filters.computed.length > 0 || search.length > 0">
                  (filtered)
                </span>
              </UBadge>
              <button
                v-if="selectedVisibleRows.length > 0"
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
              size="xs"
              :icon="isSnippetExpanded ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
            >
              {{ isSnippetExpanded ? 'Collapse' : 'Expand' }}
            </UButton>
            <UButton 
              @click="copyToClipboard" 
              variant="ghost" 
              size="xs"
              icon="i-heroicons-clipboard-document"
            >
              Copy
            </UButton>
          </div>
        </div>
        <pre class="bg-gray-100 p-1 rounded-md overflow-x-auto text-xs"><code>{{ isSnippetExpanded ? pandasSnippet : truncatedSnippet }}</code></pre>
      </UCard>
    </div>

    <UCard :ui="{ body: { padding: 'p-3' } }">
      <!-- Table management controls -->
      <div v-if="filteredData.length > 0" class="mb-2">
        <ColumnManager
          :visible-columns="visibleColumns"
          :column-ordering="columnOrdering"
          :columns="columnsForSelectors"
          :column-display-order="columnDisplayOrder"
          :total-features="tableData.length"
          :filtered-features="filteredData.length"
          :selected-features="selectedVisibleRows.length"
          @update:visible-columns="visibleColumns = $event"
          @update:column-ordering="columnOrdering = $event"
          @update:column-display-order="handleColumnReorder"
          @reset="resetColumnsToDefault"
        />
      </div>
      
      <UTable
        :key="`${visibleColumns.join(',')}-${columnOrdering.map(o => `${o.columnId}:${o.direction}`).join(',')}-${columnDisplayOrder.join(',')}`"
        :data="sortedFilteredData"
        :columns="visibleTableColumns"
        :loading="!modelData"
        class="w-full text-sm compact-table"
        :ui="{
          th: { padding: 'px-2 py-0.5' },
          td: { padding: 'px-2 py-0.5' },
          tbody: 'divide-y divide-gray-200'
        }"
      >
        <template #empty-state>
          <div class="text-center py-8">
            <p class="text-gray-500">No features found</p>
          </div>
        </template>
      </UTable>
    </UCard>

    <!-- Demographic Analysis Insights (moved to bottom) - Hide when filtering by section -->
    <div v-if="featureImportanceData && !isFilteredBySection" class="mt-6">
      <UCard :ui="{ body: { padding: 'p-3' }, header: { padding: 'p-3' } }">
        <template #header>
          <div class="flex items-center justify-between">
            <h2 class="text-base font-semibold">Demographic Analysis Summary</h2>
            <div class="flex items-center gap-2">
              <UBadge color="blue" variant="soft">
                {{ featureImportanceData.successful_analyses }} analyses
              </UBadge>
              <NuxtLink 
                to="/demographic-analysis"
                class="text-xs text-primary-600 hover:text-primary-700 flex items-center gap-0.5 font-medium"
              >
                View Full Analysis
                <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-3 h-3" />
              </NuxtLink>
            </div>
          </div>
        </template>
        
        <div class="space-y-3">
          <!-- Condensed Summary Statistics -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="text-center p-2 bg-blue-50 rounded-lg">
              <div class="text-base font-bold text-blue-700">
                {{ (featureImportanceData.average_accuracy * 100).toFixed(1) }}%
              </div>
              <div class="text-xs text-blue-600">Avg Accuracy</div>
            </div>
            <div class="text-center p-2 bg-green-50 rounded-lg">
              <div class="text-base font-bold text-green-700">
                {{ featureImportanceData.successful_analyses }}
              </div>
              <div class="text-xs text-green-600">Analyses</div>
            </div>
            <div class="text-center p-2 bg-purple-50 rounded-lg">
              <div class="text-base font-bold text-purple-700">
                {{ featureImportanceData.sections_analyzed.length }}
              </div>
              <div class="text-xs text-purple-600">Sections</div>
            </div>
            <div class="text-center p-2 bg-orange-50 rounded-lg">
              <div class="text-base font-bold text-orange-700">
                {{ featureImportanceData.top_features.length }}
              </div>
              <div class="text-xs text-orange-600">Features</div>
            </div>
          </div>
          
          <!-- Top 5 Predictors Preview -->
          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">Top 5 Demographic Predictors</h4>
            <div class="bg-gray-50 rounded-lg p-2">
              <div class="space-y-1">
                <div 
                  v-for="(feature, index) in featureImportanceData.top_features.slice(0, 5)" 
                  :key="feature.feature"
                  class="flex justify-between items-center p-1.5 bg-white rounded text-xs"
                >
                  <div class="flex items-center gap-2">
                    <span class="w-5 h-5 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-xs font-bold">
                      {{ index + 1 }}
                    </span>
                    <NuxtLink 
                      :to="`/columns/${feature.feature}`"
                      class="font-mono text-primary-600 hover:text-primary-700 hover:underline transition-colors"
                      :title="`View details for ${feature.feature}`"
                    >
                      {{ feature.feature }}
                    </NuxtLink>
                  </div>
                  <div class="text-right">
                    <div class="font-medium">{{ (feature.average_importance * 100).toFixed(1) }}%</div>
                  </div>
                </div>
              </div>
              <div class="text-center mt-2">
                <NuxtLink 
                  to="/demographic-analysis"
                  class="text-xs text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all {{ featureImportanceData.top_features.length }} features →
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<style scoped>
</style>