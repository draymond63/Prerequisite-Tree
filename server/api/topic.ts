import { fetchWiki, APIStatus } from "../utils";

export default defineEventHandler(async (event): Promise<Topic | null> => {
  const topic = getQuery(event)['topic'];
  if (topic === null || topic === undefined || topic === "" || typeof(topic) !== "string") {
    console.error("Invalid topic!:", topic);
    return null;
  }
  const description = await getDescription(topic);
  const prereqs = await getPrerequisites(topic);

  return {
    title: topic,
    description,
    prereqs: prereqs,
  };
});

const getPrerequisites = async (topic: string): Promise<string[]> => {
  const relatedArticles = await getRelatedArticles(topic);
  // TODO: Get prereqs from related articles using GPT-3
  // TODO: Filter out topics that are not existing articles
  return relatedArticles
}

const getRelatedArticles = async (topic: string): Promise<string[]> => {
  const params = {
    "action": "query",
    "format": "json",
    "prop": "links",
    "titles": topic,
    "formatversion": "2",
    "pllimit": "max"
  };
  const [results, status] = await fetchWiki<WikiLinksResponse>(params);
  if (status !== APIStatus.OKAY) {
    return [];
  }
  const links = results['query']['pages'][0]['links'] || [];
  const linkTitles = links.map(({ title }) => title);
  return filterLinks(linkTitles);
}

// TODO: Filter results by views, number of links, etc.
// TODO: https://stackoverflow.com/questions/5323589/how-to-use-wikipedia-api-to-get-the-page-view-statistics-of-a-particular-page-in
const filterLinks = async (articles: string[]): Promise<string[]> => {
  console.log(articles.length)
  const viewCounts: Record<string, number> = {};
  for (const article in articles) {
    const path = [
      "en.wikipedia",
      "all-access", // or "desktop" or "mobile-app" or "mobile-web"
      "user", // or "spider" or "all-agents"
      article,
      "monthly", // or "daily" or "hourly"
      "20230101",
      "20230201",
    ];
    const URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/" + path.join("/");
    const results = await $fetch(URL) as WikiMediaResponse; // ! Bad await call
    if (results.items) {
      const viewCount = results.items.reduce((acc, { views }) => acc + views, 0);
      console.log(viewCount);
      viewCounts[article] = viewCount;
    }
  }
  console.log(viewCounts);
  return articles;
}

const getDescription = async (topic: string): Promise<string> => {
  return ""
}