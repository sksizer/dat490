<script setup lang="ts">
const route = useRoute()
const appName = "DAT490"

// Use the page title composable
const { pageTitle, breadcrumbs } = usePageTitle()

// Computed title that shows page title or falls back to app name
const displayTitle = computed(() => {
  return pageTitle.value || appName
})

// Default breadcrumb items (always show home)
const breadcrumbItems = computed(() => {
  const defaultItems = [
    {
      label: appName,
      to: '/',
      icon: 'i-heroicons-home'
    }
  ]
  
  // Add page-specific breadcrumbs
  if (breadcrumbs.value && breadcrumbs.value.length > 0) {
    return [...defaultItems, ...breadcrumbs.value]
  }
  
  return defaultItems
})

const { data: docPages } = await useAsyncData('docs', () => queryCollection('docs').find())
const docNavItems = computed(() => {
  return docPages.value?.map(page => {
    const nav = page.navigation || {}
    return {
      label: nav.title || page.title || page._path,
      to: page._path,
      icon: nav.icon || 'i-heroicons-document',
      order: nav.order || 99
    }
  }).sort((a, b) => a.order - b.order) || []
})

const menuItems = computed(() => [
  { label: 'Home', to: '/', icon: 'i-heroicons-home' },
  { label: 'Features', to: '/columns', icon: 'i-heroicons-table-cells' },
  { label: 'Demographic Analysis', to: '/demographic-analysis', icon: 'i-heroicons-chart-bar' },
  { label: 'Codebook', to: '/codebook', icon: 'i-heroicons-book-open' },
  { 
    label: 'Documentation', 
    icon: 'i-heroicons-document-text',
    children: docNavItems.value
  },
  { label: 'GitHub', href: 'https://github.com/sksizer/dat490', target: '_blank', icon: 'i-heroicons-code-bracket' }
])
</script>

<template>
  <div class="h-screen flex flex-col">
    <!-- Fixed Header -->
    <header class="fixed top-0 left-0 right-0 z-50 bg-gray-800 text-white shadow-md border-b-2 border-blue-500">
      <UContainer>
        <div class="flex items-center py-2">
          <!-- Left section with dropdown using hamburger icon -->
          <div class="flex items-center">
            <!-- Breadcrumbs -->
            <div class="ml-3 flex-1">
              <UBreadcrumb 
                :items="breadcrumbItems"
                :ui="{
                  list: 'flex items-center',
                  item: 'text-white',
                  active: 'text-white font-semibold',
                  inactive: 'text-gray-300 hover:text-white',
                  separator: 'text-gray-400'
                }"
              />
            </div>
          </div>
          
          <!-- Right section (empty for now) -->
          <div class="ml-auto">
          </div>
        </div>
      </UContainer>
    </header>
    
    <!-- Main Content with padding for fixed header/footer -->
    <main class="flex-1 overflow-y-auto pt-14 pb-12">
      <UContainer class="py-1">
        <slot />
      </UContainer>
    </main>
    
    <!-- Fixed Footer -->
    <footer class="fixed bottom-0 left-0 right-0 z-50 bg-gray-100 border-t border-gray-200">
      <UContainer>
        <div class="py-2 flex items-center justify-between">
          <p class="text-sm text-gray-600">&copy; {{ new Date().getFullYear() }} {{ appName }}</p>
          <p class="text-xs text-gray-400 font-mono">{{ route.path }}</p>
        </div>
      </UContainer>
    </footer>
  </div>
</template>