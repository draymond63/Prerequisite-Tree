import re
from typing import List, Optional


class Article:
	def __init__(self, title: str, content: str) -> None:
		text = self.clean_content(content).split('\n')
		self.title = title
		path = text[0]
		self.path = self.parse_path(path)
		if self.path is not None:
			text = text[1:]
		self.sections = ArticleSection(title, text)

	@staticmethod
	def clean_content(text: str) -> str:
		cleaned_text = text.replace("'''", '')
		cleaned_text = re.sub(r'^;([^:]+):', r'====\1====\n', cleaned_text, flags=re.MULTILINE)
		return cleaned_text.strip()

	def parse_path(self, text: str) -> Optional[str]:
		matched_path = re.search(r'\{\{([^\]]+)\}\}', text)
		if matched_path:
			return matched_path.group(1).strip('*').strip()

	def get_section(self, header_path: List[str]) -> 'Optional[ArticleSection]':
		return self.sections.get_section([self.title, *header_path])
	
	def find_section(self, header: str) -> 'Optional[ArticleSection]':
		return self.sections.find_section(header)

	def get_content(self) -> str:
		return self.sections.get_content()


class ArticleSection:
	header: str
	depth: int
	content: str
	children: 'List[ArticleSection]'

	def __init__(self, header: str, content: List[str], depth: int = 0) -> None:
		self.header = header
		self.depth = depth
		self.content = self._parse_preamble(content)
		self.children = self.parse_section(content)

	def _parse_preamble(self, text: List[str]) -> str:
		preamble = text
		header_index = self._find_header(text)
		if header_index != -1:
			preamble = text[:header_index]
		return '\n'.join(preamble).strip()

	def parse_section(self, text: List[str]) -> 'List[ArticleSection]':
		subsection_indices = self._find_subsections(text)
		# If there are no subsections, return the content. If there are deeper subsections, go deeper
		if not len(subsection_indices):
			if self._find_header(text) == -1:
				return []
			self.depth += 1
			return self.parse_section(text)
		content = self._parse_subsections(text, subsection_indices)
		return content

	# TODO: Switch to regex
	def _find_subsections(self, text: List[str]) -> List[int]:
		subsection_indices = []
		for index, line in enumerate(text):
			if self.is_header(line):
				subsection_indices.append(index)
		return subsection_indices

	def is_header(self, line: str) -> bool:
		new_depth = self.depth + 1
		cleaned_line = line.strip()
		return cleaned_line[:new_depth] == '=' * new_depth and cleaned_line[new_depth] != '='

	def _parse_subsections(self, text: List[str], subsection_indices: List[int]):
		content = []
		subsection_indices.append(len(text))
		for subsection_start, subsection_end in zip(subsection_indices[:-1], subsection_indices[1:]):
			header = text[subsection_start].strip('=').strip()
			subection_content = text[subsection_start + 1: subsection_end]
			content.append(ArticleSection(header, subection_content, self.depth + 1))
		return content

	@staticmethod
	def _find_header(text: List[str]) -> int:
		for index, line in enumerate(text):
			cleaned_line = line.strip()
			if cleaned_line and cleaned_line[0] == '=':
				return index
		return -1

	def __iter__(self):
		return self.iter()
	
	def iter(self, leaves_only: bool = False):
		if not leaves_only or not self.children:
			yield self
		for section in self.children:
			for child in section.iter(leaves_only):
				yield child

	def iter_headers(self):
		yield [self.header]
		for section in self.children:
			for header in section.iter_headers():
				header.insert(0, self.header)
				yield header

	def get_content(self) -> str:
		output = f'\n{"=" * self.depth} {self.header} {"=" * self.depth}'
		output += '\n' + self.content
		for sections in self.children:
			output += sections.get_content()
		return output

	def find_sections_matching(self, condition: callable) -> 'List[ArticleSection]':
		sections = []
		if condition(self):
			sections.append(self)
		for section in self.children:
			sections.extend(section.find_sections_matching(condition))
		return sections

	def find_section(self, header: str) -> 'Optional[ArticleSection]':
		found_sections = self.find_sections_matching(lambda section: section.header == header)
		if len(found_sections) >= 1:
			return found_sections[-1]

	def get_section(self, header_path: List[str]) -> 'Optional[ArticleSection]':
		if len(header_path) == 1 and header_path[0] == self.header:
			return self
		for section in self.children:
			retrieved_child = section.get_section(header_path[1:])
			if retrieved_child is not None:
				return retrieved_child

	def __str__(self) -> str:
		return f'Section: {self.header} ({self.depth})'


if __name__ == '__main__':
	title = 'Control Systems'
	text = open('datasets/scratch/article_example.md').read()
	article = Article(title, text)
	content = article.sections.get_content()
	print(content)

	# sect = article.find_section('Systems')
	# print(sect.content)

	# for section in article.sections:
	#     print(section.header)
	#     print(section.content)
	#     print('  ' * section.depth, f'{section.depth}. {section.header}')
	#     found_section = article.find_section(section.header)
	#     if section != found_section:
	#         print(f'ERROR: {section.header} != {found_section.header}')
	#     else:
	#         print(f'OK: {section.header} == {found_section.header}')