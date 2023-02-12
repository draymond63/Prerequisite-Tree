<template>
   <input
    class="rounded-full p-1 pl-2 w-3/4 max-w-2xl border-grey border-1 focus:border-white"
    type="text" placeholder="I want to learn about ..."
    v-model="query"
    v-on:keyup.enter="runQuery"
  >
</template>

<script lang="ts">
export default {
  name: 'SearchBar',
  data: () => ({
    query: '',
  }),
  created() {
    const router = useRouter();
    const { q } = router.currentRoute.value.query;
    if (q) {
      this.query = q as string;
    }
  },
  methods: {
    runQuery() {
      const router = useRouter();
      router.push(`/search?q=${this.query}`);
    },
  },
};
</script>