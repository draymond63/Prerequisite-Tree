import re
from typing import List, Tuple


class Article:
    def __init__(self, title: str, content: str) -> None:
        text = content.split('\n')
        path, text = text[0], text[1:]
        self.path = self.parse_path(path)
        self.sections = ArticleSection(title, text)
    
    def parse_path(self, text: str):
        return re.search(r'\{\{([^\]]+)\}\}', text).group(1).strip('*').strip()


class ArticleSection:
    header: str
    depth: int
    content: str
    children: 'List[ArticleSection]'

    def __init__(self, header: str, content: List[str], depth: int = 0) -> None:
        self.header = header
        self.depth = depth
        self.content = self.parse_preamble(content)
        self.children = self.parse_section(content)

    def parse_preamble(self, text: List[str]) -> str:
        preamble = text
        header_index = self._find_header(text)
        if header_index != -1:
            preamble = text[:header_index]
        return '\n'.join(preamble)

    def parse_section(self, text: List[str]) -> 'List[ArticleSection]':
        # Find subsections
        subsection_indices = []
        new_depth = self.depth + 1
        for index, line in enumerate(text):
            cleaned_line = line.strip()
            if cleaned_line[:new_depth] == '=' * new_depth and cleaned_line[new_depth] != '=':
                subsection_indices.append(index)

        # If there are no subsections, return the content. If there are deeper subsections, go deeper
        if not len(subsection_indices):
            if self._find_header(text) == -1:
                return []
            return [ArticleSection(self.header, text, new_depth)]

        # Parse subections
        content = []
        subsection_indices.append(len(text))
        for subsection_start, subsection_end in zip(subsection_indices[:-1], subsection_indices[1:]):
            header = text[subsection_start].strip('=').strip()
            subection_content = text[subsection_start + 1: subsection_end]
            content.append(ArticleSection(header, subection_content, new_depth))

        # TODO: Add content that is not in a subsection
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
                complete_header = f'{self.header}/{header}'
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
