export const fetchWiki = async <T>(params: Record<string, any>, autoContinue=0): Promise<[WikiResponse<T>, APIStatus]> => {
  const URL = "https://en.wikipedia.org/w/api.php";
  let wikiParams = params;
  let continue_count = autoContinue + 1;
  const results: WikiResponse<T>[] = [];
  do {
    const result = await $fetch(URL, { params: wikiParams }) as WikiResponse<T>;
    // console.log('Result:', result);
    results.push(result)
    if (result.error) {
      console.error('error:', result.error)
      return [result, APIStatus.WIKI_FAILURE];
    }
    if (result.continue && result.limits) {
      wikiParams = Object.assign({}, wikiParams, result.continue);
      console.log('Continuing with new params:', wikiParams)
    }
    continue_count -= 1
  } while(continue_count && results[results.length - 1].continue)
  return [Object.assign({}, ...results), APIStatus.OKAY];
}

export enum APIStatus {
  OKAY = 0,
  WIKI_FAILURE = 1,
  UNKNOWN_FAILURE = 2,
}