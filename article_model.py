import re
from typing import List, Tuple


class Article:
    def __init__(self, title: str, content: str) -> None:
        text = content.split('\n')
        self.path = self.parse_path(text[0])
        self.sections = ArticleSection(title, text)
    
    def parse_path(self, text: str):
        return re.search(r'\{\{([^\]]+)\}\}', text).group(1).strip('*').strip()


class ArticleSection:
    content: 'str | List[ArticleSection]' # TODO: Convert to 'List[str | ArticleSection]'

    def __init__(self, header: str, content: List[str], depth: int = 0) -> None:
        self.header = header
        self.depth = depth
        self.content = self.parse_section(content)

    def parse_section(self, text: List[str]) -> 'str | List[ArticleSection]':
        # Find subsections
        subsection_indices = []
        new_depth = self.depth + 1
        for index, line in enumerate(text):
            cleaned_line = line.strip()
            if cleaned_line[:new_depth] == '=' * new_depth and cleaned_line[new_depth] != '=':
                subsection_indices.append(index)

        # If there are no subsections, return the content
        if not len(subsection_indices):
            if not self.contains_headers(text):
                return '\n'.join(text).strip()
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
    def contains_headers(text: List[str]) -> bool:
        for line in text:
            cleaned_line = line.strip()
            if cleaned_line and cleaned_line[0] == '=':
                return True
        return False

    def __iter__(self):
        if isinstance(self.content, str):
            yield self.header, self.content
        else:
            for section in self.content:
                for header, content in section:
                    complete_header = f'{self.header}/{header}'
                    yield complete_header, content

    def get_content(self) -> str:
        output = f'{"=" * self.depth} {self.header} {"=" * self.depth}\n'
        if isinstance(self.content, str):
            output += self.content + '\n'
        else:
            for sections in self.content:
                output += sections.get_content()
        return output

    def __str__(self) -> str:
        return f'Section: {self.header} ({self.depth})'


if __name__ == '__main__':
    title = 'Article'
    text = open('datasets/scratch/article_example.md').read()
    article = Article(title, text)
    # print(article.sections.get_content())
    # titles = str(article.sections)
    # open('test.txt', 'w').write(titles)

    print([section for section in article.sections])