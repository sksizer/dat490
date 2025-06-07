<script setup lang="ts">
// Test data for tabs
const testTabs = [
  { 
    label: 'Tab One', 
    value: 'tab1', 
    icon: 'i-heroicons-chart-bar',
    content: 'This is the content for tab one'
  },
  { 
    label: 'Tab Two', 
    value: 'tab2', 
    icon: 'i-heroicons-chart-bar-square',
    content: 'This is the content for tab two'
  },
  { 
    label: 'Tab Three', 
    value: 'tab3', 
    icon: 'i-heroicons-table-cells',
    content: 'This is the content for tab three'
  }
]

// Test chart data
const testChartData = [
  { value: '1', count: 150, description: 'Never' },
  { value: '2', count: 300, description: 'Sometimes' },
  { value: '3', count: 450, description: 'Often' },
  { value: '4', count: 200, description: 'Always' }
]

const selectedTab = ref('tab2')
</script>

<template>
  <div class="container mx-auto py-6 px-4 space-y-8">
    <h1 class="text-2xl font-bold">UTabs Test Page</h1>
    
    <!-- Test 1: Basic UTabs with Content -->
    <div>
      <h2 class="text-lg font-semibold mb-3">Test 1: Basic UTabs with Content</h2>
      <UTabs :items="testTabs" />
    </div>

    <!-- Test 2: UTabs with Custom Content Slot -->
    <div>
      <h2 class="text-lg font-semibold mb-3">Test 2: UTabs with Custom Content Slot</h2>
      <UTabs :items="testTabs">
        <template #item="{ item }">
          <div class="p-4 bg-blue-50 rounded-lg">
            <h3 class="font-semibold text-blue-900 mb-2">Custom Content for {{ item.label }}</h3>
            <p class="text-blue-700">{{ item.content }}</p>
          </div>
        </template>
      </UTabs>
    </div>

    <!-- Test 3: UTabs with Chart Components Simulation -->
    <div>
      <h2 class="text-lg font-semibold mb-3">Test 3: UTabs with Chart Components (Named Slots)</h2>
      <UTabs 
        :items="[
          { label: 'Vertical Chart', slot: 'vertical', icon: 'i-heroicons-chart-bar' },
          { label: 'Horizontal Chart', slot: 'horizontal', icon: 'i-heroicons-chart-bar-square' }
        ]"
      >
        <template #vertical="{ item }">
          <div class="bg-gray-50 rounded-lg p-3">
            <div class="text-center p-8 bg-blue-100 rounded">
              <p class="text-blue-800">Vertical Chart Component Would Go Here</p>
              <p class="text-sm text-blue-600 mt-2">Slot: {{ item.slot }}</p>
            </div>
          </div>
        </template>
        
        <template #horizontal="{ item }">
          <div class="bg-gray-50 rounded-lg p-3">
            <div class="text-center p-8 bg-green-100 rounded">
              <p class="text-green-800">Horizontal Chart Component Would Go Here</p>
              <p class="text-sm text-green-600 mt-2">Slot: {{ item.slot }}</p>
            </div>
          </div>
        </template>
      </UTabs>
    </div>

    <!-- Test 4: UTabs with Different Variants -->
    <div>
      <h2 class="text-lg font-semibold mb-3">Test 4: UTabs with Different Variants</h2>
      
      <h3 class="text-md font-medium mb-2">Pill Variant (Default)</h3>
      <UTabs :items="testTabs.slice(0,2)" variant="pill" class="mb-4" />

      <h3 class="text-md font-medium mb-2">Link Variant</h3>
      <UTabs :items="testTabs.slice(0,2)" variant="link" />
    </div>

    <!-- Test 5: UTabs with Model Binding -->
    <div>
      <h2 class="text-lg font-semibold mb-3">Test 5: UTabs with Model Binding</h2>
      <UTabs :items="testTabs" v-model="selectedTab" />
      <p class="mt-2 text-sm text-gray-600">Current selected tab: <strong>{{ selectedTab }}</strong></p>
    </div>

    <!-- Test 6: Simple Two-Tab Test (Closest to our use case) -->
    <div>
      <h2 class="text-lg font-semibold mb-3">Test 6: Simple Two-Tab Test (Fixed)</h2>
      <UTabs 
        :items="[
          { label: 'First', slot: 'first' },
          { label: 'Second', slot: 'second' }
        ]"
      >
        <template #first="{ item }">
          <div class="p-4 border rounded bg-red-50">
            <p>Content for {{ item.label }} tab (slot: {{ item.slot }})</p>
          </div>
        </template>
        
        <template #second="{ item }">
          <div class="p-4 border rounded bg-yellow-50">
            <p>Content for {{ item.label }} tab (slot: {{ item.slot }})</p>
          </div>
        </template>
      </UTabs>
    </div>
  </div>
</template>