import { getTopicInfo, APIStatus, queryGPT, parseList } from "../utils";

// Get Prerequisites: Get a list titles of prerequisites for a given topic
export default defineEventHandler(async (event): Promise<string[]> => {
  const topic = getQuery(event)['topic'];
  if (topic === null || topic === undefined || topic === "" || typeof(topic) !== "string") {
    console.error("Invalid topic!:", topic);
    return [];
  }
  return [
    "Mathematics",
    "Fourier transform",
    "Calculus",
    "Linear algebra",
    "Differential equation"
  ];
  const topicInfo = (await getTopicInfo([topic], ['links'], { pllimit: '300' }, 20))[topic];
  const subTopicInfo = await getTopicInfo(topicInfo?.links ?? [], ['extracts', 'pageviews']);
  console.log("Article Sub-topics:", Object.keys(subTopicInfo).length);
  const bestSubTopics = filterTopics(subTopicInfo);
  const prereqTitles = await getGPTPrereqs(topic, bestSubTopics);
  const prereqs = Object.fromEntries(Object.entries(bestSubTopics).filter(
    ([title, info]) => prereqTitles.some(item => item.toLowerCase() === title.toLowerCase())
  ));
  const numMissing = prereqTitles.length - Object.keys(prereqs).length;
  if (numMissing) {
    console.log(`${numMissing} invalid GPT responses for pre-requisites (${prereqTitles})`);
  }

  console.log("Possible Prereqs:", Object.keys(bestSubTopics).length);
  console.log("Final Prereqs:", Object.keys(prereqs).length);

  return Object.keys(prereqs);
});

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

export const getPrereqsPrompt = (topic: string, options: string[]): string => {
  console.log(options);
  return `The following is a list of topics related to "${topic}". 

${options.join('\n')}

The following is a list of the five most specific prerequisites for "${topic}". All prerequisites are from the list above and use the exact same format:
1.`;
}