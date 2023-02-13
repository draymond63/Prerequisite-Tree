interface WikiResponse<T> {
  batchcomplete?: boolean;
  limits?: Record<string, number>;
  continue?: {
    continue: string;
  };
  error?: {
    info: string;
  }
  query: {
    pages: T[];
  };
}

interface WikiSearchResponse {
  ns: number;
  title: string;
  index: number;
  pageid: number;
  size: number;
  wordcount: number;
  extract: string;
  timestamp: string;
  thumbnail: {
    source: string;
    width: number;
    height: number;
  },
  pageimage: string;
}

interface WikiTopicResponse {
  ns: number;
  pageid: number;
  title: string;
  timestamp: string;
  extract?: string;
  pageviews?: Record<string, number>;
  links?: {
    ns: number;
    title: string;
  }[];
}