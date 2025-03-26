"""Management of properties for pages and album."""

import os
import re

import ptah
from ptah.util import CheckError
from ptah import graph

def implies_def(obj, index):
	"""Default implies function."""
	pass

def implies_set(prop, val1, val2):
	"""Implementation of implies (in Property construction) that
	assign the val2 if the corresponding property has for value1.
	Useful for default activation of a property."""
	def doit(obj, index):
		if prop.get(obj, index) == val1:
			prop.set(obj, index, val2)
	return doit

class Property:
	"""Property to describe a page or an album."""

	def __init__(self,
			id, desc, fun,
			mode = 0,
			implies = lambda obj,
			index: None,
			default = None
		):
		self.id = id
		self.pid = id.replace("-", "_")
		self.desc = desc
		self.mode = mode
		self.fun = fun
		self.implies = implies
		self.default = default

	def parse(self, val, obj):
		"""Parse the given text and return the corresponding text.
		Raises CheckError if the text is not valid."""
		return self.fun(self, val, obj)

	def get(self, obj, index = None):
		""""Get the value corresponding to the property in the given
		object at the given index (if any)."""
		if index == None:
			return obj.__dict__[self.pid]
		else:
			return obj.__dict__[self.pid][index]

	def set(self, obj, index, val):
		"""Set the value (without index test)."""
		if index == None:
			obj.__dict__[self.pid]  = val
		else:
			obj.__dict__[self.pid][index] = val

	def set_scalar(self, val, obj):
		"""Parse the file value and set it, if valid, to the object
		corresponding field. The default implementation performs
		the assignment to the field without test. May raise
		CheckError if the value is not valid."""
		if hasattr(obj.__dict__[self.pid], "__setitem__"):
			raise CheckError("property %s must be indexed #i in %s." %
				(self.id, obj.name))
		obj.__dict__[self.pid] = self.parse(val, obj)
		self.implies(obj, None)

	def is_indexed(self):
		"""Test if the property supports indexes."""
		return self.multi

	def set_indexed(self, i, val, obj):
		"""Same as parse() but with an array. In addition, may raise
		CheckError if the index is too big."""
		l = obj.__dict__[self.pid]
		if not hasattr(l, "__setitem__"):
			raise CheckError("property %s is not indexed in %s." %
				(self.id, obj.name))
		if i < 0 or i >= len(l):
			raise CheckError("property %s#%d with bad index in %s." %
				(self.id, i, obj.name))
		l[i] = self.parse(val, obj)
		self.implies(obj, i)

	def lookup_parent(self, p):
		p = p.parent
		while(p != None):
			if p.__dict__[self.pid] != None:
				return p.__dict__[self.pid]
			p = p.parent
		return None

	def init(self, obj, n, is_root = False):
		"""Initialize a property in the given object in n instances."""
		x = self.default
		if self.mode == ptah.PROP_INH and not is_root:
			x = None
		if n == 1:
			obj.__dict__[self.pid] = x
		else:
			obj.__dict__[self.pid] = [x] * n

	def check(self, obj):
		"""Check if the property is correctly set in the object."""

		# mode required
		if self.mode == 1:
			l = obj.__dict__[self.pid]
			if not hasattr(l, "__getitem__"):
				if l == None:
					raise CheckError("property %s is required for %s!" %
						(self.id, obj.name))
			else:
				l = obj.__dict__[self.pid]
				for i in range(0, len(l)):
					if l[i] == None:
						raise CheckError("property %s#%d is required for %s!" %
							(self.id, i+1, obj.name))

		# mode inherited
		elif self.mode == 2:
			l = obj.__dict__[self.pid]
			if not hasattr(l, "__getitem__"):
				if l == None:
					obj.__dict__[self.pid] = self.lookup_parent(obj)
			else:
				l = obj.__dict__[self.pid]
				x = None
				for i in range(0, len(l)):
					if l[i] == None:
						if x == None:
							x = self.lookup_parent(obj)
						l[i] = x


	def get_description(self):
		"""Get the description of the property."""
		return self.desc


def type_float(self, val, obj):
	try:
		return float(val)
	except ValueError:
		raise CheckError("value %s of %s should be a floatting-pointer number"
			% (self.id, obj.name))

LENGTH_RE = re.compile("([+-]?[0-9\.]?)([a-zA-Z]+)")

LENGTH_UNITS = {
	"mm": 1,
	"cm": 10,
	"dm": 100,
	"in": 25.4,
	"pt": 0.3514598
}

def type_string(self, val, obj):
	return val

def type_image(self, path, page):
	if not os.path.exists(os.path.join(page.album.get_base(), path)):
		raise CheckError("no image on path '%s' for %s" %
			(path, page.name))
	return path

def type_enum(vals):
	def fun(self, val, obj):
		val = val.lower()
		for i in range(0, len(vals)):
				if val == vals[i]:
					return i
		raise CheckError("in %s, %s must be one of %s" %
			(obj.name, id, ", ".join(vals)))
	return fun

def type_color(self, col, obj):
	if isinstance(col, str):
		col = col.strip().lower()
		if col.startswith('#'):
			if len(col) == 7:
				try:
					int(col[1:], 16)
					return col
				except ValueError:
					pass
		else:
			try:
				return graph.HTML_COLORS[col]
			except KeyError:
				pass
	raise CheckError("%s: bad color in %s!" % (self.id, obj.name))

def type_length(self, val, obj):
	try:
		if isinstance(val, (int, float)):
			return graph.AbsLength(val)
		elif val.endswith("%"):
			return graph.PropLength(float(val[:-1]) / 100.)
		else:
			m = LENGTH_RE.match(val)
			if m != None:
				return graph.AbsLength(
					float(m.group(1)) * LENGTH_UNITS[m.group(2)])
	except (ValueError, KeyError):
		pass
	raise CheckError("bad length for %s in %s" % (self.id, obj.name))

def type_bool(self, val, obj):
	if val == False or val == True:
		return val
	else:
		raise CheckError("bad boolean value for %s in %s."
			% (self.id, obj.name))

def type_union(types):
	def fun(self, val, obj):
		for type in types:
			try:
				return type(self, val, obj)
			except CheckError:
				continue
		raise CheckError("cannot parse %s in %s" % (self.id, obj.name))
	return fun

def type_percent(val, obj):
	"""Parse a percent argument like FLOAT% or FLOAT in [0, 1].
	Return a value in [0, 1]."""
	try:
		if val.endswith("%"):
			x = float(val[:-1]) / 100.
		else:
			x = float(val)
		if 0 <= x and x <= 1:
			return x
	except ValueError:
		pass
	raise CheckError("cannot parse value %s for %s in %s" %
		(val, self.id, obj.name))


# For compatibility
def ImageProperty(id, desc, mode = 1):
	return Property(id, desc, type_image, mode)
def EnumProperty(id, desc, vals, mode = 0):
	return Property(id, desc, type_enum(vals), mode)
def StringProperty(id, desc, mode = 0):
	return Property(id, desc, type_string, mode)
def FloatProperty(id, desc, mode = 0):
	return Property(id, desc, type_float, mode)
def ColorProperty(id, desc, mode = 0):
	return Property(id, desc, type_color, mode)
def LengthProperty(id, desc, mode = 0):
	return Property(id, desc, type_length, mode)
def BoolProperty(id, desc, mode = 0):
	return Property(id, desc, type_bool, mode)


class Container:
	"""Class that may contain sub-objects."""

	def __init__(self, parent = None):
		self.parent = parent

	def set_parent(self, parent):
		self.parent = parent


def make(*props):
	"""Build a property map."""
	map = {}
	for prop in props:
		if isinstance(prop, dict):
			map.update(prop)
		elif isinstance(prop, list):
			for p in prop:
				map[p.id] = p
		else:
			map[prop.id] = prop
	return map

"""Known pages."""
PAGE_MAP = {
}
