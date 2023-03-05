<template>
  <li class="w-full max-w-3xl p-2">
    <button @click="router.push('/topic/' + title)">
      <div class="w-full flex space-x-2">
        <img
          class="h-36 aspect-square object-cover m-1 border-secondary border-8"
          :src="image ?? 'https://picsum.photos/seed/picsum/600/400'"
          :alt="title" 
        />
        <div class="h-min px-4 py-2 bg-white rounded-md drop-shadow-lg shadow-black text-left">
          <client-only>
          <Bookmark
            @click="$event.stopPropagation()"
            class="w-8 aspect-square float-right mt-2"
            :title="title"
          />
          </client-only>
          <h3>{{ title }}</h3>
          <p class="line-clamp-4" v-html="description" />
        </div>
      </div>
    </button>
  </li>
</template>

<script lang="ts" setup>
const router = useRouter();
const { topic: param } = defineProps<{topic: Topic | string}>();

const getTopicInfo = async (title: string): Promise<Topic> => {
  const { data } = await useFetch(() => `/api/topic`, { body: [title], method: 'POST' });
  return data.value && data.value[title] ? data.value[title] : {
    title,
    description: 'An error occured retrieving information about this topic :(',
    image: 'https://picsum.photos/seed/picsum/600/400',
  }
}
const { title, description, image } = typeof param === 'string' ? await getTopicInfo(param) : param;
</script>
