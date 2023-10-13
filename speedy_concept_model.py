from babelnet import BabelSynset
from babelnet.resources import BabelSynsetID
from concurrent.futures import ThreadPoolExecutor
from typing import List, Set

from concept_model import PrerequisiteMap, Definition



class SpeedyPrerequisiteMap(PrerequisiteMap):
	"""Drop-in replacement for PrerequisiteMap that parallelizes operations for speed."""

	def _generate_definitions(self, synset: BabelSynset) -> List[Definition]:
		glosses = synset.glosses()
		self.logger.info(f"Generating {len(glosses)} definitions for {self.search.get_name(synset)}")
		pool = ThreadPoolExecutor(len(glosses))
		categories = self.search.get_categories(synset)
		jobs = [pool.submit(self._generate_prereqs, gloss.gloss, categories) for gloss in glosses]
		definitions = []
		for job, gloss in zip(jobs, glosses):
			prereqs = job.result()
			prereqs -= set([synset.id])
			definitions.append(Definition(gloss.gloss, prereqs))
		return definitions
	
	def _generate_prereqs(self, definition: str, parent_categories: List[str]) -> Set[BabelSynsetID]:
		NotImplementedError()
