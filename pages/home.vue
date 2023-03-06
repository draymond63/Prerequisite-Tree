<template>
  <h1>Bookmarks</h1>
  <ul class="flex flex-col items-center space-y-2">
    <client-only>
      <TopicEntry v-for="title in state.bookmarks.values()" :topic="title"/>
    </client-only>
  </ul>
</template>

<script lang="ts" setup>
const state = useBookmarks();
</script>