from uuid import uuid4, UUID
from typing import Set, Dict, List, Optional

from article_model import Article


class PrerequisiteMap:
    map: 'Dict[UUID, Concept]'
    corpus: List[Article]

    # TODO: Ideally accept a list of candidates, without definitions
    def __init__(self, concept_candidates: Dict[str, str], corpus: List[Article]) -> None:
        self.corpus = corpus # Set of documents
        self.map = self.select_valid_concepts(concept_candidates)
        self.generate_connections()

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

    def generate_connections(self) -> None:
        for concept in self.map.values():
            concept.prerequisites = self.parse_concepts(concept.definition)

    # TODO: Implement
    def parse_concepts(self, text: str) -> 'Set[Concept]':
        ...


# TODO: Add ability to merge concepts
class Concept:
    name: str
    definitions: str
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
        acronym_title = self.parse_acronym_meaning(name, definition)
        if acronym_title:
            return acronym_title
        return name

    @staticmethod
    def parse_acronym(title: str, definition: str) -> Optional[str]:
        """Returns the title of the acronym if the definition is an acronym of the title, otherwise None."""
        if not title.isupper() or ' ' in title:
            return False
        definition_words = [word.capitalize() for word in definition.replace('-', ' ').split(' ')]
        remaining_acronym_letters = title.replace('/', '')
        first_acronym_word: int | None = None
        last_acronym_word: int | None = None
        for word_index, word in enumerate(definition_words):
            if not len(word):
                continue
            word_in_acronym = False
            if word[0] == remaining_acronym_letters[0]:
                word_in_acronym = True
                remaining_acronym_letters = remaining_acronym_letters[1:]
            if len(remaining_acronym_letters):
                for character in word[1:]:
                    candidate = character.upper() if word_in_acronym else character
                    if candidate == remaining_acronym_letters[0]:
                        word_in_acronym = True
                        remaining_acronym_letters = remaining_acronym_letters[1:]
                    if not len(remaining_acronym_letters):
                        break
            if word_in_acronym and first_acronym_word is None:
                first_acronym_word = word_index
            if not remaining_acronym_letters:
                last_acronym_word = word_index + 1
                break
        if first_acronym_word is not None and last_acronym_word is not None:
            return  ' '.join(definition_words[first_acronym_word:last_acronym_word])

    def __repr__(self) -> str:
        return f'Concept: {self.name}'
