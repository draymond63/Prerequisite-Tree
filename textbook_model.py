import re
from typing import List

from page_retrieval import PageRetriever
from article_model import Article

class Textbook:
    def __init__(self, title: str) -> None:
        self.title = title
        self._page_retriever = PageRetriever()
        self.chapters = self.get_chapters()

    def get_chapters(self) -> Article:
        article_title = self.title
        page_list = self._page_retriever.get_article_text(article_title)
        assert page_list, f'All_pages route does not exist for {self.title}'
        page_list = Article(article_title, page_list)
        for section in page_list.sections:
            section.content = '\n'.join(self.get_links(section.content))
        return page_list

    def get_links(self, text: str) -> List[str]:
        # return re.findall(r'\[\[([^\]]+)\]\]', text)
        return [link for link in re.findall(r'\[\[([^\]|]+)|\]\]', text) if link]


if __name__ == '__main__':
    title = 'Control_Systems'
    textbook = Textbook(title)
    # print([page.header for page in textbook.pages.sections])