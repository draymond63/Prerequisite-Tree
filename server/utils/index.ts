export { getTopicInfo, fetchWiki } from './wiki';
export { queryGPT, parseList } from './gpt';

export enum APIStatus {
  OKAY = 0,
  WIKI_FAILURE = 1,
  INVALID_INPUT = 2,
  UNKNOWN_FAILURE = 3,
  INCOMPLETE = 4,
}
