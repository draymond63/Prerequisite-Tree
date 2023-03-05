type UserTopic = Topic & {
  prereqs: Topics;
}

export const useTopic = (title: string, overwrite=false) => {
  const { $Gun } = useNuxtApp();
  const topic = $Gun.get(title);
  const topics = $Gun.get('topics');
  topics.set(topic); // Add to the global list of all topics

  const state = reactive({
    title,
    description: "Loading...",
    image: "",
    prereqs: {},
  } as UserTopic);

  topic.once(async node => {
    // ! Putting the fetch in the top-level of the composable throws warning
    const req = useFetch(() => `/api/topic`, { body: title, method: 'POST' });
    req.then(({ data }) => {
      if (data.value && data.value[title]) {
        state.description = data.value[title].description;
        state.image = data.value[title].image;
      }
    });

    if (!node || overwrite) {
      const { data: prereqTitles } = await useFetch(() => `/api/prereqs?topic=${title}`);
      const prereqs = prereqTitles.value;
      if (prereqs) {
        defineTopicRelations(title, prereqs);
        const { data: prereqInfo } = await useFetch(() => `/api/topic`, { body: prereqs, method: 'POST' });
        if (prereqInfo.value)
          state.prereqs = prereqInfo.value;
      };
    }
  });

  // ! Works but doesn't update DOM because it's changing the state inside an object
  // topic.get('prereqs').map().on(async (info, title) => {
  //   if (!Object.keys(state.prereqs).includes(title)) {
  //     const { data: prereqInfo } = await useFetch(() => `/api/topic`, { body: [title], method: 'POST' });
  //     console.log(title, prereqInfo.value);
  //     if (prereqInfo.value && prereqInfo.value[title]) {
  //       state.prereqs[title] = prereqInfo.value[title];
  //     }
  //   }
  // });
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
