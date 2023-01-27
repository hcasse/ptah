"""Misc. utilities for ptah."""

from string import Template

def generate(templ, **args):
	"""Generate the given template with the passed arguments."""
	return Template(templ).substitute(**args)


class CheckError(Exception):
	"""Error raised when there is an error in the description file."""

	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

	def __str__(self):
		return self.msg


class AttrMap:
	"""A map of attributes."""

	def __init__(self):
		self.map = {}

	def set_attr(self, name, val):
		"""Set the value of an attribute."""
		self.map[name] = val

	def get_attr(self, name):
		"""Get the value of an attribute.
		Return None if not found."""
		try:
			return self.map[name]
		except KeyError:
			return None

	def check(self):
		"""Called to check the validity of attributes. Call CheckError
		if something is wrong."""
		pass

def parse_dict(data, base, props):
	"""Parse the given data, that is a dictionary, and call functions
	proprties, a map made (key, fun) according to the key found in data.
	The function has to take 2 parameters (value, base). The base mus
	inherit from AttrMap and are assigned for any key of data not found
	in props. Call check() on base in the end."""

	# pick the properties
	for (key, val) in data.items():
		try:
			p = key.find('#')
			if p < 0:
				props[key].set(val, base)
			else:
				id = key[:p]
				i = int(key[p+1:]) - 1
				props[id].set_indexed(i, val, base)
		except ValueError:
			raise CheckError("bad index %s" % key)
		except KeyError:
			base.set_attr(key, data[key])

	# check the properties
	for prop in props:
		props[prop].check(base)
