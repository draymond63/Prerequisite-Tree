import { fetchWiki, APIStatus } from "../utils";
import { getPrereqsPrompt, queryGPT, parseList } from "../utils/gpt";

export default defineEventHandler(async (event): Promise<Topic | null> => {
  const topic = getQuery(event)['topic'];
  if (topic === null || topic === undefined || topic === "" || typeof(topic) !== "string") {
    console.error("Invalid topic!:", topic);
    return null;
  }
  console.log("Getting topic info");
  const topicInfo = (await getTopicInfo(
    [topic],
    ['links', 'extracts', 'pageimages'],
    { pllimit: '300' },
    20 // maxContinue
    ))[topic];
    console.log("Getting sub-topic info");
  const subTopicInfo = await getTopicInfo(topicInfo?.links ?? [], ['extracts', 'pageviews']);
  console.log("Article Sub-topics:", Object.keys(subTopicInfo).length);
  const bestSubTopics = filterTopics(subTopicInfo);
  const prereqTitles = await getGPTPrereqs(topic, bestSubTopics);
  const prereqs = Object.fromEntries(Object.entries(bestSubTopics).filter(
    ([title, info]) => prereqTitles.includes(title)
  ));
  console.log("Possible Prereqs:", Object.keys(bestSubTopics).length);
  console.log("GPT's prereqs:", prereqTitles);
  console.log("Final Prereqs:", Object.keys(prereqs).length);

  return {
    title: topic,
    image: topicInfo?.image ?? "",
    description: topicInfo?.description ?? "",
    prereqs,
  };
});

// TODO: Get GPT response
const getGPTPrereqs = async (topic: string, topicsInfo: TopicsMetaData): Promise<string[]> => {
  const articles = Object.keys(topicsInfo);
  const prompt = getPrereqsPrompt(topic, articles);
  const [response, status] = await queryGPT(prompt);
  if (![APIStatus.OKAY].includes(status)) {
    console.log("Error with GPT API");
    return [];
  }
  return parseList(response);
}

const filterTopics = (topicsInfo: TopicsMetaData, view_min = 5000, max = 100): TopicsMetaData => {
  let topicEntries = Object.entries(topicsInfo);
  topicEntries = topicEntries.filter(([title, {pageviews, description}]) => 
    pageviews && pageviews > view_min
    && description
  );
  console.log("Filter Sub-topics:", topicEntries.length);
  topicEntries = topicEntries.sort(([topicA, metaA], [topicB, metaB]) => (metaB.pageviews ?? 0) - (metaA.pageviews ?? 0));
  if (topicEntries.length > max)
    topicEntries.splice(max, topicEntries.length);
  return Object.fromEntries(topicEntries);
}

const getTopicInfo = async (
  topics: string[],
  props = ['links', 'extracts', 'pageviews', 'pageimages'],
  kwparams: Record<string, any> = {},
  maxContinue = 5,
  split = 50,
  ): Promise<TopicsMetaData> => {
  if (topics.length === 0) return {};
  const iterations = Math.ceil(topics.length / split);
  const metadata: Promise<TopicsMetaData>[] = [];
  let start = 0
  for (let i = 0; i < iterations; i++) {
    const results = _getTopicInfo(topics.slice(start, start + split), props, kwparams, maxContinue);
    metadata.push(results);
    start += split;
  }
  return Object.assign({}, ...(await Promise.all(metadata)));
}

const _getTopicInfo = async (
  topics: string[],
  props: string[],
  kwparams: Record<string, any>,
  maxContinue: number,
): Promise<TopicsMetaData> => {
  const params: Record<string, any> = {
    action: "query",
    format: "json",
    prop: props.join('|'),
    titles: topics.join('|'),
    formatversion: 2,
    plnamespace: 0,
    ...kwparams,
  };
  if (props.includes('pageimages')) params.pithumbsize = 600
  if (props.includes('extracts')) {
    params.exintro = 1;
    params.explaintext = 1;
    params.exsectionformat = "plain";
  }
  const [results, status] = await fetchWiki<WikiTopicResponse>(params, maxContinue);
  if (![APIStatus.OKAY, APIStatus.INCOMPLETE].includes(status)) {
    console.error(`Invalid API call. API Status: ${status} (Wiki error: ${results.error})`);
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
