<template>
  <div>
    <client-only>
    <p v-for="(topic, index) in state.bookmarks">
      <TopicEntry :topic="{
        title: topic, 
        description: '',
        image: '',
      }" />
    </p>
    </client-only>
  </div>
</template>

<script lang="ts" setup>
const state = useBookmarks();
</script>