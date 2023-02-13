<template>
  <li class="w-full max-w-3xl p-2">
    <NuxtLink :to="'/topic/' + article.title">
      <div class="w-full flex">
        <img class="w-32 h-32 m-1 mr-3 border-secondary border-8" src="https://picsum.photos/seed/picsum/600/400" alt="Placeholder" />
        <div class="h-min px-4 py-2 bg-white rounded-md shadow-lg shadow-slate-50">
          <h2>{{ article.title }}</h2>
          <p class="line-clamp-4" v-html="article.snippet" />
        </div>
      </div>
    </NuxtLink>
  </li>
</template>

<script lang="ts">
import type { PropType } from 'vue'

export default {
  props: {
    article: {
      type: Object as PropType<Article>,
      required: true
    }
  }
}
</script>

<style>
.searchmatch {
  font-weight: bold;
}
</style>