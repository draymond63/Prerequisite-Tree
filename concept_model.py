import logging
from logging import getLogger
from babelnet import BabelSynset
from babelnet.resources import BabelSynsetID, WikipediaID
from dataclasses import dataclass
from typing import Set, Dict, List

from synset_retriever import SynsetRetriever, id_to_name, get_synset, search_synsets
from wiki_clickthrough_map import WikiMap


@dataclass
class Definition:
	gloss: str
	prereqs: Set[BabelSynsetID]

	def __str__(self) -> str:
		ret = f'{self.gloss}\n'
		ret += '\tPrerequisites:\n'
		for babel_id in self.prereqs:
			ret += f'\t{id_to_name(babel_id)} ({babel_id})\n'
		return ret

	def __repr__(self) -> str:
		return f'Definition: {self.gloss}'


@dataclass
class Concept:
	name: str
	babel_id: BabelSynsetID
	# TODO: Include WikipediaID?
	topic_set: Set[BabelSynsetID]
	definitions: List[Definition]

	@property
	def glosses(self):
		for definition in self.definitions:
			yield definition.gloss

	def __str__(self):
		ret = f'Concept: {self.name} ({self.babel_id})\n'
		ret += 'Topic Set:\n'
		for babel_id in self.topic_set:
			ret += f'\t{id_to_name(babel_id)} ({babel_id})\n'
		ret += 'Definitions:\n'
		for i, definition in enumerate(self.definitions):
			ret += f'{i + 1}. {definition}\n'
		return ret

	def __repr__(self) -> str:
		return f'Concept: {self.name}'


class PrerequisiteMap:
	map: Dict[BabelSynsetID, Concept] # TODO: Switch BabelSynsetID to WikipediaID?

	def __init__(self) -> None:
		self.logger = getLogger(__name__)
		self.map = dict()
		self.babel = SynsetRetriever()
		self.wiki = WikiMap()

	def find_concept(self, name: str, wiki_category: str) -> Concept:
		synsets = self.babel.find_synset_in_category(name, wiki_category)
		if len(synsets) == 0:
			raise Exception(f'No synsets found for {name} in category {wiki_category}')
		if len(synsets) > 1:
			self.logger.warning(f'Multiple synsets found for {name} in category {wiki_category}. Using first. Possible: {synsets}')
		synset = synsets[0]
		return self.get_concept(synset)

	def get_concept(self, synset: BabelSynset) -> Concept:
		if synset.id in self.map:
			return self.map[synset.id]
		name = self.babel.get_name(synset)
		definitions = self._generate_definitions(synset)
		topic_set = self._generate_topic_set(synset)
		concept = Concept(name, synset.id, topic_set, definitions)
		self.map[concept.babel_id] = concept
		# TODO: New concept must ensure DAG
		return concept

	def _generate_definitions(self, synset: BabelSynset) -> List[Definition]:
		definitions = []
		wiki_id = self.babel.get_wiki_id(synset).title
		for gloss in synset.glosses()[:1]: # TODO: Limited to 1 definition for testing
			prereqs = self._generate_prereqs(wiki_id, gloss.gloss)
			prereqs.discard(synset.id)
			definitions.append(Definition(gloss.gloss, prereqs))
		return definitions

	def _generate_prereqs(self, wiki_id: str, definition: str) -> Set[BabelSynsetID]:
		# TODO: Extract main phrase of sentence
		self.logger.info(f"Generating prereqs for definition of {wiki_id}: {definition}")
		prereqs = set()
		ct_links = self.wiki.get_clickthrough_names(wiki_id) # TODO: Pass as an argument?
		for link_id, link_name in ct_links.items():
			self.logger.debug(f"Searching for concept: {link_name} in definition")
			if link_name.lower() in definition.lower():
				self.logger.info(f"Prerequisite found: '{link_name}'")
				synset = get_synset(WikipediaID(link_id, self.babel.lang))
				if synset is None:
					self.logger.warning(f"Synset not found for {link_name}")
				else:
					prereqs.add(synset.id)
		return prereqs

	def _generate_topic_set(self, synset: BabelSynset, score_threshold = 0.02, max_count = 10) -> Set[BabelSynsetID]:
		"""Uses Wikipedia's clickthrough articles, normalized w/ a score threshold"""
		wiki_id = self.babel.get_wiki_id(synset).title
		ct_rates = self.wiki.get_clickthrough_rates(wiki_id, normalized=True)
		ct_rates = ct_rates[ct_rates > score_threshold]
		ct_rates = ct_rates.sort_values(ascending=False)[:max_count]
		self.logger.debug(f'Clickthrough rates: {ct_rates.head(max_count)}')
		synsets = [get_synset(WikipediaID(link_id, self.babel.lang)) for link_id in ct_rates.index]
		for synset in synsets:
			if synset is not None:
				self.logger.debug(f'Topic concept: {synset.main_sense().full_lemma}')
		ids = set(synset.id for synset in synsets if synset is not None)
		ids.discard(synset.id)
		return ids

	# TODO: Move to an interface?
	def print_all_prereqs(self, concept: Concept):
		print(f'Prerequisites for {concept.name}:')
		for i, definition in enumerate(concept.definitions, 1):
			print(f'{i}. {definition}')
			for babel_id in definition.prereqs:
				do_learn = input(f'Learn about {id_to_name(babel_id)}? (y/n): ')
				if do_learn == 'y':
					self.print_all_prereqs(self.get_concept(get_synset(babel_id)))
			if i < len(concept.definitions):
				keep_going = input(f"Continue to next definition of {concept.name} ({i}/{len(concept.definitions)})? (y/n): ")
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
	for handler in logging.root.handlers[:]:
		logging.root.removeHandler(handler)
	logging.basicConfig(filename='datasets/generated/latest.log', filemode='w', level=logging.DEBUG)
	map = PrerequisiteMap()
	concept = map.get_concept(search_synsets('Fresnel diffraction')[0])
	print(concept)
	map.print_all_prereqs(concept)
