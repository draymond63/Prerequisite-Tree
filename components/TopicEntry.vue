<template>
  <li class="w-full max-w-3xl p-2">
    <button @click="router.push('/topic/' + article.title)">
      <div class="w-full flex space-x-2">
        <img
          class="h-36 aspect-square object-cover m-1 border-secondary border-8"
          :src="article.image ?? 'https://picsum.photos/seed/picsum/600/400'"
          :alt="article.title" 
        />
        <div class="h-min px-4 py-2 bg-white rounded-md drop-shadow-lg shadow-black text-left">
          <Bookmark
            @click="$event.stopPropagation()"
            class="w-8 aspect-square float-right mt-2"
            v-model:status="state.bookmarked"
          />
          <h3>{{ article.title }}</h3>
          <p class="line-clamp-4" v-html="article.extract" />
        </div>
      </div>
    </button>
  </li>
</template>

<script lang="ts" setup>
defineProps<{article: Article}>();
const router = useRouter();
const state = reactive({ bookmarked: false });
</script>
