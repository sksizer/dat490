<script setup lang="ts">
// Set breadcrumbs
const { setBreadcrumbs, clearBreadcrumbs } = usePageTitle()

// Fetch model data for summary
const { data: modelData } = await useAsyncData('model', () => {
  return queryCollection('columns').first()
})

// Fetch all available paths from the docs collection for navigation
const { data: docData } = await useAsyncData('all-paths', () =>
  queryCollection('docs').select('path', 'title').all()
)

// Define sections with cards
const sections = [
  {
    title: 'Data',
    cards: [
      {
        title: 'BRFSS Column Explorer',
        description: 'Browse all 350 columns with statistics and value distributions',
        url: '/columns',
        icon: 'i-heroicons-chart-bar',
        external: false
      },
      {
        title: 'Original Codebook',
        description: 'Official CDC codebook with detailed column descriptions',
        url: '/html/codebook_USCODE23_LLCP_021924.HTML',
        icon: 'i-heroicons-document-text',
        external: true
      }
    ]
  },
  {
    title: 'Project Resources',
    cards: [
      // {
      //   title: 'Project Outline',
      //   description: 'Main project documentation and objectives',
      //   url: 'https://docs.google.com/document/d/1RbDx5alcdpi-c61RW2LRcvwGtNUrCIo45GE9f1EYZM4/edit?usp=drivesdk',
      //   icon: 'i-heroicons-document',
      //   external: true
      // },
      // {
      //   title: 'Literature Review',
      //   description: 'Research and background literature',
      //   url: 'https://docs.google.com/document/d/1y_1qbr25FeLK4nZb1v7dKZTQkcnlG4NB4UmXdkZSLGE/edit?usp=drivesdk',
      //   icon: 'i-heroicons-academic-cap',
      //   external: true
      // },
      // {
      //   title: 'GitHub Repository',
      //   description: 'Source code and project files',
      //   url: 'https://github.com/sksizer/dat490',
      //   icon: 'i-heroicons-code-bracket',
      //   external: true
      // }
    ]
  }
]

// Add documentation section dynamically from content
const documentationCards = []
// computed(() => {
//   if (!docData.value) return []
//
//   return docData.value.map(page => ({
//     title: page.title || page.path,
//     description: 'Project documentation',
//     url: page.path,
//     icon: 'i-heroicons-book-open',
//     external: false
//   }))
// })

// Set breadcrumbs on mount
onMounted(() => {
  setBreadcrumbs([
    {
      label: 'Home',
      icon: 'i-heroicons-home'
    }
  ])
})

// Clear breadcrumbs when leaving
onUnmounted(() => {
  clearBreadcrumbs()
})
</script>

<template>
  <div class="container mx-auto py-6">
    <!-- Hero Section -->
    <div class="mb-8 text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">DAT490 - BRFSS Data Analysis</h1>
      <p class="text-lg text-gray-600 mb-6">
        Exploring the 2023 Behavioral Risk Factor Surveillance System dataset with 433,323 respondents across all US states and territories.
      </p>
      
      <!-- Dataset Summary -->
      <div class="bg-blue-50 rounded-lg p-4 mb-6">
        <ModelMetadataSummary :model-data="modelData" />
      </div>
    </div>

    <!-- Sections with Cards -->
    <div class="space-y-8">
      <!-- Main sections -->
      <div v-for="section in sections" :key="section.title" class="space-y-4">
        <h2 class="text-2xl font-semibold text-gray-900">{{ section.title }}</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <UCard 
            v-for="card in section.cards" 
            :key="card.title"
            class="hover:shadow-lg transition-shadow cursor-pointer"
            :ui="{ body: { padding: 'p-6' } }"
          >
            <div class="flex flex-col h-full">
              <div class="flex items-center gap-3 mb-3">
                <UIcon 
                  :name="card.icon" 
                  class="w-6 h-6 text-blue-600" 
                />
                <h3 class="text-lg font-semibold text-gray-900">{{ card.title }}</h3>
              </div>
              
              <p class="text-gray-600 text-sm mb-4 flex-1">{{ card.description }}</p>
              
              <div class="mt-auto">
                <NuxtLink 
                  v-if="!card.external"
                  :to="card.url"
                  class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  Explore
                  <UIcon 
                    name="i-heroicons-arrow-right"
                    class="w-4 h-4"
                  />
                </NuxtLink>
                <a 
                  v-else
                  :href="card.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  Open
                  <UIcon 
                    name="i-heroicons-arrow-top-right-on-square"
                    class="w-4 h-4"
                  />
                </a>
              </div>
            </div>
          </UCard>
        </div>
      </div>
      
      <!-- Documentation section (if available) -->
      <div v-if="documentationCards.length > 0" class="space-y-4">
        <h2 class="text-2xl font-semibold text-gray-900">Documentation</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <UCard 
            v-for="card in documentationCards" 
            :key="card.title"
            class="hover:shadow-lg transition-shadow cursor-pointer"
            :ui="{ body: { padding: 'p-6' } }"
          >
            <div class="flex flex-col h-full">
              <div class="flex items-center gap-3 mb-3">
                <UIcon 
                  :name="card.icon" 
                  class="w-6 h-6 text-blue-600" 
                />
                <h3 class="text-lg font-semibold text-gray-900">{{ card.title }}</h3>
              </div>
              
              <p class="text-gray-600 text-sm mb-4 flex-1">{{ card.description }}</p>
              
              <div class="mt-auto">
                <NuxtLink 
                  :to="card.url"
                  class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  Read
                  <UIcon 
                    name="i-heroicons-arrow-right"
                    class="w-4 h-4"
                  />
                </NuxtLink>
              </div>
            </div>
          </UCard>
        </div>
      </div>
    </div>
    
    <!-- Data Features Info -->
    <div class="mt-12 bg-gray-50 rounded-lg p-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">Dataset Features</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-gray-700">
        <div>
          <h3 class="font-medium mb-2">Coverage</h3>
          <ul class="space-y-1">
            <li>• Comprehensive health survey from all US states and territories</li>
            <li>• Demographics, health behaviors, and chronic conditions</li>
            <li>• Preventive health measures and risk factors</li>
          </ul>
        </div>
        <div>
          <h3 class="font-medium mb-2">Data Quality</h3>
          <ul class="space-y-1">
            <li>• Statistical distributions (min, max, mean, median)</li>
            <li>• Value frequency counts for categorical data</li>
            <li>• Comprehensive data completeness metrics</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Ensure cards have consistent height */
.grid > div {
  display: flex;
  flex-direction: column;
}
</style>