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
	
	def run(self, uid, text):
		response = {}
		
		for assistant in self.l_assistants_:
			response[assistant.label] = {}
			
			if assistant.kind == "ontology":
				cls, reason = assistant.get_class(text)

				response[assistant.label]["why"] = reason
				response[assistant.label]["how"] = assistant.kind
				response[assistant.label]["what"] = cls
			elif assistant.kind == "extended_properties":
				cls, reason = assistant.get_class(uid)

				reason_text = ""
				for prop, value in reason.items():
					reason_text += "{}: {}\n".format(prop, value)
				
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


class ExtendedPropertiesAssistant(Assistant):
	def __init__(self, label, kind="extended_properties"):
		self.label = label
		self.kind = kind


	def get_class(self, uid):
		from application.models import Label, UserAnnotation
		ua = UserAnnotation.query.filter_by(user_id=uid).order_by(UserAnnotation.timestamp.desc()).first()

		if ua:
			response = {}
			for label_name, value in ua.extended_labels.items():
				response[label_name] = {"value": value}

				label = Label.query.filter_by(name=label_name).first()
				if label:
					value_names = label.values.split(',')
					response[label_name]["value_name"] = value_names[0] if value < 0 else value_names[1]

			return 1, response
		else:
			return 0, {}
