import pandas as pd
from typing import Set, Optional, Iterable
from tqdm import tqdm
from copy import deepcopy

def get_category_tree(df: pd.DataFrame, add_depth = False) -> dict:
    categories = {}
    default_value = {'children': set(), 'depth': None} if add_depth else set()
    print("Building category tree") # ~8 minutes
    for index, row in tqdm(df.iterrows(), total=len(df)):
        parent = categories.setdefault(row['category'], deepcopy(default_value))
        categories.setdefault(row['item'], deepcopy(default_value))
        if add_depth:
            parent['children'].add(row['item'])
        else:
            parent.add(row['item'])
    return categories

def get_category_depth(df: pd.DataFrame) -> dict:
    categories = get_category_tree(df, add_depth=True)
    print("Calculating category depth") # ~37 minutes
    categories['Contents']['depth'] = 0
    pbar = tqdm(total=len(categories))
    pbar.update()
    set_depth(categories, 'Contents', pbar=pbar)
    depths = {category: info['depth'] for category, info in categories.items()}
    return depths

def set_depth(categories: dict, parent: str, depth: int = 1, pbar = None) -> None:
    for child in categories[parent]['children']:
        if should_set_depth(categories, child, depth):
            if pbar: pbar.update(1)
            categories[child]['depth'] = depth
    for child in categories[parent]['children']:
        for grandchild in categories[child]['children']:
            if should_set_depth(categories, grandchild, depth + 1):
                set_depth(categories, child, depth + 1, pbar)
                break

def should_set_depth(categories: dict, item: str, depth: int) -> bool:
    return categories[item]['depth'] is None or categories[item]['depth'] > depth + 1

# Removes connections that make the graph acyclic
def make_graph_acyclic(df: pd.DataFrame, depths: dict) -> pd.DataFrame: # <1 minute
    parent_depths = df['category'].map(depths)
    child_depths = df['item'].map(depths)
    distances = child_depths - parent_depths
    return df[distances == 1]

def remove_hidden_categories(df: pd.DataFrame) -> pd.DataFrame:
    hidden_categories = df[df['category'] == 'Hidden_categories']['item']
    return df[~(df['item'].isin(hidden_categories) & df['category'].isin(hidden_categories))]

# 7978906 -> 3336726 entries
def generate_acyclic_hierarchy(path = 'datasets/raw/enwiki-categories.tsv') -> pd.DataFrame:
    df = pd.read_csv(path, sep='\t')
    df.columns = ['item', 'category', 'relation']
    df = df.filter(items=['item', 'category'], axis=1)
    df = remove_hidden_categories(df) # Removes ~181629 unhelpful categories
    depths = get_category_depth(df)
    depths_df = pd.DataFrame.from_dict(depths, orient='index')
    depths_df.to_csv('datasets/generated/category_depths.tsv', sep='\t', index=True, header=False)
    print("Making graph acyclic")
    df = make_graph_acyclic(df, depths)
    return df

def get_all_children(relations: dict, top_level_category: str):
    pbar = tqdm()
    visited_categories = set()
    def _get_all_children(top_level_category: str, depth = 0) -> Set[str]:
        if top_level_category in visited_categories:
            return set()
        visited_categories.add(top_level_category)
        if pbar: pbar.update(1)
        children = relations[top_level_category]
        all_children = {top_level_category}
        for child in children:
            all_children.update(_get_all_children(child, depth + 1))
        return all_children
    return _get_all_children(relations, top_level_category)

def get_valid_relations(df: pd.DataFrame, top_levels: Iterable[str] = {'Branches_of_science', 'Engineering_disciplines', 'Fields_of_mathematics', 'Subfields_of_economics'}) -> pd.DataFrame:
    categories = get_category_tree(df)
    viable_topics = set()
    viable_topics.update(top_levels)
    for top_level in top_levels:
        viable_topics.update(get_all_children(categories, top_level))
    viable_df = df[df['category'].isin(viable_topics) & df['item'].isin(viable_topics)]
    return viable_df

if __name__ == '__main__':
    df = pd.read_csv('datasets/generated/valid_categories.tsv', sep='\t')
    categories = set(df['category'].unique()) | set(df['item'].unique())
    with open('datasets/generated/valid_categories.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(categories))
