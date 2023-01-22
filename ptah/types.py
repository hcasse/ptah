
BOOL_TRUE = { "true", "on", "yes" }
BOOL_FALSE = { "false", "off", "no"}


class TypeError(Exception):
	pass


class Type:
	"""Class used to check type of Yaml arguments."""

	def check(self, text):
		"""Check the given value and return the runtime value."""
		return text


class IntType(Type):

	def check(self, text):
		try:
			return int(text)
		except ValueError:
			raise TypeError()


def FloatType(Type):

	def check(self, text):
		try:
			return float(text)
		except ValueError:
			raise TypeError()


def StrType(Type):

	def check(self, text):
		return text


def BoolType(Type):

	def check(self, text):
		text = text.lower()
		if text in BOOL_TRUE:
			return True
		elif text in BOOL_FALSE:
			return False
		else:
			raise TypeError()


def EnumType(Type):

	def __init__(self, enums):
		self.enums = enums

	def check(self, text):
		if text in enums:
			return text
		else:
			raise TypeError()


def MapType(Type):

	def __init__(self, map):
		self.map = map

	def check(self, text):
		try:
			return self.map[text]
		except KeyError:
			raise TypeError()

def UnionType(Type):

	def __init__(self.types):
		self.types = types

	def check(self, text):
		for type in self.types:
			try:
				return type.check(text)
			except TypeError:
				pass
		raise TypeError()
	
