<script lang="ts" setup>
  const siteState = useState('siteState', () => {
    return {
    }
  });

</script>
<template>
  <UApp>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
