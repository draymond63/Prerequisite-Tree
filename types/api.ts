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
  image: string;
  prereqs: TopicsMetaData;
}

interface TopicMetaData {
  links?: string[];
  pageviews?: number;
  description?: string;
  image?: string;
}

type TopicsMetaData = Record<string, TopicMetaData>;