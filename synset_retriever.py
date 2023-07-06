import logging
import babelnet as bn
from joblib import Memory
from logging import getLogger
from babelnet.sense import BabelSense
from babelnet import BabelSynset, Language
from babelnet.resources import ResourceID, WikipediaID
from babelnet.data.source import BabelSenseSource
from typing import List, Optional

from category_map import CategoryMap

memory = Memory("datasets/cache")

@memory.cache(verbose=0)
def get_synset(babel_id: ResourceID) -> BabelSynset:
	logging.info(f"Getting synset for '{babel_id}'...")
	return bn.get_synset(babel_id)

def id_to_name(babel_id: ResourceID, lang=Language.EN) -> str:
	synset = get_synset(babel_id)
	return synset.main_sense(lang).full_lemma

def _is_invalid_concept(synset: BabelSynset) -> bool:
	return synset.type != 'CONCEPT' or not len(synset.senses(source=BabelSenseSource.WIKI))

@memory.cache(verbose=0)
def search_synsets(name: str, lang=Language.EN) -> List[BabelSynset]:
	if name == '':
		raise ValueError("Cannot search for empty string")
	logging.info(f"Searching synsets for '{name}'...")
	return bn.get_synsets(name, from_langs={lang}, sources=[BabelSenseSource.WIKI], synset_filters=(_is_invalid_concept,))


class NoSearchResultsError(ValueError):
    """No search results found"""

class CommonWordError(ValueError):
	"""Search term is a common word"""

class SynsetRetriever():
	def __init__(self, language=Language.EN) -> None:
		self.logger = getLogger(__name__)
		self.lang = language
		self.category_map = CategoryMap()

	# TODO: No longer used it seems
	def find_synset_like(self, name: str, categories: List[str]) -> BabelSynset:
		self.logger.info(f"Finding synset like '{name}' with categories {categories}")
		synsets = search_synsets(name, self.lang)
		if len(synsets) == 0:
			raise NoSearchResultsError(f"No synsets found for '{name}'")
		best_synset = None
		best_commonality = 0
		self.logger.debug(f"Found {len(synsets)} synsets for '{name}'")
		for candidate in synsets:
			candidate_categories = self.get_categories(candidate)
			if len(candidate_categories) == 0:
				self.logger.warning(f"Synset '{self.get_name(candidate)}' has no categories")
				continue
			self.logger.debug(f"Getting categorical commonality for '{self.get_name(candidate)}' ({candidate.id})")
			commonality = self.category_map.categorical_commonality(candidate_categories, categories)
			if commonality > best_commonality:
				best_synset = candidate
				best_commonality = commonality
			if best_commonality == 1: # Perfect match, no need to continue
				break
		if best_synset is None:
			raise ValueError(f"No synsets found for '{name}' with categories {categories}.\nCandidates: {synsets}")
		# TODO: Set minimum commonality threshold
		self.logger.debug(f"Found synset '{self.get_name(best_synset)}' ({best_synset.id}) with categories "
		                  f"{self.get_categories(best_synset)} (score = {best_commonality:.2f})")
		return best_synset

	def get_categories(self, synset: BabelSynset) -> List[str]:
		return [category.value for category in synset.categories(self.lang) if category.value in self.category_map.categories]

	def get_name(self, synset: BabelSynset) -> str:
		return self.get_wiki_sense(synset).full_lemma

	def get_wiki_sense(self, synset: BabelSynset) -> BabelSense:
		return synset.senses(language=self.lang, source=BabelSenseSource.WIKI)[0]
	
	def get_wiki_id(self, synset: BabelSynset) -> WikipediaID:
		return WikipediaID(self.get_wiki_sense(synset).full_lemma.lower(), self.lang)

	# TODO: Remove? Could be replaced by find_synset_like
	def find_synset_in_category(self, name: str, wiki_category: str) -> List[BabelSynset]:
		synsets = search_synsets(name, self.lang)
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
				path = self.category_map.category_path(category_str, parent_category)
				if path is not None:
					possible_paths.append([category_str, *path])
		if len(possible_paths):
			return min(possible_paths, key=len)
