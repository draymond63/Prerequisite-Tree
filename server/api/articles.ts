export default defineEventHandler(async (event): Promise<Article[]> => {
  const query = getQuery(event)['q'];
  if (query === null || query === undefined || query === "" || typeof(query) !== "string") {
    console.error("Invalid query:", query);
    return [];
  }
  let articles = await getArticles(query);
  // TODO: Filter results by views, number of links, etc.
  return articles.filter((article) => article.wordcount > 3000);
});

const getArticles = async (query: string): Promise<Article[]> => {
  const URL = "https://en.wikipedia.org/w/api.php";
  const params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "generator": "search",
    "formatversion": "2",
    "exintro": 1,
    "explaintext": 1,
    "exsectionformat": "plain",
    "gsrsearch": query,
    "gsrinfo": "totalhits|suggestion|rewrittenquery",
    "gsrprop": "size|timestamp|snippet|wordcount"
  };
  try {
    const results = await $fetch(URL, { params }) as any;
    if (results['error']) {
      return [results['error']['info']];
    }
    const pages: WikiArticleResponse[] = results['query']['pages'] || [];
    const sortedPages = pages.sort((a, b) => a.index - b.index);
    return sortedPages.map((page) => ({
      id: page.pageid,
      wordcount: page.wordcount,
      title: page.title,
      extract: page.extract
    }));
  } catch(err) {
    console.error(err);
    return [];
  }
}
