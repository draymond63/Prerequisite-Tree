import pandas as pd
from xml.etree.cElementTree import Element, iterparse

def get_pages(query: list):
	file_path = 'datasets/raw/enwikibooks-20230401-pages-meta-current.xml'
	root = iterparse(file_path)
	page_active = False
	current_title = None
	current_id = None
	current_text = None
	calls_made = 0
	element: Element
	for event, element in root:
		if 'page' in element.tag:
			page_active = True
		elif 'revision' in element.tag:
			page_active = False
			current_title = None
			current_id = None
			current_text = None
		elif 'title' in element.tag:
			current_title = element.text
		elif 'id' in element.tag:
			current_id = element.text
		elif 'text' in element.tag:
			current_text = element.text
			if page_active and current_title in query:
				if 'REDIRECT' in current_text:
					print(f'WARNING: {current_title} is a redirect')
				calls_made += 1
				yield current_title, current_id, current_text
		if calls_made >= len(query):
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
	pages = pd.read_csv('datasets/departments.tsv', sep='\t', header=None).values.flatten().tolist()
	for title, id, text in get_pages(pages):
		print(parse_headlines(text))