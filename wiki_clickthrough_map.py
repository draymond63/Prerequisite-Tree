import unicodedata
import pandas as pd
from typing import List
from babelnet._utils import normalized_lemma_to_string


def _get_ct_links(path = 'datasets/raw/clickstream-enwiki-2023-05.tsv') -> pd.DataFrame:
    df = pd.read_csv(path, sep='\t', names=('source', 'target', 'type', 'n'))
    df = df[df['type'] == 'link']
    df.drop(columns=['type'], inplace=True)
    df['source'] = df['source'].str.lower()
    df['target'] = df['target'].str.lower()
    return df


class WikiMap:
    def __init__(self, path='datasets/raw/clickstream-enwiki-2023-05.tsv') -> None:
        self.ct_links = _get_ct_links(path)

    def get_clickthrough_links(self, wiki_id: str) -> List[str]:
        links = self.ct_links[self.ct_links['source'] == wiki_id]['target']
        if len(links) == 0:
            raise ValueError(f'Article not found: {wiki_id}')
        return links.to_list()

    @staticmethod
    def link_to_title(text: str) -> str:
        cleaned_text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
        cleaned_text = cleaned_text.replace('_',' ')
        return normalized_lemma_to_string(cleaned_text).strip() # Removes parenthesis, makes lowercase

    def get_clickthrough_rates(self, wiki_id: str, target_normalized=False, source_normalized=False) -> pd.Series:
        if source_normalized and target_normalized:
            raise ValueError('Cannot normalize based on both source and target')
        ctr = self.ct_links[self.ct_links['source'] == wiki_id].set_index('target')['n']
        if len(ctr) == 0:
            raise ValueError(f'Article not found: {wiki_id}')
        # Normalize based on source clicks (i.e. portion of source out-traffic going to target)
        # This favours popular links, typically related
        if source_normalized:
            ctr /= ctr.sum()
        # Normalize based on target clicks (i.e. portion of target in-traffic is coming from source)
        # This favours niche links
        if target_normalized:
            ct_link_totals = self.ct_links[self.ct_links['target'].isin(ctr.index)].groupby('target')['n'].sum()
            ctr /= ct_link_totals
        return ctr


if __name__ == '__main__':
    m = WikiMap()
    # print(m.get_clickthrough_links('control_theory')[:5])
    ctr = m.get_clickthrough_rates('control_theory', source_normalized=True)
    print(ctr.sort_values(ascending=False).head(5))
