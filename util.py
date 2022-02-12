from requests import get

WIKI_URL = "https://en.wikipedia.org/wiki/"
TOPIC_LISTS = 'storage/categories.csv'
TOPICS = 'storage/topics.csv'
COMPLEXITY = 'storage/complexity.csv'
COMPLEXITY = 'storage/citations.csv'

# mediawiki.org/w/api.php?action=help&modules=query%2Bextracts
def get_text(site, ignore=False) -> str:
    url = f"https://en.wikipedia.org/w/api.php?"
    resp = get(url, params={
        'action': 'query',
        'format': 'json',
        'origin': '*',
        'titles': site,
        'prop': 'extracts',
        'explaintext': 1,
        'exsectionformat': 'plain',
        'exlimit': 1
    }).json()
    try:
        # Parse out extract
        pages = list(resp['query']['pages'].values())
        for page in pages:
            if page and 'extract' in page:
                return page['extract']
    except (KeyError, IndexError) as e:
        if not ignore:
            raise e
        return ""