interface WikiResponse<T extends WikiPage = WikiPage> {
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

interface WikiPage {
  ns: number;
  title: string;
  pageid: number;
}

interface WikiSearchResponse extends WikiPage {
  index: number;
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

interface WikiTopicResponse extends WikiPage {
  timestamp: string;
  extract?: string;
  pageviews?: Record<string, number>;
  links?: {
    ns: number;
    title: string;
  }[];
  thumbnail?: {
    source: string;
    width: number;
    height: number;
  },
  pageimage?: string;
}