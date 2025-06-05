<script lang="ts" setup>
  const siteState = useState('siteState', () => {

    return shallowRef({

    })
  });

</script>
<template>
  <UApp>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
