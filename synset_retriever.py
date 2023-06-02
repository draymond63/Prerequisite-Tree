import pandas as pd
import babelnet as bn
from joblib import Memory
from babelnet import BabelSynset, Language
from babelnet.resources import WikipediaID, BabelSynsetID
from typing import List, Optional

from topic_hierarchy import get_parent_tree

memory = Memory("datasets/cache")

def _is_invalid_concept(synset: BabelSynset) -> bool:
	# TODO: Ensure sysnet is_key_concept and is from Wikipedia?
	return synset.type != 'CONCEPT'

@memory.cache
def get_synset(babel_id: BabelSynsetID) -> BabelSynset:
	print(f"Getting synset for '{babel_id}'...")
	return bn.get_synset(babel_id)

def id_to_name(babel_id: BabelSynsetID, lang=Language.EN) -> str:
	synset = get_synset(babel_id)
	return synset.main_sense(lang).full_lemma

@memory.cache
def search_synsets(name: str, lang=Language.EN) -> List[BabelSynset]:
	if name == '':
		raise ValueError("Cannot search for empty string")
	print(f"Searching synsets for '{name}'...")
	return bn.get_synsets(name, from_langs={lang}, synset_filters={_is_invalid_concept})

@memory.cache
def _generate_parent_tree():
	print("Loading category tree...")
	categorylinks = pd.read_csv('datasets/generated/valid_category_links.tsv', sep='\t')
	return get_parent_tree(categorylinks)


class SynsetRetriever():
	def __init__(self, language=Language.EN) -> None:
		self.lang = language
		self.category_tree = _generate_parent_tree()

	def find_synset_wiki(self, name: str, wiki_category = None) -> Optional[BabelSynset]:
		synsets = search_synsets(name)
		if len(synsets) == 0:
			raise LookupError(f"No synsets found for '{name}'")
		if wiki_category is None:
			return synsets[0]
		# TODO: Why are most synsets distance 2 away from 'Mathematics'? What's the path?
		distances = [self.distance_to_category(synset, wiki_category) for synset in synsets]
		distances = {i: dist for i, dist in enumerate(distances) if dist is not None}
		if len(distances) == 0:
			raise LookupError(f"No synsets found like '{name}' in category {wiki_category}")
		best_index = min(distances, key=distances.get) # TODO: Handle ties (e.g. "control")
		return synsets[best_index]

	def distance_to_category(self, synset: BabelSynset, parent_category: str):
		distances = []
		for category in synset.categories(self.lang):
			if category.value in self.category_tree:
				path = self.parent_category_path(category.value, parent_category)
				if path is not None:
					distances.append(len(path))
		if len(distances):
			return min(distances)

	def parent_category_path(self, child: str, parent: str) -> Optional[List[str]]:
		parents = self.category_tree.get(child, [])
		if len(parents) == 0:
			return None
		if parent in parents:
			return [parent]
		for category in parents:
			path = self.parent_category_path(category, parent)
			if path is not None:
				return [category, *path]