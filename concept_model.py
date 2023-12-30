import spacy
import logging
from logging import getLogger
from babelnet import BabelSynset
from babelnet.resources import BabelSynsetID, WikipediaID
from dataclasses import dataclass
from typing import Set, Dict, List

from synset_retriever import SynsetRetriever, id_to_name, get_synset
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
	wiki_id: WikipediaID
	topic_set: Set[BabelSynsetID]
	definitions: List[Definition]

	@property
	def glosses(self):
		for definition in self.definitions:
			yield definition.gloss

	def __str__(self):
		ret = f'Concept: {self.name} (W={self.wiki_id}, B={self.babel_id})\n'
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
	model = spacy.load('en_core_web_sm')
	map: Dict[BabelSynsetID, Concept]

	def __init__(self) -> None:
		self.logger = getLogger(__name__)
		self.map = dict()
		self.babel = SynsetRetriever()
		self.wiki = WikiMap()

	@property
	def category_map(self):
		return self.babel.category_map

	def find_concept(self, name: str, wiki_category: str, definition_limit=None) -> Concept:
		synsets = self.babel.find_synset_in_category(name, wiki_category)
		if len(synsets) == 0:
			raise Exception(f'No synsets found for {name} in category {wiki_category}')
		if len(synsets) > 1:
			self.logger.warning(f'Multiple synsets found for {name} in category {wiki_category}. Using first. Possible: {synsets}')
		synset = synsets[0]
		return self.get_concept(synset, definition_limit)

	def get_concept(self, synset: BabelSynset, definition_limit=None) -> Concept:
		if synset.id in self.map:
			return self.map[synset.id]
		name = self.babel.get_name(synset)
		definitions = self._generate_definitions(synset, limit=definition_limit)
		topic_set = self._generate_topic_set(synset)
		wiki_id = self.babel.get_wiki_id(synset)
		concept = Concept(name, synset.id, wiki_id, topic_set, definitions)
		self.map[concept.babel_id] = concept
		return concept

	def _generate_definitions(self, synset: BabelSynset, limit=None) -> List[Definition]:
		definitions = []
		wiki_id = self.babel.get_wiki_id(synset).title
		categories = self.babel.get_categories(synset)
		glosses = synset.glosses()
		if limit is not None:
			glosses = glosses[:limit]
		for gloss in glosses:
			prereqs = self._generate_prereqs(wiki_id, gloss.gloss, categories)
			definitions.append(Definition(gloss.gloss, prereqs))
		return definitions

	def _generate_prereqs(self, wiki_id: str, definition: str, parent_categories: List[str], commonality_threshold=0.5) -> Set[BabelSynsetID]:
		"""Assumes all prereqs are linked in the wiki article"""
		# TODO: Extract main phrase of sentence
		self.logger.info(f"Generating prereqs for definition of {wiki_id}: {definition}")
		parsed = self.model(definition)
		prereqs = set()
		for noun in parsed.noun_chunks:
			cleaned_noun = self._clean_noun(noun.text)
			if cleaned_noun == '':
				self.logger.debug(f"Skipping empty noun: {noun.text}")
				continue
			synset = self.babel.find_synset_like(cleaned_noun, parent_categories, commonality_threshold)
			if synset is None:
				self.logger.warning(f"Synset not found for {cleaned_noun}")
			elif synset.id in self.map:
				# TODO: New prereq relation must ensure DAG
				self.logger.debug(f"Linked existing concepts! {self.babel.get_name(synset)} is a prereq of {wiki_id}. DAG violation?")
				prereqs.add(synset.id)
			else:
				self.logger.info(f"Prerequisite found: '{self.babel.get_name(synset)}' ({synset.id})")
				prereqs.add(synset.id)
		prereqs.discard(synset.id)
		return prereqs

	# TODO: Find spacy way of dropping stop words
	# TODO: Lemmatize?
	def _clean_noun(self, text: str) -> str:
		words = text.split(' ')
		words = [word for word in words if word not in self.model.Defaults.stop_words]
		return ' '.join(words).lower()

	def compare_commonalities(self, wiki_link, compared_links):
		commonalities = {}
		wiki_categories = self.babel.get_categories(self.babel.get_wiki_synset(wiki_link))
		for link in compared_links:
			# TODO: Get categories from map dataset, not babelnet
			link_synset = self.babel.get_wiki_synset(link)
			if link_synset is not None:
				link_categories = self.babel.get_categories(link_synset)
				commonalities[link] = self.category_map.categorical_commonality(link_categories, wiki_categories)
		return commonalities

	# TODO: Is the score threshold necessary?
	# TODO: Ensure there is traffic between the two articles flows both ways?
	def _generate_topic_set(self, synset: BabelSynset, score_threshold = 0.02) -> Set[BabelSynsetID]:
		"""Uses Wikipedia's clickthrough articles, normalized w/ a score threshold"""
		wiki_id = self.babel.get_wiki_id(synset).title
		ct_rates = self.wiki.get_clickthrough_rates(wiki_id, source_normalized=True)
		ct_rates = ct_rates[ct_rates > score_threshold]
		ct_rates = ct_rates.sort_values(ascending=False)
		self.logger.debug(f'Clickthrough rates: {ct_rates.head(10)} ({len(ct_rates)} total)')
		synsets = [self.babel.get_wiki_synset(link_id) for link_id in ct_rates.index]
		# Not all wikipedia articles are concepts, so they might not exist in babelnet
		ids = set(synset.id for synset in synsets if synset is not None)
		ids.discard(synset.id)
		return ids

	# TODO: Move to an interface?
	def print_all_prereqs(self, concept: Concept):
		print(f'Prerequisites for "{concept.name}":')
		for i, definition in enumerate(concept.definitions, 1):
			if i > 1:
				keep_going = input(f"Continue to next definition of {concept.name} ({i}/{len(concept.definitions)})? (y/N): ")
				if keep_going != 'y':
					return
			print(f'{i}. {definition}')
			if len(definition.prereqs) != 0:
				for babel_id in definition.prereqs:
					do_learn = input(f'Learn about {id_to_name(babel_id)}? (y/N): ')
					if do_learn == 'y':
						self.print_all_prereqs(self.get_concept(get_synset(babel_id)))

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
	for handler in logging.root.handlers:
		logging.root.removeHandler(handler)
	logging.basicConfig(filename='datasets/generated/latest.log', filemode='w', level=logging.DEBUG)
	map = PrerequisiteMap()
	concept = map.find_concept('Control Theory', 'Mathematics', definition_limit=2)
	print(concept)
	map.print_all_prereqs(concept)
