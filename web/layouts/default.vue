<script setup lang="ts">
const appName = "DAT490"
// Note: Using queryCollection API for Nuxt 3 Content
// See documentation: https://content.nuxt.com/docs/utils/query-collection
const { data: docPages } = await useAsyncData('docs', () => queryCollection('docs').find())

// Transform the data for the dropdown menu
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
  { 
    label: 'Documentation', 
    icon: 'i-heroicons-book-open',
    children: docNavItems.value
  },
  { label: 'GitHub', href: 'https://github.com/sksizer/dat490', target: '_blank', icon: 'i-heroicons-code-bracket' }
])
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Navbar 
         Note: UHeader is not a valid Nuxt UI component. Using standard header with classes instead.
         See Nuxt UI components list: https://ui.nuxt.com/components
    -->
    <UContainer>
      <header class="bg-gray-800 text-white shadow-md border-b-2 border-blue-500">
        <div class="flex items-center py-3">
          <!-- Left section with dropdown using hamburger icon -->
          <div class="flex items-center">
            <UDropdownMenu :items="menuItems" hover>
              <UButton color="white" variant="ghost" icon="i-heroicons-bars-3-20-solid" aria-label="Menu" />
            </UDropdownMenu>
            
            <!-- Title next to menu button -->
            <NuxtLink to="/" class="text-xl font-bold ml-3">{{ appName }}</NuxtLink>
          </div>
          
          <!-- Right section (empty for now) -->
          <div class="ml-auto">
          </div>
        </div>
      </header>
    </UContainer>
    
    <!-- Main Content -->
    <UContainer class="flex-grow py-6">
      <slot />
    </UContainer>
    
    <!-- Footer -->
    <footer class="bg-gray-100 border-t border-gray-200 py-4">
      <UContainer>
        <p class="text-sm text-gray-600">&copy; {{ new Date().getFullYear() }} {{ appName }}</p>
      </UContainer>
    </footer>
  </div>
</template>