export default defineEventHandler(async (event): Promise<Array<any>> => {
  const query = getQuery(event)['q'];
  if (query === null || query === undefined || query === "") {
    return [event.context];
  }
  const URL = "https://en.wikipedia.org/w/api.php";
  const params = {
    "action": "query",
    "format": "json",
    "prop": "extracts",
    "list": "",
    "meta": "",
    "generator": "allpages",
    "converttitles": "1",
    "formatversion": "2",
    "exintro": "1",
    "explaintext": "1",
    "exsectionformat": "plain",
    "gapfrom": query.toString(),
    "gaplimit": "3"
  };
  try {
    const results = await $fetch(URL, { params }) as any;
    if (results['error']) {
      return [results['error']['info']];
    }
    const pages = results['query']['pages'] || [];
    return pages.map(({ title }: {title: any}) => title);
  } catch(err) {
    return [(err as any).toString()];
  }
})