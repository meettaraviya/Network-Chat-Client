import json

class Message:
	def __init__(self, json_str=None):
		if json_str!=None:
			self.__dict__.update(json.loads(json_str))
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__)