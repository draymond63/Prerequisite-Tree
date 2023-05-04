import numpy as np
import pandas as pd
from typing import Set, Iterable, Dict, Mapping, Tuple
from tqdm import tqdm

def get_child_tree(df: pd.DataFrame) -> Dict[str, set]:
    parents = df.groupby('category')['item'].apply(set)
    leafs = set(df['item'].unique()) - set(parents.keys())
    leafs = pd.Series(index=leafs).fillna("").apply(set)
    parents = pd.concat([parents, leafs])
    return parents.to_dict()

def get_parent_tree(df: pd.DataFrame) -> Dict[str, set]:
    return df.groupby('item')['category'].apply(set).to_dict()

def get_category_depth(children: Dict[str, set], root = 'Contents') -> Dict[str, int]:
    depths = {category: None for category in children.keys()}
    depths[root] = 0
    pbar = tqdm(total=len(children))
    pbar.update()
    set_depth(children, depths, 'Contents', pbar=pbar)
    return depths

def set_depth(categories: dict, depths: dict, parent: str, depth: int = 1, pbar = None) -> None:
    for child in categories[parent]:
        if should_set_depth(depths, child, depth):
            if pbar: pbar.update()
            depths[child] = depth
    for child in categories[parent]:
        for grandchild in categories[child]:
            if should_set_depth(depths, grandchild, depth + 1):
                set_depth(categories, depths, child, depth + 1, pbar)
                break

def should_set_depth(depths: dict, item: str, depth: int) -> bool:
    return depths[item] is None or depths[item] > depth + 1

# Removes connections that make the graph acyclic
def make_graph_acyclic(df: pd.DataFrame, depths: Mapping[str, int]) -> pd.DataFrame: # <1 minute
    parent_depths = df['category'].map(depths)
    child_depths = df['item'].map(depths)
    distances = child_depths - parent_depths
    return df[distances == 1]

def remove_hidden_categories(df: pd.DataFrame) -> pd.DataFrame:
    hidden_categories = df[df['category'] == 'Hidden_categories']['item']
    return df[~(df['item'].isin(hidden_categories) & df['category'].isin(hidden_categories))]

# 7978906 -> 3336726 entries
def generate_acyclic_hierarchy(path = 'datasets/raw/enwiki-categories.tsv') -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(path, sep='\t')
    df.columns = ['item', 'category', 'relation']
    df = df.filter(items=['item', 'category'], axis=1)
    df = remove_hidden_categories(df) # Removes ~181629 unhelpful categories
    print("Generating children tree")
    relations = get_child_tree(df) # ~30 seconds
    print("Calculating category depth") # ~37 minutes
    depths = get_category_depth(relations)
    print("Making graph acyclic")
    df = make_graph_acyclic(df, depths)
    return df, depths

def get_all_children(relations: dict, top_level_category: str):
    pbar = tqdm(total=len(relations))
    visited_categories = set()
    def _get_all_children(category: str, depth = 0) -> Set[str]:
        if category in visited_categories:
            return set()
        visited_categories.add(category)
        if pbar: pbar.update(1)
        children = relations[category]
        all_children = {category}
        for child in children:
            all_children.update(_get_all_children(child, depth + 1))
        return all_children
    return _get_all_children(top_level_category)

def get_valid_relations(df: pd.DataFrame, top_levels: Iterable[str] = {'Branches_of_science', 'Engineering_disciplines', 'Fields_of_mathematics', 'Subfields_of_economics'}) -> pd.DataFrame:
    categories = get_child_tree(df)
    viable_topics = set()
    viable_topics.update(top_levels)
    for top_level in top_levels:
        viable_topics.update(get_all_children(categories, top_level))
    viable_df = df[df['category'].isin(viable_topics) & df['item'].isin(viable_topics)]
    return viable_df

def get_mentioned_categories(df: pd.DataFrame) -> Set[str]:
    return set(df['category'].unique()).union(set(df['item'].unique()))

if __name__ == '__main__':
    df = pd.read_csv('datasets/generated/category_hierarchy.tsv', sep='\t')
    relations = get_child_tree(df)
    depths = get_category_depth(relations)
    print(depths.head())
    # generate_acyclic_hierarchy()    

