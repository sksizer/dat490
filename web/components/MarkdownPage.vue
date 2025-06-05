<script setup lang="ts">
// Define the prop for page path override
const props = defineProps({
  pagePath: {
    type: String,
    default: ''
  }
})

const route = useRoute()
// Determine which path to use - prop takes precedence over route
const contentPath = computed(() => props.pagePath || route.path)

// Note: Using queryCollection API for Nuxt 3 Content
// See documentation: https://content.nuxt.com/docs/utils/query-collection
const { data: page } = await useAsyncData(`content-${contentPath.value}`, () => {
  return queryCollection('docs').path(contentPath.value).first()
})
</script>

<template>
  <div>
    <div v-if="page" class="markdown">
      <ContentRenderer :value="page" />
    </div>
    <div v-else class="py-12 text-center">
      <h2 class="text-xl text-gray-600">Page not found</h2>
      <p class="mt-4">
        <NuxtLink to="/" class="text-blue-500 hover:underline">Return to home</NuxtLink>
      </p>
    </div>
    <div>{{contentPath}}</div>
  </div>

</template>