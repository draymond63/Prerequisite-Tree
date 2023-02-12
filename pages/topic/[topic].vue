<template>
  <div>
    <p>{{ title }}</p>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute()
const title = route.params.topic
</script>