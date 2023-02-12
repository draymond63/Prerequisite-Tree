<template>
  <div>
    <h1>{{ title }}</h1>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute()
const title = route.params.topic
</script>