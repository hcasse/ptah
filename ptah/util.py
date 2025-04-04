"""Misc. utilities for ptah."""

from string import Template
import sys

DEBUG = False

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


class AttrMapOld:			# to remove
	"""A map of attributes."""

	def __init__(self, parent=None):
		self.parent = parent
		self.attrs = {}

	def set_attr(self, name, val):
		"""Set the value of an attribute."""
		self.attrs[name] = val

	def get_attr(self, name):
		"""Get the value of an attribute. Return None if not found."""
		try:
			return self.attrs[name]
		except KeyError:
			return None

	def check(self):
		"""Called to check the validity of attributes. Call CheckError
		if something is wrong."""
		pass

	def get_props_map(self):
		"""Get the map of supported properties."""
		return {}


def parse_dict_old(data, base, props, mon):		# to remove
	"""Parse the given data, that is a dictionary, and call functions
	proprties, a map made (key, fun) according to the key found in data.
	The function has to take 2 parameters (value, base). The base must
	inherit from AttrMap and are assigned for any key of data not found
	in props. Call check() on base in the end."""

	def parse_val(key, val, base):
		try:
			prop = props[key]
			val = prop.parse(val, base)
			base.set_attr(prop.name, val)
		except KeyError:
			mon.print_warning(f"no property {key} in {base}. Ignoring it.")

	# pick the properties
	for (key, val) in data.items():
		#print("DEBUG:", key, val)
		p = key.find('#')

		# single value
		if p < 0:
			parse_val(key, val, base)

		# multiple value
		else:
			id = key[:p]
			try:
				i = int(key[p+1:]) - 1
				item = base.get_item(i)
				parse_val(id, val, item)
			except ValueError:
				mon.print_warning(f"bad number in {key} of {base}. Ignoring it.")

	# check the properties
	for prop in props.values():
		prop.check(base)

def normalize(s):
	"""Normalize s to lower case and remove spaces."""
	return s.lower().replace(' ', '').replace('_', '-')

class Console:
	"""Console for user interaction."""
	stderr = sys.stderr

	def warn(self, msg):
		self.stderr.write(f"WARNING: {msg}\n")

CONSOLE = Console()
