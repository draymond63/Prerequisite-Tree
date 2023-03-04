<template>
  <button
    @click="emit('update:status', !status)"
    class="text-accent-2-dark"
  >
    <BookmarkIconSolid v-if="status" />
    <BookmarkIconOutline v-else />
  </button>
</template>

<script lang="ts" setup>
// https://github.com/tailwindlabs/heroicons
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/vue/24/solid'
import { BookmarkIcon as BookmarkIconOutline } from '@heroicons/vue/24/outline'

const { status } = defineProps(['status'])
const emit = defineEmits(['update:status'])
</script>

<style>
svg path {
  stroke-width: 2.5;
}
</style>