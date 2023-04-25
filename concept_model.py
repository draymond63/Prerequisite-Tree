import re
import string
from tqdm import tqdm
from uuid import uuid4, UUID
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from typing import Set, Dict, List, Optional

from utils import StringUtils
from article_model import Article


class LemmaTokenizer:
	def __init__(self):
		self.wnl = WordNetLemmatizer()
	def __call__(self, doc) -> List[str]:
		regex_num_ponctuation = '(\d+)|([^\w\s])'
		regex_little_words = r'(\b\w{1,2}\b)'
		return [self.wnl.lemmatize(t) for t in word_tokenize(doc) 
				if not re.search(regex_num_ponctuation, t) and not re.search(regex_little_words, t)]


class PrerequisiteMap:
	map: 'Dict[UUID, Concept]'
	_corpus: List[Article]

	# TODO: Ideally accept a list of candidates, without definitions
	def __init__(self, concept_candidates: Dict[str, str], corpus: List[Article]) -> None:
		self._corpus = corpus # Set of documents
		self.lemmatizer = LemmaTokenizer()
		self.corpus_ngrams = self.get_ngrams([article.get_content() for article in corpus])
		self.map = self.select_valid_concepts(concept_candidates)
		self._generate_connections()

	# TODO: How many ngrams should be counted?
	# TODO: Supply vocabulary?
	def get_ngrams(self, corpus: List[str], ngram_range=(1, 5)) -> Dict[str, int]:
		vectorizer = TfidfVectorizer(analyzer='word', ngram_range=ngram_range, min_df=1, stop_words='english', tokenizer=self.lemmatizer)
		X = vectorizer.fit_transform(corpus)
		candidates = vectorizer.get_feature_names_out()
		counts = X.toarray().sum(axis=0)
		counts = {candidate: count for candidate, count in zip(candidates, counts) if count > 0}
		return counts

	def select_valid_concepts(self, concept_candidates: Dict[str, str]) -> 'Dict[str, Concept]':
		concepts = {}
		for name, definition in concept_candidates.items():
			concept = Concept(name, definition)
			if self.is_valid_concept(concept):
				concepts[concept.uuid] = concept
		return concepts

	def is_valid_concept(self, concept: 'Concept') -> bool:
		ngrams = self.corpus_ngrams.keys()
		lemmatized_concept = ' '.join(self.lemmatizer(concept.name)).lower()
		return lemmatized_concept in ngrams # TODO: Base on TF-IDF

	def _generate_connections(self) -> None:
		for concept in self.map.values():
			concept.prerequisites = self.parse_concepts(concept.definition)
			concept.prerequisites -= {concept}
			print(concept.name, [*concept.get_prerequiste_relations()])

	def parse_concepts(self, text: str) -> 'Set[Concept]':
		if not text:
			return set()
		ngrams = self.get_ngrams([text]).keys()
		found_concepts = set()
		for ngram in ngrams:
			concept = self.find_concept(ngram)
			if concept:
				found_concepts.add(concept)
		return found_concepts

	def find_concept(self, name: str) -> 'Optional[Concept]':
		lemmatized_name = ' '.join(self.lemmatizer(name)).lower()
		for concept in self.map.values():
			lemmatized_concept = ' '.join(self.lemmatizer(concept.name)).lower()
			if lemmatized_name == lemmatized_concept:
				return concept

	def save(self, path: str) -> None:
		with open(path, 'w') as f:
			for concept in self.map.values():
				for prereq in concept.get_prerequiste_relations():
					f.write(f'{concept.name}\t{prereq}\n')


# TODO: Add ability to merge concepts
class Concept:
	name: str
	definition: str
	prerequisites: 'Set[Concept]' # TODO: Or UUIDs?
	topic_set: 'Set[Concept]' # TODO: Or UUIDs?

	def __init__(self, name: str, definition: str) -> None:
		self.uuid = uuid4()
		# TODO: How should multiple names and definitions be handled?
		self.name = self.get_best_name(name, definition)
		self.definition = definition # All valid definitions of the concept
		self.prerequisites = set() # Topics that must be learned before this topic
		self.topic_set = set() # Concepts that are part of this topic (e.g. a chapter in a book)

	def get_prerequiste_relations(self):
		for prereq in self.prerequisites:
			yield prereq.name

	def get_concepts_in_topic(self):
		for concept in self.topic_set:
			yield concept.name

	def get_best_name(self, name: str, definition: str) -> str:
		cleaned_name = re.sub(r'\([^)]+\)', '', name) # Remove parentheticals
		acronym_title = StringUtils.parse_acronym(cleaned_name, definition)
		if acronym_title:
			cleaned_name = acronym_title
		characters_to_replace = StringUtils.remove_characters(string.punctuation, "-'+")
		cleaned_name = StringUtils.remove_characters(cleaned_name, characters_to_replace).strip()
		# TODO: Nounify
		return cleaned_name

	def __repr__(self) -> str:
		return f'Concept: {self.name}'


def parse_textbook(page_titles: List[str], glossary_title: str) -> PrerequisiteMap:
	pages = {page_title: page_text for page_title, page_id, page_text in tqdm(PageRetriever().get(page_titles), total=len(page_titles))}
	glossary = Article(glossary_title, pages[glossary_title])
	articles = [Article(title, text) for title, text in pages.items()]
	concepts = {section.header: section.content for section in glossary.sections.iter(leaves_only=True)}
	return PrerequisiteMap(concepts, articles)

if __name__ == '__main__':
	from page_retrieval import PageRetriever
	from article_model import Article

	title = 'Control_Systems/Glossary'
	# text = PageRetriever().get_article_text(title)
	text = open('datasets/scratch/Control Systems-Glossary.md').read()
	article = Article(title, text)

	concepts = {section.header: section.content for section in article.sections.iter(leaves_only=True)}
	concept_map = PrerequisiteMap(concepts, [article])
	concept_map.save('prereqs.tsv')

	# names = [concept.name for concept in concept_map.map.values()]
	# open('valid_concepts.txt', 'w').write('\n'.join(names))
	# open('ngrams.txt', 'w').write('\n'.join(concept_map.corpus_ngrams.keys()))
