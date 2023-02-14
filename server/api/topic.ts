import { fetchWiki, APIStatus } from "../utils";

export default defineEventHandler(async (event): Promise<Topic | null> => {
  const topic = getQuery(event)['topic'];
  if (topic === null || topic === undefined || topic === "" || typeof(topic) !== "string") {
    console.error("Invalid topic!:", topic);
    return null;
  }
  const topicInfo = (await getTopicInfo([topic], ['links', 'extracts', 'pageimages']))[topic];
  const subTopicInfo = await getTopicInfo(topicInfo?.links ?? [], ['links', 'extracts', 'pageviews']);
  console.log("sub-topics:", Object.keys(subTopicInfo).length);

  const possiblePrereqs = filterTopics(subTopicInfo);
  console.log("possiblePrereqs:", Object.keys(possiblePrereqs).length);

  const prereqTitles = await queryGPT(possiblePrereqs);

  const prereqs = Object.fromEntries(Object.entries(possiblePrereqs).filter(
    ([title, info]) => prereqTitles.includes(title)
  ));
  console.log("prereqs:", Object.keys(prereqs).length);

  return {
    title: topic,
    image: topicInfo?.image ?? "",
    description: topicInfo?.description ?? "",
    prereqs,
  };
});

// TODO: Get GPT response
const queryGPT = async (topicsInfo: TopicsMetaData): Promise<string[]> => {
  return Object.keys(topicsInfo);
}

// TODO: Filter to top 100? articles
const filterTopics = (topicsInfo: TopicsMetaData): TopicsMetaData => {
  return Object.fromEntries(Object.entries(topicsInfo).filter(([title, {links, pageviews, description}]) => 
    pageviews && pageviews > 1000
    // && links && links.length > 5 // TODO: Link retrieval is maxed out ?
    && description
  ));
}

const getTopicInfo = async (
  topics: string[],
  props = ['links', 'extracts', 'pageviews', 'pageimages'],
  split = 50
): Promise<TopicsMetaData> => {
  if (topics.length === 0) return {};
  const iterations = Math.ceil(topics.length / split);
  const metadata: Promise<TopicsMetaData>[] = [];
  let start = 0
  for (let i = 0; i < iterations; i++) {
    const results = _getTopicInfo(topics.slice(start, start + split), props);
    metadata.push(results);
    start += split;
  }
  return Object.assign({}, ...(await Promise.all(metadata)));
}

const _getTopicInfo = async (
  topics: string[],
  props = ['links', 'extracts', 'pageviews', 'pageimages']
): Promise<TopicsMetaData> => {
  const params: Record<string, any> = {
    action: "query",
    format: "json",
    prop: props.join('|'),
    titles: topics.join('|'),
    formatversion: "2",
    pllimit: "max",
  };
  if (props.includes('pageimages')) params.pithumbsize = 600
  if (props.includes('extracts')) {
    params.exintro = 1;
    params.explaintext = 1;
    params.exsectionformat = "plain";
  }
  const [results, status] = await fetchWiki<WikiTopicResponse>(params);
  if (status !== APIStatus.OKAY) {
    return {};
  }

  const metadata: Record<string, Record<string, any>> = {};
  results['query']['pages'].forEach(({ title, links, pageviews, extract, thumbnail }) => {
    metadata[title] = {};
    if (props.includes('links')) metadata[title].links = links?.map(({ title }) => title);
    if (props.includes('extracts')) metadata[title].description = extract;
    if (props.includes('pageimages')) metadata[title].image = thumbnail?.source ?? "";
    if (props.includes('pageviews'))
      metadata[title].pageviews = Object.values(pageviews ?? {}).reduce((a, b) => a + b, 0);
  });
  return metadata;
}
