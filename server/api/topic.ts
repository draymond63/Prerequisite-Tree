import { fetchWiki, APIStatus } from "../utils";

export default defineEventHandler(async (event): Promise<Topic | null> => {
  const topic = getQuery(event)['topic'];
  if (topic === null || topic === undefined || topic === "" || typeof(topic) !== "string") {
    console.error("Invalid topic!:", topic);
    return null;
  }
  const topicInfo = (await getTopicInfo([topic]))[topic];
  const subTopicInfo = await getTopicInfo(topicInfo?.links ?? [], { links: true, description: true, pageviews: true });
  console.log("sub-topics:", Object.keys(subTopicInfo).length);
  const prereqs = filterTopics(subTopicInfo);
  console.log("prereqs:", Object.keys(prereqs).length);

  return {
    title: topic,
    description: topicInfo?.description ?? "",
    prereqs,
  };
});

// TODO: Filter to top 100? articles
const filterTopics = (topicsInfo: TopicsMetaData): TopicsMetaData => {
  return Object.fromEntries(Object.entries(topicsInfo).filter(([title, {links, pageviews}]) => 
    pageviews && pageviews > 5000
    // && links && links.length > 5 // TODO: Link retrieval is broken
  ));
}

const getTopicInfo = async (
  topics: string[],
  { links, description, pageviews } = {
    links: true,
    description: true,
    pageviews: false,
  }
): Promise<TopicsMetaData> => {
  const props = [];
  if (links) props.push('links')
  if (pageviews) props.push('pageviews');
  if (description) props.push('extracts');
  const params: Record<string, any> = {
    "action": "query",
    "format": "json",
    "prop": props.join('|'),
    "titles": topics.slice(0, 50).join('|'),
    "formatversion": "2",
    "pllimit": "max",
  };
  if (description) {
    params["exintro"] = 1;
    params["explaintext"] = 1;
    params["exsectionformat"] = "plain";
  }
  const [results, status] = await fetchWiki<WikiTopicResponse>(params);
  if (status !== APIStatus.OKAY) {
    return {};
  }

  const metadata: Record<string, Record<string, any>> = {};
  results['query']['pages'].forEach(({ title, links, pageviews, extract }) => {
    metadata[title] = {};
    if (links) metadata[title]['links'] = links.map(({ title }) => title);
    if (pageviews) metadata[title]['pageviews'] = Object.values(pageviews).reduce((a, b) => a + b, 0);
    if (description) metadata[title]['description'] = extract;
  });
  return metadata;
}
