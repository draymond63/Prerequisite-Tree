<template>
  <h1>Bookmarks</h1>
  <ul class="flex flex-col items-center px-8">
    <client-only>
      <p v-for="title in state.bookmarks.values()">
        <TopicEntry :topic="title" />
      </p>
    </client-only>
  </ul>
</template>

<script lang="ts" setup>
const state = useBookmarks();
</script>