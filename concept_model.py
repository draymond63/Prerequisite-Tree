import spacy
import pandas as pd
import babelnet as bn
from joblib import Memory
from babelnet import BabelSynset, Language
from babelnet.resources import WikipediaID, BabelSynsetID
from babelnet.data.relation import BabelPointer
from typing import Set, Dict, List, Optional

from topic_hierarchy import get_parent_tree

class Definition:
	def __init__(self, gloss: str, prereqs: Set[BabelSynsetID]) -> None:
		self.gloss = gloss
		self.prereqs = prereqs

	def __repr__(self) -> str:
		return f'Definition: {self.gloss}'

class Concept:
	def __init__(self, name: str, topic_set: Set[BabelSynsetID], definitions: List[Definition]) -> None:
		self.name = name
		self.topic_set = topic_set
		self.definitions = definitions

	@property
	def glosses(self):
		for definition in self.definitions:
			yield definition.gloss

	def __repr__(self) -> str:
		return f'Concept: {self.name}'

class PrerequisiteMap:
	memory = Memory("datasets/cache")
	model = spacy.load('en_core_web_sm')
	map: 'Dict[BabelSynsetID, Concept]'
	category_tree: Dict[str, Set[str]]

	def __init__(self) -> None:
		self.map = dict()
		self.lang = Language.EN
		self.category_tree = self.init_categories()

	@staticmethod
	@memory.cache
	def init_categories():
		categorylinks = pd.read_csv('datasets/generated/valid_category_links.tsv', sep='\t')
		return get_parent_tree(categorylinks)

	def find_concept(self, name: str, wiki_category = None) -> 'Concept':
		synset = self.find_synset_wiki(name, wiki_category)
		return self.get_concept(synset)
	
	@staticmethod
	def _is_invalid_concept(synset: BabelSynset) -> bool:
		# TODO: Ensure sysnet is_key_concept
		return synset.type != 'CONCEPT'

	def find_synset_wiki(self, name: str, wiki_category = None) -> BabelSynset:
		if wiki_category is None:
			return bn.get_synset(WikipediaID(name, language=self.lang)) # TODO: Name is not an ID
		synsets = bn.get_synsets(name, from_langs={self.lang}, synset_filters={self._is_invalid_concept})
		if len(synsets) == 0:
			raise LookupError(f'No synsets found for {name}')
		distances = [self.distance_to_category(synset, wiki_category) for synset in synsets]
		distances = {i: dist for i, dist in enumerate(distances) if dist is not None}
		if len(distances) == 0:
			raise LookupError(f'No synsets found like {name} in category {wiki_category}')
		best_index = min(distances, key=distances.get)
		return synsets[best_index]

	@memory.cache
	def get_synset(self, babel_id: BabelSynsetID) -> BabelSynset:
		return bn.get_synset(babel_id, to_langs={self.lang})

	def get_concept(self, synset: BabelSynset) -> 'Concept':
		name = synset.main_sense().lemma # TODO: Wrong
		if synset.id in self.map:
			return self.map[synset.id]
		category = synset.categories[0].name # TODO: Better principle category selection
		definitions = [Definition(gloss.gloss, self._generate_prereqs(gloss.gloss, category)) for gloss in synset.glosses()]
		topic_set = self._generate_topic_set(synset)
		concept = Concept(name, topic_set, definitions)
		self.map[concept.wikiID] = concept
		return concept

	def _generate_prereqs(self, definition: str, wiki_category: Optional[str] = None) -> Set[BabelSynsetID]:
		# TODO: Extract main phrase of sentence
		# TODO: For each noun chunk, find all possible synsets
		# TODO: Determine best synset for each noun chunk based on categorical similarity to original synset
		parsed = self.model(definition)
		prereqs = set()
		for noun in parsed.noun_chunks:
			cleaned_noun = self.clean_noun(noun.text)
			try:
				synset_candidate = self.find_synset_wiki(cleaned_noun, wiki_category)
			except LookupError:
				synset_candidate = self.find_find_synset_wiki(cleaned_noun)
			# TODO: Wasteful to just use the id
			prereqs.add(synset_candidate.id)
		return prereqs

	# TODO: Find spacy way of dropping stop words
	def clean_noun(self, text: str) -> str:
		words = text.split(' ')
		words = [word for word in words if word not in self.model.Defaults.stop_words]
		return ' '.join(words)

	@staticmethod
	def _generate_topic_set(synset: BabelSynset) -> 'Set[BabelSynsetID]':
		# TODO: Switch to WIKI only relations? Are these the correct relations?
		relations = synset.outgoing_edges(BabelPointer.ANY_HOLONYM)
		relations += synset.outgoing_edges(BabelPointer.ANY_HYPONYM)
		relations += synset.outgoing_edges(BabelPointer.TOPIC)
		return {relation.id_target for relation in relations}

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

	def distance_to_category(self, synset: BabelSynset, parent_category: str):
		distances = []
		for category in synset.categories(self.lang):
			if category.value in self.category_tree:
				path = self.parent_category_path(category.value, parent_category)
				if path is not None:
					distances.append(len(path))
		if len(distances):
			return min(distances)

	# TODO: get_prerequiste_relations no longer exists
	def save(self, path: str) -> None:
		with open(path, 'w') as f:
			for concept in self.map.values():
				for prereq in concept.get_prerequiste_relations():
					f.write(f'{concept.name}\t{prereq}\n')


if __name__ == '__main__':
	map = PrerequisiteMap()
	synset = map.get_synset(BabelSynsetID('bn:03566112n'))
	print(synset)
	print(map.get_concept(synset))