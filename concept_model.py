from uuid import uuid4, UUID
from typing import Set, Dict, List

from article_model import Article


class PrerequisiteMap:
    map: 'Dict[UUID, Concept]'
    corpus: List[Article]

    # TODO: Ideally accept a list of candidates, without definitions
    def __init__(self, concept_candidates: Dict[str, str], corpus: List[Article]) -> None:
        self.map = self.parse_concepts(concept_candidates)
        self.corpus = corpus # Set of documents

    def parse_concepts(self, concept_candidates: Dict[str, str]) -> 'Dict[str, Concept]':
        concepts = {}
        for name, definition in concept_candidates.items():
            if self.is_valid_concept(name, definition):
                concept_name = self.get_best_name(name, definition)
                concepts[concept_name] = Concept(concept_name, definition)
        return concepts

    # TODO: Implement
    def is_valid_concept(self, name: str, definition: str) -> bool:
        return True

    def get_best_name(self, name: str, definition: str) -> str:
        acronym_title = self.parse_acronym_meaning(name, definition)
        if acronym_title:
            return acronym_title
        return name

    # TODO: Convert to `parse_acronym_meaning`
    @staticmethod
    def is_acronym(title: str, definition: str) -> bool:
        if not title.isupper() or ' ' in title:
            return False
        acronym_index = 0
        for word in definition.split():
            if word[0].capitalize() == title[acronym_index]:
                acronym_index += 1
                if acronym_index == len(title):
                    return True
        return False


class Concept:
    names: List[str]
    definitions: Set[str]
    definitional_concepts: Set[str]
    prerequisites: 'Set[Concept]' # TODO: Or UUIDs?
    topic_set: 'Set[Concept]' # TODO: Or UUIDs?

    def __init__(self, name: str, definition: str) -> None:
        self.uuid = uuid4()
        # TODO: How should multiple names and definitions be handled?
        self.names = [name]
        self.definitions = set([definition]) # All valid definitions of the concept
        self.definitional_concepts = self.parse_concepts() # Concepts mentioned in the definition
        self.prerequisites = set() # Topics that must be learned before this topic
        self.topic_set = set() # Concepts that are part of this topic (e.g. a chapter in a book)

    # TODO: A concept shouldn't do this, right?
    def parse_concepts(definition: str) -> Set[str]:
        ...

    def get_prerequiste_relations(self):
        for prereq in self.prerequisites:
            yield prereq.name

    def get_concepts_in_topic(self):
        for concept in self.topic_set:
            yield concept.name

    # TODO: Add ability to merge concepts

    def __repr__(self) -> str:
        return f'Concept: {self.name}'
