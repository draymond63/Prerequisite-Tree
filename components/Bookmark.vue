<template>
  <button @click="emit('update:status', !status)">
    <BookmarkIconSolid v-if="status" class="text-accent-2-dark" />
    <BookmarkIconOutline v-else class="text-accent-2-dark" />
  </button>
</template>

<script lang="ts" setup>
// https://github.com/tailwindlabs/heroicons
import { BookmarkIcon as BookmarkIconSolid } from '@heroicons/vue/24/solid'
import { BookmarkIcon as BookmarkIconOutline } from '@heroicons/vue/24/outline'

const { status } = defineProps(['status'])
const emit = defineEmits(['update:status'])
</script>