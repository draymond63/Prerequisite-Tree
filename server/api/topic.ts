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

// TODO: Filter results by number of links
// TODO: https://stackoverflow.com/questions/5323589/how-to-use-wikipedia-api-to-get-the-page-view-statistics-of-a-particular-page-in
const filterLinks = async (articles: string[]): Promise<string[]> => {
  console.log(articles.length)
  const resultPromises: Promise<WikiMediaResponse>[] = [];
  for (const i in articles) {
    const path = [
      "en.wikipedia",
      "all-access", // or "desktop" or "mobile-app" or "mobile-web"
      "user", // or "spider" or "all-agents"
      encodeURIComponent(articles[i]),
      "monthly", // or "daily" or "hourly"
      "20230101",
      "20230201",
    ];
    const URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/" + path.join("/");
    resultPromises.push($fetch(URL).catch(r => ({})) as Promise<WikiMediaResponse>);
  }
  const results = await Promise.all(resultPromises);
  const viewCountEntries: [string, number][] = results.map((result) => {
    if (result.items) {
      const article = result.items[0].article;
      const viewCount = result.items.reduce((acc, { views }) => acc + views, 0);
      return [article, viewCount];
    }
    else {
      return ["", 0];
    }
  });
  // const viewCounts = Object.fromEntries(viewCountEntries);
  return viewCountEntries.filter(([_, views]) => views > 5000).map(([article, _]) => article);
}

const getDescription = async (topic: string): Promise<string> => {
  return ""
}