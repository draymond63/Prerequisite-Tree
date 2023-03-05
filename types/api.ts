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
}

interface TopicMetaData {
  links?: string[];
  pageviews?: number;
  description?: string;
  image?: string;
}

type Topics = Record<string, Topic>;
type TopicsMetaData = Record<string, TopicMetaData>;