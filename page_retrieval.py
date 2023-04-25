import re
from utils import StringUtils
from typing import Optional, List
from xml.etree.cElementTree import iterparse


class PageRetriever:
	def __init__(self, file_path='datasets/raw/enwikibooks-20230401-pages-meta-current.xml', show_warnings=False):
		self.file_path = file_path
		self.show_warnings = show_warnings
	
	# TODO: Add progress bar
	def get(self, page_titles: Optional[List[str]] = None, regex: Optional[str] = None, pbar=False):
		if page_titles:
			page_titles = [title.replace('_', ' ') for title in page_titles]
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
			elif 'text' in element.tag and page_active and self.is_valid_title(page_title, page_titles, regex):
				page_count += 1
				page_text = self.clean_page_text(element.text)
				yield page_title, page_id, page_text
			if page_titles is not None and page_count >= len(page_titles):
				break

	def is_valid_title(self, page_title, pages: Optional[List[str]] = None, regex: Optional[str] = None) -> bool:
		if self.show_warnings and 'REDIRECT' in page_title:
			print(f'WARNING: {page_title} is a redirect')
		if pages is None and regex is None:
			return True
		elif regex:
			assert pages is None, "Cannot give Regex and page list to the PageRetriever"
			return bool(re.search(regex, page_title))
		else:
			return page_title in pages

	def get_article_text(self, page_title: str) -> str:
		title, page_id, text = next(self.get([page_title]))
		return text
	
	@staticmethod
	def clean_page_text(text: str) -> str:
		if not text:
			return ''
		cleaned_text = StringUtils.remove_wiki_links(text)
		cleaned_text = StringUtils.remove_tags(text)
		return cleaned_text

if __name__ == '__main__':
	# pages = pd.read_csv('datasets/departments.tsv', sep='\t').values.flatten().tolist()
	pages = ['Shelf:Systems_engineering', 'Control_Systems/System_Identification']
	for title, page_id, text in PageRetriever().get(regex='.*/Glossary'):
		print(title, page_id)
		# print(text)
		# print()
