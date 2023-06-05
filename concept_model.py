import spacy
from babelnet import BabelSynset
from babelnet.resources import BabelSynsetID
from babelnet.data.relation import BabelPointer
from typing import Set, Dict, List, Optional

from synset_retriever import SynsetRetriever, id_to_name, get_synset, NoSearchResultsError


class Definition:
	def __init__(self, gloss: str, prereqs: Set[BabelSynsetID]) -> None:
		self.gloss = gloss
		self.prereqs = prereqs

	def __str__(self) -> str:
		ret = f'{self.gloss}\n'
		ret += '\tPrerequisites:\n'
		for babel_id in self.prereqs:
			ret += f'\t{id_to_name(babel_id)}\n'
		return ret

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
		for babel_id in self.topic_set:
			ret += f'\t{id_to_name(babel_id)}\n'
		ret += 'Definitions:\n'
		for i, definition in enumerate(self.definitions):
			ret += f'{i + 1}. {definition}\n'
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

	def find_concept(self, name: str, wiki_category: str) -> Concept:
		synsets = self.search.find_synset_in_category(name, wiki_category)
		if len(synsets) == 0:
			raise Exception(f'No synsets found for {name} in category {wiki_category}')
		if len(synsets) > 1:
			print(f'Multiple synsets found for {name} in category {wiki_category}. Using first. Possible: {synsets}')
		synset = synsets[0]
		return self.get_concept(synset)

	def get_concept(self, synset: BabelSynset) -> Concept:
		if synset.id in self.map:
			return self.map[synset.id]
		name = synset.main_sense().lemma # TODO: Wrong
		definitions = self._generate_definitions(synset)
		topic_set = self._generate_topic_set(synset)
		concept = Concept(name, synset.id, topic_set, definitions)
		self.map[concept.babel_id] = concept
		# TODO: New concept must ensure DAG
		return concept

	def _generate_definitions(self, synset: BabelSynset) -> List[Definition]:
		definitions = []
		categories = self.search.get_categories(synset)
		for gloss in synset.glosses()[:1]:
			prereqs = self._generate_prereqs(gloss.gloss, categories)
			prereqs -= set([synset.id])
			definitions.append(Definition(gloss.gloss, prereqs))
		return definitions

	def _generate_prereqs(self, definition: str, parent_categories: List[str]) -> Set[BabelSynsetID]:
		# TODO: Extract main phrase of sentence
		# TODO: For each noun chunk, find all possible synsets
		# TODO: Determine best synset for each noun chunk based on categorical similarity to original synset
		parsed = self.model(definition)
		prereqs = set()
		print("Generating prereqs for definition:", definition)
		for noun in parsed.noun_chunks:
			cleaned_noun = self.clean_noun(noun.text)
			if cleaned_noun == '':
				continue
			print(f"Searching for prerequisite synset '{cleaned_noun}'")
			try:
				synset_candidate = self.search.find_synset_like(cleaned_noun, parent_categories)
				print(f"Prerequisite found: '{synset_candidate.main_sense().lemma}'")
				prereqs.add(synset_candidate.id)
			except NoSearchResultsError:
				print(f"No results for {cleaned_noun}. Ignoring")
		return prereqs

	# TODO: Find spacy way of dropping stop words
	# TODO: Lemmatize?
	def clean_noun(self, text: str) -> str:
		words = text.split(' ')
		words = [word for word in words if word not in self.model.Defaults.stop_words]
		return ' '.join(words).lower()

	@staticmethod
	def _generate_topic_set(synset: BabelSynset) -> Set[BabelSynsetID]:
		# TODO: Switch to WIKI only relations? Are these the correct relations?
		relations = synset.outgoing_edges(BabelPointer.ANY_HOLONYM)
		relations += synset.outgoing_edges(BabelPointer.ANY_HYPONYM)
		relations += synset.outgoing_edges(BabelPointer.TOPIC)
		return {relation.id_target for relation in relations}

	# TODO: Move to an interface?
	def print_all_prereqs(self, concept: Concept):
		print(f'Prerequisites for {concept.name}:')
		for i, definition in enumerate(concept.definitions, 1):
			print(f'{i}. {definition}')
			for babel_id in definition.prereqs:
				do_learn = input(f'Learn about {id_to_name(babel_id)}? (y/n): ')
				if do_learn == 'y':
					self.print_all_prereqs(self.get_concept(get_synset(babel_id)))
			keep_going = input(f"Continue to next definition of {concept.name} ({i + 1}/{len(concept.definitions)})? (y/n): ")
			if keep_going != 'y':
				return

	# TODO: Save map to a standard format. Duck DB?
	def save(self, path: str) -> None:
		with open(path, 'w') as f:
			for concept in self.map.values():
				...
				# Table Relations:
					# Definitions: concept_id, gloss_id
					# Prereqs: gloss_id, prereq_id
					# Topic Set: concept_id, child_id
					# Naming (Optional): concept_id, concept_name
					# Definitions: gloss_id, gloss
	

if __name__ == '__main__':
	map = PrerequisiteMap()
	concept = map.find_concept('Control Theory', 'Mathematics')
	print(concept)
	map.print_all_prereqs(concept)
