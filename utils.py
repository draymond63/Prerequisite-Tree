import re
import string
import networkx as nx
from typing import Optional

# edges = pd.read_csv('datasets/scratch/initial-prereqs.tsv', sep='\t', header=None)
def draw_graph(edges: list, filename: str = 'example.png'):
	G = nx.DiGraph()
	G.add_edges_from(edges)
	p=nx.drawing.nx_pydot.to_pydot(G)
	p.write_png(filename)

class StringUtils:
	@staticmethod
	def remove_tags(text: str) -> str:
		return re.sub(r'<[^>]+>.*?</[^>]+>', '', text)
	
	@staticmethod
	def remove_wiki_links(text: str) -> str:
		unlinked_text = re.sub(r'\[\[.*?\|([^\]]+)\]\]', r'\1', text)
		return re.sub(r'\[\[.*\]\]', '', unlinked_text) 

	@staticmethod
	def replace_characters(text: str, map: dict) -> str:
		return text.translate(str.maketrans(map))
	
	@staticmethod
	def remove_characters(text: str, characters: str) -> str:
		return text.translate(str.maketrans('', '', characters))

	@staticmethod
	def parse_acronym(title: str, definition: str, use_innerword_letters = False) -> Optional[str]:
		"""Returns the title of the acronym if the definition is an acronym of the title, otherwise None."""
		if not title.isupper() or ' ' in title:
			return False
		cleaned_definition = StringUtils.replace_characters(definition, {char: ' ' for char in string.punctuation})
		definition_words = [word.capitalize() for word in cleaned_definition.split(' ')]
		remaining_acronym_letters = StringUtils.remove_characters(title, string.punctuation)
		first_acronym_word: int | None = None
		last_acronym_word: int | None = None
		for word_index, word in enumerate(definition_words):
			if not len(word):
				continue
			word_in_acronym = False
			if word[0] == remaining_acronym_letters[0]:
				word_in_acronym = True
				remaining_acronym_letters = remaining_acronym_letters[1:]
			if use_innerword_letters and len(remaining_acronym_letters):
				found_letter = StringUtils.find_letter(word[1:], remaining_acronym_letters[0], not word_in_acronym)
				while found_letter != -1 and len(remaining_acronym_letters):
					found_letter = StringUtils.find_letter(word[found_letter + 1:], remaining_acronym_letters[0], not word_in_acronym)
					word_in_acronym = True
					remaining_acronym_letters = remaining_acronym_letters[1:]
			if word_in_acronym and first_acronym_word is None:
				first_acronym_word = word_index
			if not remaining_acronym_letters:
				last_acronym_word = word_index + 1
				break
		if first_acronym_word is not None and last_acronym_word is not None:
			key_words = definition_words[first_acronym_word:last_acronym_word]
			return ' '.join(key_words)
		if not use_innerword_letters:
			return StringUtils.parse_acronym(title, definition, use_innerword_letters=True)

	@staticmethod
	def find_letter(text: str, letter: str, case_sensitive=False) -> int:
		for index, character in enumerate(text):
			if not case_sensitive:
				character = character.upper()
				letter = letter.upper()
			if character == letter:
				return index
		return -1


if __name__ == '__main__':
	test = StringUtils.parse_acronym('L/R', 'blah blah Local/Remote blah blah')
	print(test)