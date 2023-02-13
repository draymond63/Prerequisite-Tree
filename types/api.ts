interface Article {
  id: number;
  wordcount: number;
  title: string;
  extract: string;
  image: string;
}

interface Topic {
  title: string;
  description: string;
  prereqs: string[];
}

interface TopicMetaData {
  links?: string[];
  pageviews?: number;
  description?: string;
}

type TopicsMetaData = Record<string, TopicMetaData>;