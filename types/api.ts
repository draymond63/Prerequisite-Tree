interface WikiResponse<T> {
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

interface WikiMediaResponse {
  items?: {
    project: string;
    article: string;
    granularity: string;
    timestamp: string;
    access: string;
    agent: string;
    views: number;
  }[]
}

interface WikiArticleResponse {
  ns: number;
  title: string;
  index: number;
  pageid: number;
  size: number;
  wordcount: number;
  extract: string;
  timestamp: string;
}

type WikiLinksResponse = {
  links: {
    ns: number;
    title: string;
  }[];
};

interface Article {
  id: number;
  wordcount: number;
  title: string;
  extract: string;
}

interface Topic {
  title: string;
  description: string;
  prereqs: string[];
}