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

type WikiLinksResponse = Array<{
  ns: number;
  title: string;
}>

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