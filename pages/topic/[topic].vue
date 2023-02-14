<template>
  <div>
    <h1>{{ data?.title }}</h1>
    <p>{{ data?.description }}</p>
    <img :src="data?.image" :alt="data?.title" />
    <h2>Prerequisites</h2>
    <div v-for="[prereq, prereqInfo] in Object.entries(data?.prereqs)" :key="prereq">
      <h3>{{ prereq }}</h3>
      <p>{{ prereqInfo.description }}</p>
    </div>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute()
const title = route.params.topic
const { data } = await useFetch(() => `/api/topic?topic=${title}`);
</script>