import os
from bs4 import BeautifulSoup
from bs4.element import PageElement
from requests import get
from tqdm import tqdm

import pandas as pd
from util import TOPIC_LISTS, TOPICS, WIKI_URL

def get_title(tag: PageElement):
	return tag.text.removesuffix('[edit]').strip()

def parse_wiki(uri: str, clean=True, endings=('references', 'see also')):
	columns = ['h1', 'h2', 'h3', 'h4', 'li']
	# Start adding data to the levels dict
	df = pd.DataFrame(columns=columns)
	last_h = [None] * (len(columns) - 1) # h1-4

	ignore = (
		'help:', 'index', 'wikipedia', 'cookie_statement', 'how_to_contribute', 'category:',
		'special:', 'talk:', 'portal:', 'terms_of_Use', '#', 'privacy_policy', 'main_page'
	)
	ignore_titles = ('Wikidata item')
	# Get data from wikipedia
	response = get(WIKI_URL + uri)
	soup = BeautifulSoup(response.text, 'html.parser').find('div', id='mw-content-text')
	assert soup, "No 'mw-content-text' in article"
	# Remove toc
	toc = soup.find('div', id='toc')
	if toc: toc.decompose()
	
	# Descendants gets access to all tags, children is only surface level
	for tag in soup.descendants:
		if tag.name and tag.name[0] == 'h' and len(tag.name) == 2:
			title = get_title(tag)
			# Typically the last section in an article
			if (not clean) or (title.lower() in endings):
				break
			n = int(tag.name[1]) - 1 # Header value (0 indexed)
			# Fill the most recent header with values
			for i in range(n, len(last_h)):
				last_h[i] = title

		# Get wiki articles (found in lists of links)
		if tag.name == 'li' and last_h[-1]:
			tag = tag.find('a')
			if tag and tag.get('href'):
				# Get the title
				title = get_title(tag)
				# Add url to the Dataframe
				url = tag.get('href').split('/')[-1]
				if not (clean
					and any(c in url.lower() for c in ignore)
					and any(c in title.lower() for c in ignore_titles)):
					df.loc[url] = [*last_h, title]
	return df

def clean_topics(df: pd.DataFrame) -> pd.DataFrame:
	# Remove lists from topics
	df.index = df.index.astype('str')
	df = df[~df.index.str.contains('List')]
	# Remove non-english/strange articles
	df = df[df.index.str.count('%') < 15]
	# h1 column is empty
	if not any(df['h1']):
		df.drop('h1', axis='columns', inplace=True)
	return df

def get_data():
	if os.path.exists(TOPIC_LISTS):
		df = pd.read_csv(TOPIC_LISTS, index_col='Unnamed: 0')
	else:
		df = parse_wiki('Lists_of_mathematics_topics', endings=('v', 'see also', 'equations named after people'))
		df.drop('List_of_numbers', inplace=True) # We don't want the list of nubmers
		df.to_csv(TOPIC_LISTS)

	articles = []
	for uri in tqdm(df.index):
		a = parse_wiki(uri)
		a['uri'] = [uri] * len(a)
		articles.append(a)
	# Combine into one dataframe
	df = pd.concat(articles)
	# df = pd.read_csv(TOPICS, index_col='Unnamed: 0')
	df = clean_topics(df)
	df.to_csv(TOPICS)



if __name__ == "__main__":
	get_data()