<template>
  <div>
    <div>
        <img :src="data?.image" :alt="data?.title" class="float-right max-w-lg mx-2" />
        <div>
          <h1 class="my-4">{{ data?.title }}</h1>
        </div>
        <p>{{ data?.description }}</p>
        <a :href="'https://en.wikipedia.org/wiki/' + data?.title">
          Learn more about {{ title }} here
        </a>
    </div>
    <h2>Prerequisites</h2>
    <div v-for="[prereq, prereqInfo] in Object.entries(data?.prereqs)" :key="prereq">
      <h3>{{ prereq }}</h3>
      <p>{{ prereqInfo.description }}</p>
    </div>
  </div>
</template>

<script lang="ts" setup>
const route = useRoute()
const title = route.params.topic
const { data } = await useFetch(() => `/api/topic?topic=${title}`);
</script>