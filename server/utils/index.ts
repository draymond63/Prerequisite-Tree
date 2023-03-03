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

export enum APIStatus {
  OKAY = 0,
  WIKI_FAILURE = 1,
  INVALID_INPUT = 2,
  UNKNOWN_FAILURE = 3,
  INCOMPLETE = 4,
}