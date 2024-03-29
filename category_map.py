import logging
import numpy as np
from joblib import Memory
from logging import getLogger
from typing import Optional, List

from category_map_generation import get_category_map, get_parent_tree

memory = Memory("datasets/cache")

@memory.cache
def _get_parent_tree():
	logging.info("Loading category tree...")
	categorylinks, depths = get_category_map()
	return get_parent_tree(categorylinks)


class CategoryMap:
	def __init__(self) -> None:
		self.logger = getLogger(__name__)
		self.root = 'Main_topic_classifications' # Not using 'Contents' because it's too broad
		self.categories = _get_parent_tree()

	def categorical_commonality(self, category_list1: List[str], category_list2: List[str]) -> float:
		"""
		Returns commonality between two lists of categories, between 0 and 1.
		"""
		valid_cats1 = [cat for cat in category_list1 if self.category_in_root(cat)]
		valid_cats2 = [cat for cat in category_list2 if self.category_in_root(cat)]
		if len(valid_cats1) == 0 or len(valid_cats2) == 0:
			return 0
		distances = np.zeros((len(valid_cats1), len(valid_cats2)))
		for i, cat1 in enumerate(valid_cats1):
			for j, cat2 in enumerate(valid_cats2):
				distances[i, j] = self.categorical_distance(cat1, cat2)
		# ? Use minimum values to include all axis, not just minimum of both axes (then divide by longer list length)
		# ? Would this be better?
		min_distances = np.min(distances, axis=0).tolist() + np.min(distances, axis=1).tolist()
		commonality = 1 / np.average(min_distances) # ? Square root to scales the values to be more reasonable (still between 0 and 1)
		self.logger.debug(f"Commonality of {commonality:.2f} between category lists: {valid_cats1} & {valid_cats2}")
		return commonality

	def categorical_distance(self, cat1: str, cat2: str) -> int:
		path1 = self.category_path(cat1, self.root)
		path2 = self.category_path(cat2, self.root)
		if path1 is None or path2 is None:
			raise ValueError(f"Category not connected to root: {cat1} & {cat2} -> {self.root}")
		path1 = [cat1, *path1]
		path2 = [cat2, *path2]
		for i1, c1 in enumerate(path1):
			for i2, c2 in enumerate(path2):
				if c1 == c2:
					return i1 + i2 + 1
		raise ValueError(f"Categories not connected, but this should be impossible\nPaths:{path1}\n{path2})")

	def category_in_root(self, category: str) -> bool:
		return self.category_path(category, self.root) is not None

	def category_path(self, child: str, parent: str) -> Optional[List[str]]:
		parents = self.categories.get(child, [])
		if len(parents) == 0:
			return None
		if parent in parents:
			return [parent]
		for category in parents:
			path = self.category_path(category, parent)
			if path is not None:
				return [category, *path]


if __name__ == "__main__":
	management = ['Business_terms', 'Wikipedia_articles_incorporating_a_citation_from_the_1911_Encyclopaedia_Britannica_with_Wikisource_reference', 'Control_theory', 'Management', 'All_articles_with_peacock_terms', 'All_articles_with_style_issues', 'Articles_with_multiple_maintenance_issues', 'Control_(social_and_political)', 'All_articles_needing_additional_references']
	optimal_controls = ['Applied_mathematics_stubs', 'Control_theory']
	control_theory = ['Use_mdy_dates_from_July_2016', 'Computer_engineering', 'Articles_with_short_description', 'Control_theory', 'Control_engineering', 'Cybernetics']
	mapper = CategoryMap()
	print('management, optimal_controls:', mapper.categorical_commonality(management, optimal_controls))
	print('management, control_theory:', mapper.categorical_commonality(management, control_theory))
	print('optimal_controls, control_theory:', mapper.categorical_commonality(optimal_controls, control_theory))
	print('control_theory, control_theory:', mapper.categorical_commonality(control_theory, control_theory))