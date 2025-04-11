"""Management of properties for pages and album."""

import os
import re
import sys
import traceback

import ptah.font
from ptah.util import CheckError, normalize
from ptah import graph
from ptah import io

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

	def resolve_old(self, obj, direct=False, required=False, default=None):
		"""Resolve the value of a propertry. If direct is True, do not lookup
		in parents. If required, raises an error if the property cannot be
		found. Returns the value of the property or None if it cannot be found."""
		val = obj.get_attr(self.id)
		if val is not None:
			return val
		if not direct and obj.parent is not None:
			val = self.resolve(obj.parent, direct, required)
		if val is None:
			if required:
				raise CheckError(f"property {self.id} is required in {obj.name}")
			else:
				val = default
		return val

	def set_scalar_old(self, val, obj):
		"""Parse the file value and set it, if valid, to the object
		corresponding field. The default implementation performs
		the assignment to the field without test. May raise
		CheckError if the value is not valid."""
		if hasattr(obj.__dict__[self.pid], "__setitem__"):
			raise CheckError("property %s must be indexed #i in %s." %
				(self.id, obj.name))
		obj.__dict__[self.pid] = self.parse(val, obj)
		self.implies(obj, None)

	def is_indexed_old(self):
		"""Test if the property supports indexes."""
		return self.multi

	def set_indexed_old(self, i, val, obj):
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

	def lookup_parent_old(self, p):
		p = p.parent
		while(p != None):
			if p.__dict__[self.pid] != None:
				return p.__dict__[self.pid]
			p = p.parent
		return None

	def init_old(self, obj, n = 1, is_root = False):
		"""Initialize a property in the given object in n instances."""
		obj.__dict__[self.pid] = None
		#x = self.default
		#if self.mode == ptah.PROP_INH and not is_root:
		#	x = None
		#if n == 1:
		#	obj.__dict__[self.pid] = x
		#else:
		#	obj.__dict__[self.pid] = [x] * n

	def set_old(self, obj, val):
		"""Set the value of a property."""
		obj.__dict__[self.pid] = val

	def check_old(self, obj):
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
	actual_path = page.get_album().find(path)
	if actual_path is None:
		io.DEF.print_warning(f"image {path} in {page.get_location()} cannot be found!")
		actual_path = ""
	return actual_path

def type_enum(vals):
	def fun(self, val, obj):
		val = val.lower()
		for i in range(0, len(vals)):
				if val == vals[i]:
					return i
		raise CheckError("in %s, %s must be one of %s" %
			(obj.name, id, ", ".join(vals)))
	return fun

def type_penum(cls):
	"""Type support for a Python enumeration."""
	map = { normalize(x.name): x for x in cls }
	def convert(self, val, obj):
		try:
			return map[normalize(val).strip()]
		except KeyError:
			raise CheckError(f"{val} in {obj.name} must be one of {', '.join([normalize(x.name) for x in cls])}")
	return convert

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

def type_percent(self, val, obj):
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


FONT_WITH_ERROR = set()

def type_font(self, val, obj):
	"""Convert val to a font. Display a warning if the
	font does not exists and returns None."""
	val = ptah.util.normalize(val).strip()
	font = ptah.font.find(val)
	if font is not None:
		return font
	else:
		if val not in FONT_WITH_ERROR:
			FONT_WITH_ERROR.add(val)
		CONSOLE.warn(f"cannot find font {val} in {obj.name}! Reverting to default.")
		return None


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


class Map:
	"""Property map with a parent.."""

	def __init__(self, parent = None):
		self.props = {}
		self.parent = parent
		if parent is not None:
			parent.add_item(self)

	def get_location(self):
		"""Get the location of the map."""
		return "unknown"

	def get_parent(self):
		"""Get the parent containe of property."""
		return self.parent

	def get_props_map(self):
		"""Get the map of supported properties."""
		return {}

	def set_prop(self, prop, val):
		"""Add a property to the map."""
		self.props[prop] = val

	def get_prop(self, prop, required=False, direct=False, default=None):
		"""Look for a property value. If the property is not found, returns
		default value if not required, also raises an util.CheckError.
		If direct is false, just look in the current map. Otherwise look also
		in the parents."""
		try:
			return self.props[prop]
		except KeyError:
			if direct:
				val = None
			elif self.parent is not None:
				val = self.parent.get_prop(prop)
			else:
				val = None
			if val is not None:
				return val
			elif required:
				traceback.print_stack(file=sys.stdout)
				raise CheckError(f"{prop.id} has to be defined in {self.get_location()}")
			else:
				return default

	def parse_prop(self, key, val, mon):
		"""Parse a single property."""
		try:
			prop = self.get_props_map()[key]
			val = prop.parse(val, self)
			self.set_prop(prop, val)
		except KeyError:
			mon.print_warning(f"no property {key} in {self.get_location()}. Ignoring it.")

	def parse(self, data, mon):
		"""Parse the given data, a dictionary of (key, value) and built
		corresponding properties. All error displayed on monitor mon."""

		for (key, val) in data.items():
			p = key.find('#')

			if p < 0:
				self.parse_prop(key, val, mon)

			else:
				id = key[:p]
				try:
					i = int(key[p+1:]) - 1
					item = self.get_item(i)
					item.parse_prop(id, val, mon)
				except ValueError:
					mon.print_warning(f"bad number in {key} of {self.get_location()}. Ignoring it.")

		# check the properties
		self.check(mon)

	def check(self, mon):
		"""Function that may be called to perform additional check after parsing.
		The default implementation does nothing. May raise a CheckError
		if an error is found."""
		pass

	def init_prop(self, prop):
		"""Initialize a property from a property map."""
		val = self.get_prop(prop)
		if val is not None:
			self.__dict__[prop.pid] = val

	def init_props(self, props):
		"""Initialize the properties from the provided map."""
		for prop in props:
			self.init_prop(prop)

	def copy_props(self, target, props):
		"""Copy the properties inside the current object to the target."""
		for prop in props:
			if prop in self.props:
				target.set_prop(prop, self.props[prop])


class Container(Map):
	"""Class that may contain sub-objects."""

	def __init__(self, parent = None):
		Map.__init__(self, parent)
		self.parent = parent
		self.content = []

	def get_content(self):
		return self.content

	def get_item(self, i):
		return self.content[i]

	def add_item(self, item):
		"""Add an item to the container and returns it."""
		self.content.append(item)
		return item

	def remove_item(self, item):
		"""Remove an item from the container."""
		self.content.remove(item)

	#def check(self, mon):
	#	Map.check(self, mon)
	#	for item in self.content:
	#		item.check(mon)


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
