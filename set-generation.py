import pandas as pd
from typing import Optional

# * Categories
# ['Assistant', 'Book', 'Department', 'Documentation_pages_made_with_Template', 'Fukushima_Aftermath', 'Shelf', 
# 'Solutions_To_Computer_Engineering_Textbooks/Computer_Organization_and_Design', 'Subject', 'User', 'Users', 'Wikibooks']

namespaces = {
    0: 'Article', # Important: This is the default namespace
    1: 'Talk',
    2: 'User',
    3: 'User talk',
    4: 'Wikipedia',
    5: 'Wikipedia talk',
    6: 'File',
    7: 'File talk',
    8: 'MediaWiki',
    9: 'MediaWiki talk',
    10: 'Template',
    11: 'Template talk',
    12: 'Help',
    13: 'Help talk',
    14: 'Category', # Important: Contains shelfs and books
    15: 'Category talk',
    100: 'Portal',
    101: 'Portal talk',
    118: 'Draft',
    119: 'Draft talk',
    710: 'TimedText',
    711: 'TimedText talk',
    828: 'Module',
    829: 'Module talk',
}

def split_category(pages: pd.Series) -> pd.DataFrame:
    df = pages.str.split(':', n=1, expand=True)
    df.dropna(inplace=True)
    df.columns = ['category', 'title']
    df = pd.concat([df['category'], pages], axis='columns')
    return df

# TODO: Switch to regex filtering
def drop_redundant(pages: pd.Series) -> pd.Series:
    def keep_page(page: str) -> bool:
        return not 'all_books' in page
    return pages[pages.apply(keep_page)]

def get_category(pages: pd.Series, category: str) -> pd.Series:
    filtered_pages = drop_redundant(pages)
    df = split_category(filtered_pages)
    return df[df['category'] == category]['page_title']

# def drop_structural_articles(articles: pd.Series, sets: pd.Series) -> pd.Series:
#     article_set = set(articles.unique())
#     droppables = set(sets.unique())
#     return pd.Series(article_set - droppables)

def generate_sets(source_path: str, save_dir='./datasets'):
    df = pd.read_csv(source_path, sep='\t')
    df['page_namespace'] = df['page_namespace'].map(namespaces)
    df.dropna(inplace=True)
    articles = df[df['page_namespace'] == 'Article']['page_title']
    categories = df[df['page_namespace'] == 'Category']['page_title']
    books = get_category(categories, 'Book')
    shelfs = get_category(categories, 'Shelf') # TODO: Determine difference between <shelf> & <shelf>/all_books
    departments = get_category(categories, 'Department') # TODO: Determine difference between <dep> & <dep>/all_books
    # TODO: Split page path on '/' ?
    articles.to_csv(f'{save_dir}/articles.tsv', sep='\t', index=False)
    books.to_csv(f'{save_dir}/books.tsv', sep='\t', index=False)
    shelfs.to_csv(f'{save_dir}/shelfs.tsv', sep='\t', index=False)
    departments.to_csv(f'{save_dir}/departments.tsv', sep='\t', index=False)

if __name__ == "__main__":
    generate_sets('datasets/raw/enwikibooks-20230401-all-titles.tsv')
