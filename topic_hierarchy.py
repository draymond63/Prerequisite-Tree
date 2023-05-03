import pandas as pd
from typing import List

visited_categories = set()

def remove_hidden_categories(df: pd.DataFrame) -> pd.DataFrame:
    hidden_categories = df[df['category'] == 'Hidden_categories']['item']
    return df[~(df['item'].isin(hidden_categories) & df['category'].isin(hidden_categories))]

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
    df = pd.read_csv('datasets/raw/enwiki-categories.tsv', sep='\t')
    df.columns = ['item', 'category', 'relation']
    df = df.filter(items=['item', 'category'], axis=1)
    df = remove_hidden_categories(df) # Removes ~181629 unhelpful categories

    top_levels = {'Branches_of_science', 'Engineering_disciplines', 'Fields_of_mathematics', 'Subfields_of_economics'}
    # top_levels = {'Tensors', 'Differential_forms'}
    viable_topics = set()
    viable_topics.update(top_levels)
    for top_level in top_levels:
        viable_topics.update(get_all_children(df, top_level))
        viable_df = df[df['category'].isin(viable_topics) & df['item'].isin(viable_topics)]
        viable_df.to_csv('datasets/generated/valid_categories.tsv', sep='\t', index=False)
