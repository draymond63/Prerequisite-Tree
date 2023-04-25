import re
import string
from uuid import uuid4, UUID
from typing import Set, Dict, List

from utils import StringUtils
from article_model import Article


class PrerequisiteMap:
    map: 'Dict[UUID, Concept]'
    corpus: List[Article]

    # TODO: Ideally accept a list of candidates, without definitions
    def __init__(self, concept_candidates: Dict[str, str], corpus: List[Article]) -> None:
        self.corpus = corpus # Set of documents
        self.map = self.select_valid_concepts(concept_candidates)
        self._generate_connections()

    def select_valid_concepts(self, concept_candidates: Dict[str, str]) -> 'Dict[str, Concept]':
        concepts = {}
        for name, definition in concept_candidates.items():
            concept = Concept(name, definition)
            if self.is_valid_concept(concept):
                concepts[concept.uuid] = concept
        return concepts

    # TODO: Implement
    # If the concept has a high enough tfidf, it is valid
    # If the concept contains common words, it is not valid?
    # If the concept is a named entity, it is invalid?
    def is_valid_concept(self, concept: 'Concept') -> bool:
        return True

    def _generate_connections(self) -> None:
        for concept in self.map.values():
            concept.prerequisites = self.parse_concepts(concept.definition)

    # TODO: Implement
    def parse_concepts(self, text: str) -> 'Set[Concept]':
        ...


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
        return cleaned_name

    def __repr__(self) -> str:
        return f'Concept: {self.name}'


if __name__ == '__main__':
    from page_retrieval import PageRetriever
    from article_model import Article

    title = 'Control_Systems/Glossary'
    # text = PageRetriever().get_article_text(title)
    text = open('datasets/scratch/Control Systems-Glossary.md').read()
    article = Article(title, text)

    concepts = {section.header: section.content for section in article.sections.iter(leaves_only=True)}
    concept_map = PrerequisiteMap(concepts, [article])
    names = [concept.name for concept in concept_map.map.values()]
    open('test.txt', 'w').write('\n'.join(names))
