import spacy
import babelnet as bn
from joblib import Memory
from babelnet import BabelSynset, Language
from babelnet.resources import WikipediaID, BabelSynsetID
from typing import Set, Dict, List

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

	def __init__(self) -> None:
		self.map = dict()
		self.lang = Language.EN

	def find_concept(self, name: str, wiki_category = None) -> 'Concept':
		synset = self.find_synset(name, wiki_category)
		return self.get_concept(synset)

	@memory.cache
	def find_synset(self, name: str, wiki_category = None) -> BabelSynset:
		print('Running find_synset')
		if wiki_category is None:
			return bn.get_synset(WikipediaID(name, language=self.lang))
		synsets = bn.get_synsets(name, from_langs={self.lang})
		print(synsets)
		for synset in synsets:
			print(synset.categories(self.lang))
			# TODO: Find the best synset based on the proximity of the given category to the synset's

	def get_concept(self, synset: BabelSynset) -> 'Concept':
		name = synset.main_sense().lemma # TODO: Wrong
		if synset.id in self.map:
			return self.map[synset.id]
		definitions = [Definition(gloss.gloss, self._generate_prereqs(gloss.gloss)) for gloss in synset.glosses()]
		topic_set = self._generate_topic_set(synset)
		concept = Concept(name, topic_set, definitions)
		self.map[concept.wikiID] = concept
		return concept

	def _generate_prereqs(self, definition: str) -> 'Set[BabelSynsetID]':
		# TODO: Extract main phrase of sentence
		# TODO: For each noun chunk, find all possible synsets
		# TODO: Determine best synset for each noun chunk based on categorical similarity to original synset
		parsed = self.model(definition)
		for noun in parsed.noun_chunks:
			cleaned_noun = self.clean_noun(noun.text)
			# TODO: Get the synset for the noun
			print(f'"{cleaned_noun}"', noun.root.dep_, noun.root.head.text)

	# TODO: Find spacy way of dropping stop words
	def clean_noun(self, text: str) -> str:
		words = text.split(' ')
		words = [word for word in words if word not in self.model.Defaults.stop_words]
		return ' '.join(words)

	# TODO: Generate topic set based on relations, not glosses
	def _generate_topic_set(self, synset: BabelSynset) -> 'Set[BabelSynsetID]':
		topic_set = set()
		for gloss in synset.glosses():
			for token in gloss.token_ids:
				topic_set.add(token.id)
		return topic_set

	# TODO: get_prerequiste_relations no longer exists
	def save(self, path: str) -> None:
		with open(path, 'w') as f:
			for concept in self.map.values():
				for prereq in concept.get_prerequiste_relations():
					f.write(f'{concept.name}\t{prereq}\n')


if __name__ == '__main__':
	# BabelSynsetID('bn:03566112n')
	PrerequisiteMap().find_concept('Control Theory', 'Mathematics')