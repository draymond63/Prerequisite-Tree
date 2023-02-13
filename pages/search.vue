<template>
  <ul class="flex flex-col items-center px-8">
    <TopicEntry v-for="article in articles" :key="article.title" :article="article" />
  </ul>
</template>

<script lang="ts" setup>
const route = useRoute()
const { data: articles } = await useFetch(() => `/api/search?q=${route.query.q}`);
</script>
