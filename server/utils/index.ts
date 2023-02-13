export const fetchWiki = async <T>(params: Record<string, any>): Promise<[WikiResponse<T>, APIStatus]> => {
  const URL = "https://en.wikipedia.org/w/api.php";
  const results = await $fetch(URL, { params }) as any;
  if (results['error']) {
    return [results, APIStatus.WIKI_FAILURE];
  }
  return [results, APIStatus.OKAY];
}

export enum APIStatus {
  OKAY = 0,
  WIKI_FAILURE = 1,
  UNKNOWN_FAILURE = 2,
}