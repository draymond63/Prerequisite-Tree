<template>
  <ul class="flex flex-col items-center">
    <TopicEntry v-for="article in articles" :key="article" :title="article" />
  </ul>
</template>

<script lang="ts">
export default {
  name: 'SearchBar',
  data() {
    return {
      articles: [],
    };
  },
  async created() {
    const results = await this.fetch();
    if (results) {
      this.articles = this.parseResults(results)
    }
  },
  methods: {
    async fetch() {
      const router = useRouter();
      const { q } = router.currentRoute.value.query;
      if ((!(typeof q === 'string')) || q === '') {
        return { results: [] };
      }
      // https://en.wikipedia.org/wiki/Special:ApiSandbox#action=query&format=json&prop=extracts&list=&meta=&generator=allpages&converttitles=1&formatversion=2&exintro=1&explaintext=1&exsectionformat=plain&gapfrom=Control%20Systems&gaplimit=3
      const URL = "https://en.wikipedia.org/w/api.php?";
      const queryParams: Record<string, string> = {
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
        "gapfrom": q.toString(),
        "gaplimit": "3"
      };
      const request = URL + new URLSearchParams(queryParams).toString();
      return await useFetch(request);
    },
    parseResults(results: any) {
      const pages = results['data']['value']['query']['pages']
      if (pages) {
        return pages.map(({ title }: {title: any}) => title);
      }
      return []
    }
  },
};
</script>