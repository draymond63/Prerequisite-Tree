import spacy
from babelnet import BabelSynset
from babelnet.resources import BabelSynsetID
from babelnet.data.relation import BabelPointer
from typing import Set, Dict, List, Optional

from synset_retriever import SynsetRetriever


class Definition:
	def __init__(self, gloss: str, prereqs: Set[BabelSynsetID]) -> None:
		self.gloss = gloss
		self.prereqs = prereqs

	def __repr__(self) -> str:
		return f'Definition: {self.gloss}'

class Concept:
	def __init__(self, name: str, babel_id: BabelSynsetID, topic_set: Set[BabelSynsetID], definitions: List[Definition]) -> None:
		self.name = name
		self.babel_id = babel_id
		self.topic_set = topic_set
		self.definitions = definitions

	@property
	def glosses(self):
		for definition in self.definitions:
			yield definition.gloss

	def __str__(self):
		ret = f'Concept: {self.name}\n'
		ret += 'Topic Set:\n'
		ret += '\n'.join([f'\t{topic}' for topic in self.topic_set]) # TODO: Needs concept name, not ID
		ret += '\nDefinitions:'
		for i, definition in enumerate(self.definitions):
			ret += f'\n{i + 1}. {definition.gloss}\n'
			ret += '\n'.join([f'\t{prereq}' for prereq in definition.prereqs]) # TODO: Needs concept name, not ID
		return ret

	def __repr__(self) -> str:
		return f'Concept: {self.name}'


class PrerequisiteMap:
	model = spacy.load('en_core_web_sm')
	map: Dict[BabelSynsetID, Concept]
	search: SynsetRetriever

	def __init__(self) -> None:
		self.map = dict()
		self.search = SynsetRetriever()

	def find_concept(self, name: str, wiki_category = None) -> Concept:
		synset = self.search.find_synset_wiki(name, wiki_category)
		return self.get_concept(synset, wiki_category)

	def get_concept(self, synset: BabelSynset, wiki_category = None) -> Concept:
		if synset.id in self.map:
			return self.map[synset.id]
		name = synset.main_sense().lemma # TODO: Wrong
		category = wiki_category if wiki_category else synset.categories[0].name # TODO: Better default category selection
		definitions = self._generate_definitions(synset, category)
		topic_set = self._generate_topic_set(synset)
		concept = Concept(name, synset.id, topic_set, definitions)
		self.map[concept.babel_id] = concept
		return concept

	def _generate_definitions(self, synset: BabelSynset, category: str) -> List[Definition]:
		definitions = []
		for gloss in synset.glosses()[:1]:
			prereqs = self._generate_prereqs(gloss.gloss, category)
			prereqs -= set([synset.id])
			definitions.append(Definition(gloss.gloss, prereqs))
		return definitions

	def _generate_prereqs(self, definition: str, wiki_category: Optional[str] = None) -> Set[BabelSynsetID]:
		# TODO: Extract main phrase of sentence
		# TODO: For each noun chunk, find all possible synsets
		# TODO: Determine best synset for each noun chunk based on categorical similarity to original synset
		parsed = self.model(definition)
		prereqs = set()
		print("Generating prereqs for definition:", definition)
		for noun in parsed.noun_chunks:
			cleaned_noun = self.clean_noun(noun.text)
			print(f"Searching for prerequisite synset '{cleaned_noun}'")
			try:
				synset_candidate = self.search.find_synset_wiki(cleaned_noun, wiki_category)
			except LookupError as e:
				print(f"{e}. Ignoring wiki category {wiki_category}")
				synset_candidate = self.search.find_synset_wiki(cleaned_noun)
			# TODO: Wasteful to just use the id
			if synset_candidate is not None:
				print(f"Prerequisite found: '{synset_candidate.main_sense().lemma}'")
				prereqs.add(synset_candidate.id)
		return prereqs

	# TODO: Find spacy way of dropping stop words
	# TODO: Lemmatize?
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

	# TODO: Save map to a standard format
	def save(self, path: str) -> None:
		with open(path, 'w') as f:
			for concept in self.map.values():
				...


if __name__ == '__main__':
	map = PrerequisiteMap()
	concept = map.find_concept('Control Theory', 'Mathematics')
	print(concept)
