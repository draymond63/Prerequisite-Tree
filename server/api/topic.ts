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

// TODO: Filter results by views, number of links, etc.
const getRelatedArticles = async (topic: string): Promise<string[]> => {
  const URL = "https://en.wikipedia.org/w/api.php";
  const params = {
    "action": "query",
    "format": "json",
    "prop": "links",
    "titles": topic,
    "formatversion": "2",
    "pllimit": "max"
  };
  try {
    const results = await $fetch(URL, { params }) as any;
    console.log("Results:", results);
    if (results['error']) {
      return [results['error']['info']];
    }
    const links: WikiLinksResponse = results['query']['pages'][0]['links'] || [];
    return links.map(({ title }) => title);
  } catch(err) {
    console.error(err);
    return [];
  }
}

const getDescription = async (topic: string): Promise<string> => {
  return ""
}