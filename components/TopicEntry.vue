<template>
  <li class="w-full max-w-3xl p-2">
    <button @click="router.push('/topic/' + topic.title)">
      <div class="w-full flex space-x-2">
        <img
          class="h-36 aspect-square object-cover m-1 border-secondary border-8"
          :src="topic.image ?? 'https://picsum.photos/seed/picsum/600/400'"
          :alt="topic.title" 
        />
        <div class="h-min px-4 py-2 bg-white rounded-md drop-shadow-lg shadow-black text-left">
          <client-only>
          <Bookmark
            @click="$event.stopPropagation()"
            class="w-8 aspect-square float-right mt-2"
            :title="topic.title"
          />
          </client-only>
          <h3>{{ topic.title }}</h3>
          <p class="line-clamp-4" v-html="topic.description" />
        </div>
      </div>
    </button>
  </li>
</template>

<script lang="ts" setup>
defineProps<{topic: Topic}>();
const router = useRouter();
</script>
