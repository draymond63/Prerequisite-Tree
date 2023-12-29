import spacy
import logging
from thefuzz import fuzz, process
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
		wiki_id = self.babel.get_wiki_id(synset)
		concept = Concept(name, synset.id, wiki_id, topic_set, definitions)
		self.map[concept.babel_id] = concept
		return concept

	def _generate_definitions(self, synset: BabelSynset) -> List[Definition]:
		definitions = []
		wiki_id = self.babel.get_wiki_id(synset).title
		for gloss in synset.glosses()[:1]: # TODO: Limited to 1 definition for testing
			prereqs = self._generate_prereqs(wiki_id, gloss.gloss)
			prereqs.discard(synset.id)
			definitions.append(Definition(gloss.gloss, prereqs))
		return definitions

	def _generate_prereqs(self, wiki_id: str, definition: str, str_match_threshold = 0.6, commonality_threshold = 0.5) -> Set[BabelSynsetID]:
		"""Assumes all prereqs are linked in the wiki article"""
		# TODO: Extract main phrase of sentence
		self.logger.info(f"Generating prereqs for definition of {wiki_id}: {definition}")
		parsed = self.model(definition)
		prereqs = set()
		ct_links = self.wiki.get_clickthrough_links(wiki_id)
		# TODO: Low ct_link counts result in few candidates and bad results
		if not len(ct_links):
			self.logger.warning(f"No clickthrough links found for '{wiki_id}'")
			return prereqs
		ct_titles = {link: WikiMap.link_to_title(link) for link in ct_links}
		for noun in parsed.noun_chunks:
			matches = process.extractBests(noun.text, ct_titles, scorer=fuzz.token_sort_ratio, score_cutoff=str_match_threshold * 100)
			links = [link for name, score, link in matches]
			self.logger.debug(f"Possible matches for '{noun}': {links}")
			if not len(links):
				continue
			# Select link with highest categorical commonality
			commonalities = self.compare_commonalities(wiki_id, links)
			if not len(commonalities):
				continue
			concept_link = max(commonalities, key=commonalities.get)
			if commonalities[concept_link] < commonality_threshold:
				self.logger.debug(f"Commonality of '{concept_link}' is too low: {commonalities}")
				continue
			self.logger.info(f"Prerequisite found: '{concept_link}'")
			synset = self.babel.get_wiki_synset(concept_link)
			# Not all wikipedia articles are concepts, so they might not exist in babelnet
			if synset is None:
				self.logger.warning(f"Synset not found for {concept_link}")
			else:
				# TODO: New prereq relation must ensure DAG
				if synset.id in self.map:
					self.logger.debug(f"Linked existing concepts! {concept_link} is a prereq of {wiki_id}. DAG violation?")
				prereqs.add(synset.id)
		return prereqs

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
	for handler in logging.root.handlers:
		logging.root.removeHandler(handler)
	logging.basicConfig(filename='datasets/generated/latest.log', filemode='w', level=logging.DEBUG)
	map = PrerequisiteMap()
	concept = map.find_concept('Control Theory', 'Mathematics')
	print(concept)
	map.print_all_prereqs(concept)
