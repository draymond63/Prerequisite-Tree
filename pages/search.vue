<template>
  <ul class="flex flex-col items-center px-8">
    <TopicEntry v-for="topic in topics" :key="topic.title" :topic="topic" />
  </ul>
</template>

<script lang="ts" setup>
const route = useRoute()
const { data: topics } = await useFetch(() => `/api/search?q=${route.query.q}`);
</script>
