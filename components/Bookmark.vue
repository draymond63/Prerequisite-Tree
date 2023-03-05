<template>
  <button
    @click="() => update(!state.bookmarked)"
    class="text-accent-2-dark"
  >
    <!-- TODO: Fix hydration issue -->
    <client-only placeholder="">
      <BookmarkIconSolid v-if="state.bookmarked" />
      <BookmarkIconOutline v-else />
    </client-only>
  </button>
</template>

<script lang="ts" setup>
// https://github.com/tailwindlabs/heroicons
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/vue/24/solid'
import { BookmarkIcon as BookmarkIconOutline } from '@heroicons/vue/24/outline'

const { topic } = defineProps<{topic: string}>();
const { state, update } = useBookmark(topic);
</script>

<style>
svg path {
  stroke-width: 2.5;
}
</style>