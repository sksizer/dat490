<template>
  <div class="bg-gray-50 rounded-lg p-0.5 h-[616px]">
    <!-- Loading state -->
    <div v-if="!isLoaded" class="w-full h-[600px] bg-white rounded border border-gray-200 flex items-center justify-center">
      <div class="text-gray-400 text-sm text-center">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 mb-2 mx-auto animate-spin" />
        <p>Loading codebook...</p>
      </div>
    </div>
    
    <!-- Error state -->
    <div v-if="hasError" class="w-full h-[600px] bg-white rounded border border-gray-200 flex items-center justify-center">
      <div class="text-red-500 text-sm text-center">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8 mb-2 mx-auto" />
        <p>Failed to load codebook</p>
      </div>
    </div>
    
    <!-- Iframe -->
    <iframe
      v-show="isLoaded && !hasError"
      ref="iframe"
      :src="currentSrc"
      class="w-full h-[600px] bg-white rounded border border-gray-200"
      :title="title"
      @load="onLoad"
      @error="onError"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  src: string
  anchor?: string
  title?: string
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  delay: 0
})

const iframe = ref<HTMLIFrameElement>()
const isLoaded = ref(false)
const hasError = ref(false)
const currentSrc = ref('')

// Compute the full URL with anchor if provided
const fullSrc = computed(() => {
  return props.anchor ? `${props.src}#${props.anchor}` : props.src
})

// Initialize iframe loading with delay
onMounted(() => {
  if (props.delay > 0) {
    setTimeout(() => {
      currentSrc.value = fullSrc.value
    }, props.delay)
  } else {
    currentSrc.value = fullSrc.value
  }
})

// Handle iframe load event
const onLoad = () => {
  isLoaded.value = true
  hasError.value = false
}

// Handle iframe error event
const onError = () => {
  hasError.value = true
  isLoaded.value = false
}

// Method to reset iframe to anchor location
const reset = () => {
  if (iframe.value && props.anchor) {
    iframe.value.contentWindow?.location.replace(fullSrc.value)
  }
}

// Expose reset method to parent
defineExpose({
  reset
})
</script>