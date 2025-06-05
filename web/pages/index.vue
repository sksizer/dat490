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

const { data: modelData } = await useAsyncData('model', () => {
  const val = queryCollection('columns').first()
  return val; 
})

</script>

<template>
  <div>
    <div>
      <h1>Data</h1>
      <h2>BFRSS Column Data - <NuxtLink to="/columns" class="link">Explore</NuxtLink></h2>
      <ModelMetadataSummary :modelData="modelData" />
    </div>

    <div>
      <h1>Project Documents</h1>
        <h1>Documentation</h1>
        <div v-if="availablePaths && availablePaths.length > 0" class="mt-2">
          <div v-for="path in availablePaths">
            <NuxtLink class="link" :to="path.path">{{path.title}}</NuxtLink>
          </div>
      </div>
    </div>

    <div>
      <h1>Getting Started</h1>
      <!-- Content display -->
      <MarkdownPage :pagePath="contentPath" />
    </div>
  </div>
</template>