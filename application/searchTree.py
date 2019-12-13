import ahocorasick
import re
import xml.etree.ElementTree as ElementTree
import json


class SearchTree():	
	"""
	Search Tree that performs a semantic search using pre-defined
	ontologies.
	"""
	def __init__(self, filename):
		self.SEARCHTREE_IS_BUILT = False
		self.FILENAME = filename
		
		with open('ontologies/' + filename + ".json", 'r', encoding = "utf-8") as ontology:
			self.tree = json.load(ontology)
			self._searchtree = ahocorasick.Automaton()
		
	def _build_recursive(self, node):
		"""
		Given a node, builds recursively the underlying tree.
		:param node: Node whose subtree we are going to build.
		:return: Subtree for the given node.

		"""
		subtree = {"labels": [], "subcategories": {}}

		for child in node:
			if child.tag == "label":
				subtree["labels"].append(child.text.lower())
			else:
				subtree["subcategories"][child.attrib["ID"]] = self._build_recursive(child)
		
		return subtree
	
	def _build_searchtree_recursive(self, category, node):
		"""
		Given a tree and a category, builds recursively the search tree.
		:param category: Uppermost category to build.
		:param node: Node (usually root) of the subtree to consider.

		"""
		if "labels" in node.keys():
			for label in node["labels"]:
				#self._searchtree.add_word(label, category)
				self._searchtree.add_word(label, (label, category))

		if "subcategories" in node.keys():
			for key, subcategory in node["subcategories"].items():
				self._build_searchtree_recursive(category, subcategory)
	
	def build(self, categories):
		"""
		Given a list of categories of the pre-defined ontologies, builds
		the corresponding Search Tree.
		:param categories: List of categories to consider.

		"""
		for category in categories:
			if category[-1] == '/':
				category = category[:-1]
				
			subclasses = category.split("/")
			
			node = self.tree[subclasses[0]]
			for subclass in subclasses[1:]:
				node = node["subcategories"][subclass]
			
			# We have the subcategory. Time to generate the Search Tree
			self._build_searchtree_recursive(category, node)
		
		self._searchtree.make_automaton()
		self.SEARCHTREE_IS_BUILT = True
			
	def search(self, text):
		"""
		Once the search tree is build, performs search of relevant terms
		in the given string.
		:param text: String we are going to search into.
		:return: List of tags found on the string.

		"""
		if self.SEARCHTREE_IS_BUILT:
			results = []
			tags = []
			
			for end_index, value in self._searchtree.iter(text):
				results.append(value)
			
			for tag in results:
				word, _ = tag
				
				if re.search(r"[^a-zA-Z]" + word, text) and tag not in tags:
					tags.append(tag)
				
			return tags
	
	def __str__(self):
		return json.dumps(self.tree)
