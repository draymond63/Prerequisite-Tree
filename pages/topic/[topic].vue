<template>
  <div>
    <h1>{{ data?.title }}</h1>
    <p>{{ data?.description }}</p>
    <p v-for="prereq in data?.prereqs" :key="prereq">{{ prereq }}</p>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute()
const title = route.params.topic
const { data } = await useFetch(() => `/api/topic?topic=${title}`);
</script>