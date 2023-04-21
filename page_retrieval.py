import re
import pandas as pd
from tqdm import tqdm
from typing import Optional, List, Dict
from xml.etree.cElementTree import iterparse


class PageRetriever:
	def __init__(self, file_path='datasets/raw/enwikibooks-20230401-pages-meta-current.xml', show_warnings=False):
		self.file_path = file_path
		self.show_warnings = show_warnings
	
	# TODO: Add progress bar
	def get(self, page_titles: Optional[List[str]] = None, regex: Optional[str] = None, pbar=False):
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
				page_text = self.remove_wiki_links(element.text) if element.text else ''
				if page_active and self.is_valid_title(page_title, page_titles, regex):
					page_count += 1
					yield page_title, page_id, page_text
			if page_titles is not None and page_count >= len(page_titles):
				break

	def is_valid_title(self, page_title, pages: Optional[List[str]] = None, regex: Optional[str] = None) -> bool:
		page_urend = page_title.replace(' ', '_') # Works for all but 11 (useless) article titles
		if self.show_warnings and 'REDIRECT' in page_title:
			print(f'WARNING: {page_title} is a redirect')
		if pages is None and regex is None:
			return True
		elif regex:
			return bool(re.search(regex, page_urend))
		else:
			return page_urend in pages
	
	def get_article_text(self, page_title: str) -> str:
		title, page_id, text = next(self.get([page_title]))
		return text
	
	@staticmethod
	def remove_wiki_links(text: str) -> str:
		unlinked_text = re.sub(r'\[\[.*?\|([^\]]+)\]\]', r'\1', text)
		return re.sub(r'\[\[.*\]\]', '', unlinked_text)

# TODO: Clean text
def parse_sections(text: str) -> Dict[str, str]:
	text_lines = text.split('\n')
	sections = {}
	current_section = None
	section_start_index = None
	for current_index, line in enumerate(text_lines):
		cleaned_line = line.strip()
		if cleaned_line.startswith('='):
			if current_section:
				paragraph = '\n'.join(text_lines[section_start_index:current_index])
				sections[current_section] = paragraph.strip()
			current_section = cleaned_line.strip('=').strip()
			section_start_index = current_index + 1
	if current_section not in sections:
		paragraph = '\n'.join(text_lines[section_start_index:])
		sections[current_section] = paragraph.strip()	
	return sections

if __name__ == '__main__':
	# pages = pd.read_csv('datasets/departments.tsv', sep='\t').values.flatten().tolist()
	pages = ['Shelf:Systems_engineering', 'Control_Systems/System_Identification']
	for title, page_id, text in PageRetriever().get(regex='.*/Glossary'):
		print(title, page_id)
		# print(text)
		# print()
