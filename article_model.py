import re
from typing import List, Optional


class Article:
    def __init__(self, title: str, content: str) -> None:
        text = content.split('\n')
        path, text = text[0], text[1:]
        self.path = self.parse_path(path)
        self.sections = ArticleSection(title, text)
    
    def parse_path(self, text: str) -> Optional[str]:
        matched_path = re.search(r'\{\{([^\]]+)\}\}', text)
        if matched_path:
            return matched_path.group(1).strip('*').strip()


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
        return self.clean_content('\n'.join(preamble))

    @staticmethod
    def clean_content(text: str) -> str:
        return text.replace("'''", '')

    def parse_section(self, text: List[str]) -> 'List[ArticleSection]':
        subsection_indices = self._find_subsections(text)
        # If there are no subsections, return the content. If there are deeper subsections, go deeper
        if not len(subsection_indices):
            if self._find_header(text) == -1:
                return []
            return [ArticleSection(self.header, text, self.depth + 1)]
        content = self._parse_subsections(text, subsection_indices)
        return content

    def _find_subsections(self, text):
        new_depth = self.depth + 1
        subsection_indices = []
        for index, line in enumerate(text):
            cleaned_line = line.strip()
            if cleaned_line[:new_depth] == '=' * new_depth and cleaned_line[new_depth] != '=':
                subsection_indices.append(index)
        return subsection_indices

    def _parse_subsections(self, text, subsection_indices):
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
        yield self.header, self.content, self.depth
        for section in self.children:
            for header, content, depth in section:
                complete_header = f'{self.header}/{header}' if not self.header in header else header
                yield complete_header, content, depth

    def get_content(self) -> str:
        output = f'\n{"=" * self.depth} {self.header} {"=" * self.depth}'
        output += self.content
        for sections in self.children:
            output += sections.get_content()
        return output

    def __str__(self) -> str:
        return f'Section: {self.header} ({self.depth})'


if __name__ == '__main__':
    title = 'Control Systems'
    text = open('datasets/scratch/article_example.md').read()
    article = Article(title, text)
    content = article.sections.get_content()
    open('test.txt', 'w').write(content)

    for header, content, depth in article.sections:
        print(header, depth)
