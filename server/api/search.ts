import { fetchWiki, APIStatus } from "../utils";

export default defineEventHandler(async (event): Promise<Topic[]> => {
  const query = getQuery(event)['q'];
  if (query === null || query === undefined || query === "" || typeof(query) !== "string") {
    console.error("Invalid query:", query);
    return [];
  }
  let articles = await searchArticles(query);
  // TODO: Filter results by views, number of links, etc.
  return articles.filter((article) => article.wordcount ?? 0 > 3000);
});

const searchArticles = async (query: string): Promise<Topic[]> => {
  const params = {
    "action": "query",
    "format": "json",
    "prop": ["extracts", "pageimages"].join('|'),
    "pithumbsize": 300,
    "generator": "search",
    "formatversion": "2",
    "exintro": 1,
    "explaintext": 1,
    "exsectionformat": "plain",
    "gsrsearch": query,
    "gsrinfo": "totalhits|suggestion|rewrittenquery",
    "gsrprop": "size|timestamp|snippet|wordcount"
  };
  const [results, status] = await fetchWiki<WikiSearchResponse>(params);
  if (status !== APIStatus.OKAY) {
    return [];
  }
  const pages = results['query']['pages'] || [];
  const sortedPages = pages.sort((a, b) => a.index - b.index);
  return sortedPages.map((page) => ({
    id: page.pageid,
    wordcount: page.wordcount,
    title: page.title,
    description: page.extract,
    image: page.thumbnail?.source,
  }));
}
