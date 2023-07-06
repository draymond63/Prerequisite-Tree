import unicodedata
import pandas as pd
from joblib import Memory

memory = Memory("datasets/cache")

@memory.cache(verbose=0)
def _get_ct_links(path = 'datasets/raw/clickstream-enwiki-2023-05.tsv') -> pd.DataFrame:
    print("Getting clickthrough links...")
    df = pd.read_csv(path, sep='\t', names=('from', 'to', 'type', 'n'))
    df = df[df['type'] == 'link'] # TODO: Should external counts be included for normalization?
    df = df.filter(items=['from', 'to', 'n'])
    df['from'] = df['from'].str.lower()
    df['to'] = df['to'].str.lower()
    print("CT link dataset:", df.shape, df.columns)
    print(df.head())
    return df


class WikiMap:
    def __init__(self) -> None:
        self.ct_links = _get_ct_links()
        # TODO: Add link->name dataset

    def get_clickthrough_names(self, wiki_id: str) -> pd.Series:
        links = self.ct_links[self.ct_links['from'] == wiki_id]['to']
        if len(links) == 0:
            raise ValueError(f'Article not found: {wiki_id}')
        names = links.apply(self._clean_text).set_axis(links)
        return names

    @staticmethod
    def _clean_text(text: str) -> str:
        cleaned_text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
        cleaned_text = cleaned_text.replace('_',' ').lower()
        return cleaned_text

    def get_clickthrough_rates(self, wiki_id: str, normalized = False) -> pd.Series:
        ctr = self.ct_links[self.ct_links['from'] == wiki_id].set_index('to')['n']
        if len(ctr) == 0:
            raise ValueError(f'Article not found: {wiki_id}')
        if normalized:
            ctr = ctr / ctr.sum()
        return ctr


if __name__ == '__main__':
    m = WikiMap()
    print(m.get_clickthrough_names('Control_theory').head(10))
    ctr = m.get_clickthrough_rates('Control_theory', normalized=True)
    print(sorted(ctr.items(), key=lambda x: x[1], reverse=True))
