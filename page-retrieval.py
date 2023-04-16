import pandas as pd
from xml.etree.cElementTree import Element, iterparse
from tqdm import tqdm
from typing import Optional, List


class PageRetriever:
	def __init__(self, file_path='datasets/raw/enwikibooks-20230401-pages-meta-current.xml', show_warnings=False):
		self.file_path = file_path
		self.show_warnings = show_warnings
	
	# TODO: Add progress bar
	def get(self, page_titles: Optional[List[str]] = None, pbar=False):
		root = iterparse(self.file_path)
		page_count = 0
		page_active, page_title, page_id, page_text = False, '', '', ''
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
				if page_active and self.is_valid_title(page_title, page_titles):
					page_count += 1
					yield page_title, page_id, page_text
			if page_titles is not None and page_count >= len(page_titles):
				break

	def is_valid_title(self, page_title, pages: Optional[List[str]] = None):
		if pages is None:
			return True
		if self.show_warnings and 'REDIRECT' in page_title:
			print(f'WARNING: {page_title} is a redirect')
		page_urend = page_title.replace(' ', '_') # Works for all but 11 (useless) article titles
		return page_urend in pages

def parse_headlines(text: str) -> list:
	print(text)
	headlines = []
	for line in text.split('\n'):
		if line.startswith('='):
			header = line.strip().strip('=').strip()
			headlines.append(header)
	return headlines

if __name__ == '__main__':
	pages = pd.read_csv('datasets/books.tsv', sep='\t').values.flatten().tolist()
	# pages = ['Shelf:Systems_engineering', 'Shelf:Systems_engineering/all_books', 'Systems_engineering']
	for title, page_id, text in PageRetriever().get(pages):
		print(title, text)
