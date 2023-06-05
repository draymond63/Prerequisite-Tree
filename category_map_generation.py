import os
import pandas as pd
from tqdm import tqdm
from typing import Set, Dict, Mapping, Tuple

def get_child_tree(df: pd.DataFrame) -> Dict[str, set]:
	parents = df.groupby('category')['item'].apply(set)
	leafs = set(df['item'].unique()) - set(parents.keys())
	leafs = pd.Series(index=leafs).fillna("").apply(set)
	parents = pd.concat([parents, leafs])
	return parents.to_dict()

def get_parent_tree(df: pd.DataFrame) -> Dict[str, set]:
	children = df.groupby('item')['category'].apply(set)
	leafs = set(df['category'].unique()) - set(children.keys())
	leafs = pd.Series(index=leafs).fillna("").apply(set)
	children = pd.concat([children, leafs])
	return children.to_dict()

def get_category_depth(children: Dict[str, set], root = 'Contents') -> Dict[str, int]: # Main_topic_classifications
	depths = {category: None for category in children.keys()}
	depths[root] = 0
	pbar = tqdm(total=len(children))
	pbar.update()
	set_depth(children, depths, root, pbar=pbar)
	return depths

def set_depth(categories: dict, depths: dict, parent: str, depth: int = 1, pbar = None) -> None:
	for child in categories[parent]:
		if depths[child] is None and pbar:
			pbar.update()
		if should_set_depth(depths, child, depth):
			depths[child] = depth
	for child in categories[parent]:
		for grandchild in categories[child]:
			if should_set_depth(depths, grandchild, depth + 2):
				set_depth(categories, depths, child, depth + 1, pbar)
				break

def should_set_depth(depths: dict, item: str, depth: int) -> bool:
	return depths[item] is None or depths[item] > depth

# Removes connections that make the graph acyclic
def make_graph_acyclic(df: pd.DataFrame, depths: Mapping[str, int]) -> pd.DataFrame: # <1 minute
	parent_depths = df['category'].map(depths)
	child_depths = df['item'].map(depths)
	distances = child_depths - parent_depths
	return df[distances == 1]

def remove_hidden_categories(df: pd.DataFrame) -> pd.DataFrame:
	hidden_categories = df[df['category'] == 'Hidden_categories']['item']
	return df[~(df['item'].isin(hidden_categories) & df['category'].isin(hidden_categories))]

def get_raw_relations(path = 'datasets/raw/enwiki-categories.tsv'):
	df = pd.read_csv(path, sep='\t')
	df.columns = ['item', 'category', 'relation']
	df = df.filter(items=['item', 'category'], axis=1)

# 7978906 -> 3336171 entries
def generate_category_map(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
	df = remove_hidden_categories(df) # Removes ~181629 unhelpful categories
	print("Generating children tree...")
	relations = get_child_tree(df) # ~30 seconds
	print("Calculating category depth...")
	depths = get_category_depth(relations) # ~37 minutes
	print("Making graph acyclic...")
	df = make_graph_acyclic(df, depths)
	depths = pd.DataFrame.from_dict(depths, orient='index', columns=['depth'])
	return df, depths


def get_category_map(source_path = 'datasets/raw/enwiki-categories.tsv', 
					 save_path = 'datasets/generated/valid_category_links.tsv', 
					 depths_path = 'datasets/generated/category_depths.tsv'):
	if os.path.exists(save_path) and os.path.exists(depths_path):
		df = pd.read_csv(save_path, sep='\t')
		depths = pd.read_csv(depths_path, sep='\t')
		return df, depths
	print("Generating category map...")
	df = get_raw_relations(source_path)
	df, depths = generate_category_map(df)
	if save_path:
		df.to_csv(save_path, sep='\t', index=False)
	if depths_path:
		depths.to_csv(depths_path, sep='\t')
	return df, depths

if __name__ == '__main__':
	get_category_map()
