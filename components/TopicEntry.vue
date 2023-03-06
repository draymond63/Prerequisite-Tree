<template>
  <li class="w-full max-w-3xl">
    <button @click="router.push('/topic/' + title)">
      <div class="
        w-full flex space-x-2 overflow-hidden shadow-black
        flex-col       rounded-lg      drop-shadow-lg      bg-white
        md:flex-row md:rounded-none md:drop-shadow-none md:bg-transparent
      ">
        <img
          class="h-24 md:h-36 aspect-square object-cover md:m-1 md:border-8 border-secondary"
          :src="image ?? 'https://picsum.photos/seed/picsum/600/400'"
          :alt="title" 
        />
        <div class="h-min px-4 py-2 md:bg-white md:rounded-md md:drop-shadow-lg shadow-black text-left">
          <client-only>
          <Bookmark
            @click="$event.stopPropagation()"
            class="w-8 aspect-square float-right mt-2"
            :title="title"
          />
          </client-only>
          <h3>{{ title }}</h3>
          <p class="line-clamp-3 md:line-clamp-4" v-html="description" />
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
