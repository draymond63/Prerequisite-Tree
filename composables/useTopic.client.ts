type UserTopic = Topic & {
  prereqs: Topics;
}

export const useTopic = (title: string, overwrite=false) => {
  const { $Gun } = useNuxtApp();
  const topic = $Gun.get(title);
  const topics = $Gun.get('topics');
  topics.set(topic); // Add to the global list of all topics

  const state = reactive<UserTopic>({
    title,
    description: "Loading...", // TODO: Better loading visual
    image: "",
    prereqs: {},
  });

  topic.once(async node => {
    // ! Putting the fetch in the top-level of the composable throws warning
    const { data } = await useFetch(() => `/api/topic`, { body: title, method: 'POST' });
    if (data.value && data.value[title]) {
      state.description = data.value[title].description;
      state.image = data.value[title].image || 'https://picsum.photos/seed/picsum/600/400';
    }
  });
  topic.get('prereqs').once(a => {});

  topic.get('prereqs').once(async (node) => {
    let prereqs = Object.keys(getNodeData(node));
    console.log("Current prereqs:", prereqs);
    if (!prereqs.length || overwrite) {
      console.log("Fetching prereqs");
      const { data } = await useFetch(() => `/api/prereqs?topic=${title}`);
      if (data.value) {
        prereqs = data.value;
        defineTopicRelations(title, prereqs);
      };
      console.log("New prereqs:", prereqs);
    }
    if (prereqs.length) {
      const { data: prereqInfo } = await useFetch(() => `/api/topic`, { body: prereqs, method: 'POST' });
      if (prereqInfo.value)
        state.prereqs = prereqInfo.value;
    } 
  });
  return state
}

const defineTopicRelations = (title: string, prereqs: string[]) => {
  const { $Gun } = useNuxtApp();
  const topic = $Gun.get(title);
  prereqs.map((prereqTitle) => {
    const prereq = $Gun.get(prereqTitle);
    prereq.get('leads-to').set(topic);
    topic.get('prereqs').set(prereq);
  });
}

const getNodeData = (node: Record<string, any>) => {
  const newNode = {...node};
  delete newNode['_'];
  return newNode;
}
