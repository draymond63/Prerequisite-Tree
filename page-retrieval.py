import pandas as pd
from xml.etree.cElementTree import Element, iterparse
from tqdm import tqdm
from typing import Optional, Iterable

def get_pages(query: Optional[Iterable[str]] = None):
	file_path = 'datasets/raw/enwikibooks-20230401-pages-meta-current.xml'
	root = iterparse(file_path)
	page_active, page_title, page_id, page_text = False, '', '', ''
	calls_made = 0
	element: Element
	for event, element in root:
		if 'page' in element.tag:
			page_active = True
		elif 'revision' in element.tag:
			page_active, page_title, page_id, page_text = False, '', '', ''
		elif 'title' in element.tag:
			page_title = element.text
		elif 'id' in element.tag:
			page_id = element.text
		elif 'text' in element.tag:
			page_text = element.text
			valid_title = query is None or page_title in query
			if page_active and valid_title:
				# if 'REDIRECT' in page_text:
				# 	print(f'WARNING: {page_title} is a redirect')
				# else:
				# 	print(page_title)
				calls_made += 1
				yield page_title, page_id, page_text
		if query is not None and calls_made >= len(query):
			break

def parse_headlines(text: str) -> list:
	print(text)
	headlines = []
	for line in text.split('\n'):
		if line.startswith('='):
			header = line.strip().strip('=').strip()
			headlines.append(header)
	return headlines

if __name__ == '__main__':
	pages = pd.read_csv('datasets/articles.tsv', sep='\t').values.flatten().tolist()
	# pages = ['Shelf:Systems_engineering', 'Shelf:Systems_engineering/all_books', 'Systems_engineering']
	for title, page_id, text in tqdm(get_pages(pages), total=len(pages)):
		print(title, parse_headlines(text))
