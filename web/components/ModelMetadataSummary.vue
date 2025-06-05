<script setup lang="ts">
interface Props {
  modelData: any
}

const props = defineProps<Props>()

// Calculate metadata statistics
const stats = computed(() => {
  if (!props.modelData?.columns) {
    return {
      totalColumns: 0,
      computedColumns: 0,
      sections: 0,
      typesOfVariables: 0
    }
  }

  const columns = Object.values(props.modelData.columns)
  const computedColumns = columns.filter((col: any) => col.computed).length
  const sections = new Set(columns.map((col: any) => col.section_name).filter(Boolean))
  const variableTypes = new Set(columns.map((col: any) => col.type_of_variable).filter(Boolean))

  return {
    totalColumns: columns.length,
    computedColumns,
    sections: sections.size,
    typesOfVariables: variableTypes.size
  }
})
</script>

<template>
  <UCard class="mb-3">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Columns</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.totalColumns }}</p>
      </div>
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Computed Columns</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.computedColumns }}</p>
      </div>
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Sections</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.sections }}</p>
      </div>
      <div>
        <p class="text-sm font-medium text-gray-500 dark:text-gray-400">Variable Types</p>
        <p class="mt-1 text-2xl font-semibold">{{ stats.typesOfVariables }}</p>
      </div>
    </div>
  </UCard>
</template>