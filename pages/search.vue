<template>
  <div>
    <p>{{ query }}</p>
  </div>
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