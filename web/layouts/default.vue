<script setup lang="ts">
const appName = "DAT490"
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
  { 
    label: 'Documentation', 
    icon: 'i-heroicons-book-open',
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
        <div class="flex items-center py-3">
          <!-- Left section with dropdown using hamburger icon -->
          <div class="flex items-center">
            <UDropdownMenu :items="menuItems" hover>
              <UButton color="white" variant="ghost" icon="i-heroicons-bars-3-20-solid" aria-label="Menu" />
            </UDropdownMenu>
            
            <!-- Title next to menu button -->
            <NuxtLink to="/" class="text-xl font-bold ml-3">{{ appName }}  </NuxtLink>
          </div>
          
          <!-- Right section (empty for now) -->
          <div class="ml-auto">
          </div>
        </div>
      </UContainer>
    </header>
    
    <!-- Main Content with padding for fixed header/footer -->
    <main class="flex-1 overflow-y-auto pt-16 pb-16">
      <UContainer class="py-3">
        <slot />
      </UContainer>
    </main>
    
    <!-- Fixed Footer -->
    <footer class="fixed bottom-0 left-0 right-0 z-50 bg-gray-100 border-t border-gray-200">
      <UContainer>
        <div class="py-4">
          <p class="text-sm text-gray-600">&copy; {{ new Date().getFullYear() }} {{ appName }}</p>
        </div>
      </UContainer>
    </footer>
  </div>
</template>