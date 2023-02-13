// TODO: Filter results by views, number of links, etc.

export default defineEventHandler(async (event): Promise<Array<Article>> => {
  const query = getQuery(event)['q'];
  if (query === null || query === undefined || query === "") {
    console.error("error: query is null or undefined or empty");
    return [];
  }
  const URL = "https://en.wikipedia.org/w/api.php";
  const params = {
    "action": "query",
    "format": "json",
    "list": "search",
    "formatversion": "2",
    "srsearch": query,
  };
  try {
    const results = await $fetch(URL, { params }) as any;
    if (results['error']) {
      return [results['error']['info']];
    }
    const pages: Array<WikiArticleResponse> = results['query']['search'] || [];
    return pages.map((page) => ({
      id: page.pageid,
      wordcount: page.wordcount,
      title: page.title,
      snippet: page.snippet
    }));
  } catch(err) {
    console.error(err);
    return [];
  }
})

/*
"query": {
  "searchinfo": {
    "totalhits": 66753
  },
  "search": [
    {
      "ns": 0,
      "title": "Control theory",
      "pageid": 7039,
      "size": 55379,
      "wordcount": 7315,
      "snippet": "<span class=\"searchmatch\">Control</span> <span class=\"searchmatch\">theory</span> is a field of mathematics that deals with the <span class=\"searchmatch\">control</span> of dynamical systems in engineered processes and machines. The objective is to develop",
      "timestamp": "2023-02-02T07:36:42Z"
    },
  ]
}
*/