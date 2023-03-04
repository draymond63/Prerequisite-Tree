type UserTopic = Topic & {
  bookmarked: boolean;
  updateBookmark: (status: boolean) => void;
}

// TODO: Add optional pre-req retrieval
export const useTopic = (title: string, overwrite=false) => {
  const { $Gun } = useNuxtApp();
  const topic = $Gun.get(title);
  const bookmark = $Gun.get('user').get('bookmarks').get(title);

  const state = reactive({
    title,
    description: "Loading...",
    image: "",
    prereqs: {},
    bookmarked: false,
    updateBookmark: (status: boolean) => bookmark.put(status)
  } as UserTopic);

  topic.once((node) => {
    if (!node || overwrite) {
      const req = useFetch(() => `/api/topic?topic=${title}`);
      req.then(({ data }) => {
        if (data.value) {
          state.description = data.value.description;
          state.image = data.value.image;
          state.prereqs = data.value.prereqs
          setTopicGraph(title, data.value.prereqs);
        }
      })
    }
  })

  bookmark.once((status: boolean) => {
    state.bookmarked = status;
  });

  // TODO: Initial render not working
  bookmark.on((status: boolean) => {
    state.bookmarked = status;
  });
  return state
}

const setTopicGraph = (title: string, prereqs: TopicsMetaData) => {
  const { $Gun } = useNuxtApp();
  const topic = $Gun.get(title);
  Object.keys(prereqs).map((prereqTitle) => {
    const prereq = $Gun.get(prereqTitle);
    prereq.get('leads-to').set(topic);
    topic.get('prereqs').set(prereq);
  });
}
