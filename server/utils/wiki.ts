import { APIStatus } from './index';

export const getTopicInfo = async (
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

export const fetchWiki = async <T extends WikiPage>(params: Record<string, any>, autoContinue=0): Promise<[WikiResponse<T>, APIStatus]> => {
  const URL = "https://en.wikipedia.org/w/api.php";
  let wikiParams = params;
  let continue_count = autoContinue + 1;
  const results: WikiResponse<T>[] = [];
  do {
    const result = await $fetch(URL, { params: wikiParams }) as WikiResponse<T>;
    results.push(result);
    if (result.error) {
      console.error('error:', result.error);
      return [result, APIStatus.WIKI_FAILURE];
    }
    if (result.continue) {
      wikiParams = Object.assign({}, wikiParams, result.continue);
    }
    continue_count -= 1
  } while(continue_count && results[results.length - 1].continue);
  return _mergeResults(results);
}

// Prevents results from overriding each other
const _mergeResults = <T extends WikiPage>(responses: WikiResponse<T>[]): [WikiResponse<T>, APIStatus] => {
  const mergedResults: WikiResponse<T> = Object.assign({}, ...responses);
  
  const batch_complete = responses.reduce<boolean>((x, resp) => x || (resp.batchcomplete ?? false), false); 
  mergedResults.batchcomplete = batch_complete;
  // Results in a bunch of duplicate pages -> Need to recursively merge each pages properties
  const pages = responses.map(({query}) => query.pages).flat();
  
  mergedResults.query.pages = groupByTitle(pages).map(_mergeObjects);
  const status = batch_complete ? APIStatus.OKAY : APIStatus.INCOMPLETE;
  return [mergedResults, status];
}

const groupByTitle = <T extends WikiPage>(pages: T[]): T[][] => { 
  const groupedPages: Record<string, T[]> = {};
  pages.forEach(page => {
    if (!(page.title in groupedPages)) {
      groupedPages[page.title] = [];
    }
    groupedPages[page.title].push(page);
  })
  return Object.values(groupedPages)
}

const _mergeObjects = <T extends Record<string, any>>(objects: T[]): T => {
  const newObj: T = Object.assign({}, ...objects);
  const entries = Object.entries(newObj).map( // TODO: Not recursive
    ([key, value]) => [key, Array.isArray(value) ? objects.map(obj => obj[key]).flat() : value]
  );
  return Object.fromEntries(entries);
}