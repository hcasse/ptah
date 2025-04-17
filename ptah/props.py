#
#	Ptah -- Photo album generator
#	Copyright (C) 2022 Hugues Cassé <hug.casse@gmail.com>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Management of properties for pages and album.

Parsing function for properties takes the following parameters: (prop, data, props, monitor)
where:
* prop - property itself
* data - data,
* props - properties to augment,
* monitor - monitor to display error message.

Props must implement a location for the error message.
"""

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

	def parse(self, val, obj, mon):
		"""Parse the given text and return the corresponding text.
		Display an error or raises CheckError if the text is not valid."""
		return self.fun(self, val, obj, mon)

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

	def get_description(self):
		"""Get the description of the property."""
		return self.desc


def parse_float(self, val, obj, mon):
	try:
		return float(val)
	except ValueError:
		raise CheckError(f"value {self.id} of {obj.get_location()} should be a floatting-pointer number")


LENGTH_RE = re.compile("([+-]?[0-9\.]?)([a-zA-Z]+)")

LENGTH_UNITS = {
	"mm": 1,
	"cm": 10,
	"dm": 100,
	"in": 25.4,
	"pt": 0.3514598
}

def parse_string(self, val, obj, mon):
	return str(val)

def parse_image(self, path, page, mon):
	actual_path = page.get_album().find(path)
	if actual_path is None:
		raise CheckError(f"image {path} in {page.get_location()} cannot be found!")
	return actual_path

def parse_penum(cls):
	"""Type support for a Python enumeration."""
	map = { normalize(x.name): x for x in cls }
	def convert(self, val, obj, mon):
		try:
			return map[normalize(val).strip()]
		except KeyError:
			raise CheckError(f"{val} in {obj.name} must be one of {', '.join([normalize(x.name) for x in cls])}")
	return convert

def parse_color(self, col, obj, mon):
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
			color = obj.get_album().get_color(col)
			if color is not None:
				return color
			else:
				try:
					return graph.HTML_COLORS[col]
				except KeyError:
					pass
	raise CheckError(f"{self.id}: bad color in {obj.get_location()}!")

def parse_length(self, val, obj, mon):
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
	raise CheckError(f"bad length for {self.id} in {obj.get_location()}")

def parse_bool(self, val, obj, mon):
	if val == False or val == True:
		return val
	else:
		raise CheckError(f"bad boolean value for {self.id} in {obj.get_location()}.")

def parse_union(parsers):
	"""Join several parsers"""
	def fun(self, val, obj, mon):
		for parser in parsers:
			try:
				return parser(self, val, obj, mon)
			except CheckError:
				pass
		raise CheckError(f"cannot parse {self.id} in {obj.get_location()}")
	return fun

def parse_percent(self, val, obj, mon):
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
	raise CheckError(f"cannot parse value {val} for {self.id} in {obj.get_location()}")


FONT_WITH_ERROR = set()

def parse_font(self, val, obj, mon):
	"""Convert val to a font. Display a warning if the
	font does not exists and returns None."""
	val = ptah.util.normalize(val).strip()
	font = ptah.font.find(val)
	if font is not None:
		return font
	else:
		if val not in FONT_WITH_ERROR:
			FONT_WITH_ERROR.add(val)
		raise CheckError(f"cannot find font {val} in {obj.get_location()}! Reverting to default.")


# For compatibility
def ImageProperty(id, desc, mode = 1):
	return Property(id, desc, parse_image, mode)
def StringProperty(id, desc, mode = 0):
	return Property(id, desc, parse_string, mode)
def FloatProperty(id, desc, mode = 0):
	return Property(id, desc, parse_float, mode)
def ColorProperty(id, desc, mode = 0):
	return Property(id, desc, parse_color, mode)
def LengthProperty(id, desc, mode = 0):
	return Property(id, desc, parse_length, mode)
def BoolProperty(id, desc, mode = 0):
	return Property(id, desc, parse_bool, mode)


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
				#traceback.print_stack(file=sys.stdout)
				raise CheckError(f"{prop.id} has to be defined in {self.get_location()}")
			else:
				return default

	def parse_prop(self, key, val, mon):
		"""Parse a single property."""
		try:
			prop = self.get_props_map()[key]
			val = prop.parse(val, self, mon)
			self.set_prop(prop, val)
		except KeyError:
			mon.print_warning(f"no property {key} in {self.get_location()}. Ignoring it.")
		except CheckError as e:
			mon.print_error(f"bad value {val} for {key} in {self.get_location()}: {e}. Value must be {prop.desc}.")

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
