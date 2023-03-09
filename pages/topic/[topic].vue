<template>
  <div class="mt-2 md:mt-4 space-y-2">
    <div>
      <img :src="topic?.image" :alt="title" class="max-sm:hidden float-right max-w-lg mx-2" />
      <div class="flex items-center space-x-4">
        <h1 class="leading-none">{{ title }}</h1>
        <Bookmark class="max-md:hidden w-10 h-10" :title="title" />
      </div>
      <p class="max-sm:line-clamp-6">{{ topic?.description }}</p>
      <div class="flex my-2">
        <a :href="'https://en.wikipedia.org/wiki/' + topic?.title" target="_blank">
            Learn more about {{ topic?.title }} here.
        </a>
        <Bookmark class="md:hidden w-10 h-10" :title="title" />
      </div>
    </div>
    <h2>Prerequisites</h2>
    <div
      v-if="topic?.prereqs != undefined"
      v-for="([prereq, prereqInfo], index) in Object.entries(topic?.prereqs ?? {})"
      :key="prereq"
      class="pb-2"
    >
      <div class="flex items-center justify-between">
        <NuxtLink :to="'/topic/' + prereq" class="text-inherit">
          <h3>{{ index + 1 }}. {{ prereq }}</h3>
        </NuxtLink>
        <Bookmark class="w-6 h-6" :title="prereq" />
      </div>
      <p class="line-clamp-4">{{ prereqInfo.description }}</p>
    </div>
    <b v-else>
      Loading prerequisites...
    </b>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute()
const param = route.params.topic
if (Array.isArray(param)) {
  console.error("Title was an array:", param);
}
const title = Array.isArray(param) ? param[0] : param;
const topic = useTopic(title);
</script>