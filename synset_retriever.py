import babelnet as bn
from joblib import Memory
from babelnet import BabelSynset, Language
from babelnet.resources import BabelSynsetID
from typing import List, Optional

from category_map import CategoryMap

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

class NoSearchResultsError(ValueError):
    pass

class SynsetRetriever():
	def __init__(self, language=Language.EN) -> None:
		self.lang = language
		self.category_map = CategoryMap()

	def find_synset_like(self, name: str, categories: List[str]) -> BabelSynset:
		print("Finding synset like", name, "with categories", categories)
		synsets = search_synsets(name)
		if len(synsets) == 0:
			raise NoSearchResultsError(f"No synsets found for '{name}'")
		best_synset = None
		best_commonality = 0
		for candidate in synsets:
			candidate_categories = self.get_categories(candidate)
			commonality = self.category_map.categorical_commonality(candidate_categories, categories)
			if commonality > best_commonality:
				best_synset = candidate
				best_commonality = commonality
		if best_synset is None:
			raise ValueError(f"No synsets found for '{name}' with categories {categories}.\nCandidates: {synsets}")
		return best_synset
	
	@staticmethod
	def get_categories(synset: BabelSynset) -> List[str]:
		return [category.value for category in synset.categories(Language.EN)]
	
	# TODO: Remove? Could be replaced by find_synset_like
	def find_synset_in_category(self, name: str, wiki_category: str) -> List[BabelSynset]:
		synsets = search_synsets(name)
		if len(synsets) == 0:
			return []
		paths = [self.synset_category_path(synset, wiki_category) for synset in synsets]
		distances = {i: len(path) for i, path in enumerate(paths) if path is not None}
		if len(distances) == 0:
			return []
		best_distance = min(distances.values())
		best_synsets = [synsets[i] for i, dist in distances.items() if dist == best_distance]
		return best_synsets

	def synset_category_path(self, synset: BabelSynset, parent_category: str) -> Optional[List[str]]:
		possible_paths = []
		for category in synset.categories(self.lang):
			category_str = category.value
			if category_str in self.category_map.categories:
				path = self.category_map.parent_category_path(category_str, parent_category)
				if path is not None:
					possible_paths.append([category_str, *path])
		if len(possible_paths):
			return min(possible_paths, key=len)
