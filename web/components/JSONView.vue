<script setup lang="ts">
interface Props {
  data: any
  maxHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  maxHeight: '600px'
})

// Convert data to formatted JSON string
const jsonString = computed(() => {
  try {
    if (typeof props.data === 'string') {
      // If it's already a string, try to parse and re-stringify for formatting
      return JSON.stringify(JSON.parse(props.data), null, 2)
    }
    return JSON.stringify(props.data, null, 2)
  } catch (e) {
    // If parsing fails, return the original string
    return typeof props.data === 'string' ? props.data : JSON.stringify(props.data, null, 2)
  }
})

// Apply syntax highlighting
const highlightedJson = computed(() => {
  let json = jsonString.value
  
  // Replace property names (keys)
  json = json.replace(/"([^"]+)":/g, '<span class="json-key">"$1"</span>:')
  
  // Replace string values
  json = json.replace(/: "([^"]*)"/g, ': <span class="json-string">"$1"</span>')
  
  // Replace numbers
  json = json.replace(/: (\d+\.?\d*)/g, ': <span class="json-number">$1</span>')
  
  // Replace booleans
  json = json.replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>')
  
  // Replace null
  json = json.replace(/: null/g, ': <span class="json-null">null</span>')
  
  return json
})

// Copy to clipboard state
const copied = ref(false)

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(jsonString.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<template>
  <div class="json-view-container">
    <!-- Header with copy button -->
    <div class="flex items-center justify-between mb-2">
      <h3 class="text-xs font-medium text-gray-500">JSON Data</h3>
      <UButton
        @click="copyToClipboard"
        variant="ghost"
        size="xs"
        :icon="copied ? 'i-heroicons-check' : 'i-heroicons-clipboard-document'"
        :ui="{ color: { gray: { ghost: copied ? 'text-green-600 hover:text-green-700' : '' } } }"
      >
        {{ copied ? 'Copied!' : 'Copy' }}
      </UButton>
    </div>
    
    <!-- JSON content -->
    <div 
      class="json-content overflow-auto bg-gray-900 text-gray-100 p-4 rounded-lg"
      :style="{ maxHeight }"
    >
      <pre class="m-0"><code v-html="highlightedJson"></code></pre>
    </div>
  </div>
</template>

<style scoped>
.json-content {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
}

.json-content pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Syntax highlighting */
:deep(.json-key) {
  color: #7dd3fc; /* sky-300 */
}

:deep(.json-string) {
  color: #86efac; /* green-300 */
}

:deep(.json-number) {
  color: #fdba74; /* orange-300 */
}

:deep(.json-boolean) {
  color: #f9a8d4; /* pink-300 */
}

:deep(.json-null) {
  color: #fca5a5; /* red-300 */
}
</style>