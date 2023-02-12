<template>
  <ul class="flex flex-col items-center px-8">
    <TopicEntry v-for="article in articles" :key="article" :title="article" />
  </ul>
</template>

<script lang="ts">
export default {
  data: () => ({
    articles: [] as Array<string>,
  }),
  watchQuery: ['q'],
  created() {
    this.search();
  },
  updated() {
    this.search();
  },
  methods: {
    async search() {
      const router = useRouter();
      const { q } = router.currentRoute.value.query;
      const URL = "https://en.wikipedia.org/w/api.php";
      const params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "list": "",
        "meta": "",
        "generator": "allpages",
        "converttitles": "1",
        "formatversion": "2",
        "exintro": "1",
        "explaintext": "1",
        "exsectionformat": "plain",
        "gapfrom": (q ?? '').toString(),
        "gaplimit": "3"
      };
      const { data } = await useFetch(URL, { params });
      this.articles = this.parseResults(data);
    },
    parseResults (results: any): Array<string> {
      const pages = results['value']['query']['pages'] || [];
      return pages.map(({ title }: {title: any}) => title);
    }
  }
}
</script>