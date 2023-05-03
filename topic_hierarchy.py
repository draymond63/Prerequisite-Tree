import pandas as pd
from typing import List
from tqdm import tqdm


def get_category_depth(df: pd.DataFrame) -> dict:
    categories = {}
    print("Building category tree") # ~8 minutes
    for index, row in tqdm(df.iterrows(), total=len(df)):
        parent = categories.setdefault(row['category'], {'children': set(), 'depth': None})
        child = categories.setdefault(row['item'], {'children': set(), 'depth': None})
        parent['children'].add(row['item'])

    print("Calculating category depth") # ~37 minutes
    categories['Contents']['depth'] = 0
    pbar = tqdm(total=len(categories))
    pbar.update(1)
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

visited_categories = set()

def get_child_categories(df: pd.DataFrame, category: str) -> List[str]:
    return df[df['category'] == category]['item'].values.flatten().tolist()

def get_all_children(df: pd.DataFrame, top_level_category: str, depth = 0) -> List[str]:
    if top_level_category in visited_categories:
        print(f'{depth}. {top_level_category} already visited')
        return []
    visited_categories.add(top_level_category)
    children = get_child_categories(df, top_level_category)
    print(f'{depth}. {top_level_category}: {children}')
    all_children = []
    for child in children:
        all_children.append(child)
        all_children.extend(get_all_children(df, child, depth + 1))
    return all_children

if __name__ == '__main__':
    df = pd.read_csv('datasets/generated/category_hierarchy.tsv', sep='\t')
    top_levels = {'Branches_of_science', 'Engineering_disciplines', 'Fields_of_mathematics', 'Subfields_of_economics'}
    # top_levels = {'Tensors', 'Differential_forms'}
    viable_topics = set()
    viable_topics.update(top_levels)
    for top_level in top_levels:
        viable_topics.update(get_all_children(df, top_level))
        viable_df = df[df['category'].isin(viable_topics) & df['item'].isin(viable_topics)]
        viable_df.to_csv('datasets/generated/valid_categories.tsv', sep='\t', index=False)
