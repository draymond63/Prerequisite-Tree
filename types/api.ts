interface Topic {
  title: string;
  description: string;
  image: string;
  wordcount?: number;
  id?: number;
}

interface TopicMetaData {
  links?: string[];
  pageviews?: number;
  description?: string;
  image?: string;
}

type Topics = Record<string, Topic>;
type TopicsMetaData = Record<string, TopicMetaData>;