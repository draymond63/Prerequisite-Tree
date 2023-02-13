interface WikiArticleResponse {
  ns: number;
  title: string;
  pageid: number;
  size: number;
  wordcount: number;
  snippet: string;
  timestamp: string;
}

interface Article {
  id: number;
  wordcount?: number;
  title: string;
  snippet: string;
}