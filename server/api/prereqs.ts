import { getTopicInfo, APIStatus, queryGPT, parseList } from "../utils";

// Get Prerequisites: Get a list titles of prerequisites for a given topic
export default defineEventHandler(async (event): Promise<string[]> => {
  console.log("Fetching pre-reqs");
  const topic = getQuery(event)['topic'];
  if (topic === "" || typeof(topic) !== "string") {
    console.error("Invalid topic!:", topic);
    return [];
  }
  const topicInfo = (await getTopicInfo([topic], ['links'], { pllimit: '300' }, 20))[topic];
  console.log("Topic Info:", Object.keys(topicInfo).length);
  const subTopicInfo = await getTopicInfo(topicInfo?.links ?? [], ['extracts', 'pageviews']);
  console.log("Article Sub-topics:", Object.keys(subTopicInfo).length);
  const bestSubTopics = filterTopics(subTopicInfo);
  const prereqs = await getGPTPrereqs(topic, bestSubTopics);
  const validPrereqs = prereqs.filter(title => bestSubTopics.some(item => item.toLowerCase() === title.toLowerCase()));
  const numMissing = prereqs.length - validPrereqs.length;
  if (numMissing) {
    console.log(`${numMissing} invalid GPT responses for pre-requisites (${prereqs})`);
  }
  console.log("Possible Prereqs:", bestSubTopics.length);
  console.log("Chosen Prereqs:", prereqs.length);
  console.log("Final Prereqs:", validPrereqs.length);

  return validPrereqs;
});

const getGPTPrereqs = async (topic: string, articles: string[]): Promise<string[]> => {
  const prompt = getPrereqsPrompt(topic, articles);
  const [response, status] = await queryGPT(prompt);
  if (![APIStatus.OKAY].includes(status)) {
    console.log("Error with GPT API");
    return [];
  }
  return parseList(response);
}

const filterTopics = (topicsInfo: TopicsMetaData, view_min = 5000, max = 100): string[] => {
  let topicEntries = Object.entries(topicsInfo);
  topicEntries = topicEntries.filter(([title, {pageviews, description}]) => 
    pageviews && pageviews > view_min
    && description
  );
  console.log("Filter Sub-topics:", topicEntries.length);
  topicEntries = topicEntries.sort(([topicA, metaA], [topicB, metaB]) => (metaB.pageviews ?? 0) - (metaA.pageviews ?? 0));
  if (topicEntries.length > max)
    topicEntries.splice(max, topicEntries.length);
  return Object.keys(Object.fromEntries(topicEntries));
}

export const getPrereqsPrompt = (topic: string, options: string[]): string => {
  console.log(options);
  return `The following is a list of topics related to "${topic}". 

${options.join('\n')}

The following is a list of the five most specific prerequisites for "${topic}". All prerequisites are from the list above and use the exact same format. Do not pluralize or change the format of the prerequisites:
1.`;
}