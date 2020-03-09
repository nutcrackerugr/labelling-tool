from .searchTree import SearchTree


class Assistant():
	
	def __init__(self, label, kind=None):
		self.label = label
		self.kind = kind
	
	def get_class(self, text):
		return "test_class_for_label_" + self.label, "the reason is because yes"

class AssistantManager():
	def __init__(self):
		self.l_assistants_ = []
		
	def add_assistant(self, assistant):
		self.l_assistants_.append(assistant)
	
	def run(self, text):
		response = {}
		
		for assistant in self.l_assistants_:
			response[assistant.label] = {}
			
			cls, reason = assistant.get_class(text)

			response[assistant.label]["why"] = reason
			response[assistant.label]["how"] = assistant.kind
			response[assistant.label]["what"] = cls
		
		return response


class OntologyAssistant(Assistant):
	def __init__(self, label, kind="ontology", app=None, filename=None):
		self.label = label
		self.kind = kind
		
		if not filename:
			self.filename = label
		
		if app:
			self.tree = SearchTree(self.filename, path=app.config["ONTOLOGIES_PATH"])
		else:
			self.tree = SearchTree(self.filename)

		self.tree.build([self.filename])
	
	def get_class(self, text):
		tags = self.tree.search(text.lower())
		
		return 1 if tags else 0, tags
