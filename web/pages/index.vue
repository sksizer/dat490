<script setup lang="ts">
// Add interactive path testing functionality
import type {PageCollection} from "@nuxt/content";

const contentPath = ref('/')
const availablePaths = ref<any[]>()

// Fetch all available paths from the docs collection
  const { data } = await useAsyncData('all-paths', () =>
    queryCollection('docs').select('path', 'title' ).all()
  )

onMounted(() => {
  availablePaths.value = data.value?.map(page => ({
    path: page.path,
    title: page.title || page.path
  })) || []
})

</script>

<template>
  <div>
      <h1>Markdown Files</h1>
      <div v-if="availablePaths && availablePaths.length > 0" class="mt-2">
        <div v-for="path in availablePaths">
          <NuxtLink :to="path.path">{{path.title}}</NuxtLink>
        </div>
    </div>

    <h1>Readme</h1>
    <!-- Content display -->
    <MarkdownPage :pagePath="contentPath" />
  </div>
</template>