"""Management of properties for pages and album."""

import os
import ptah

class Property:
	"""Property to describe a page or an album."""

	def __init__(self, id, desc, req = False):
		self.id = id
		self.desc = desc
		self.req = req

	def parse(self, val, obj):
		"""Parse the file value and assign it, if valid, to the object
		corresponding field. The default implementation performs
		the assignment to the field without test."""
		obj.__dict__[self.id] = val

	def check(self, obj):
		"""Check if the property is correctly set in the object."""
		if self.req and obj.__dict__[self.id] == None:
			raise CheckError("property %s is required for %s" %
				(self.id, obj.name))

	def get_description(self):
		"""Get the description of the property."""
		return self.desc


class ImageProperty(Property):
	"""Property to pass an image."""

	def __init__(self, id, desc, req = True):
		Property.__init__(self, id, desc, req)

	def parse(self, path, page):
		if not os.path.exists(os.path.join(page.album.get_base(), path)):
			raise util.CheckError("no image on path '%s'" % path)
		Property.parse(self, path, page)


class EnumProperty(Property):
	"""A value from an enumeration."""

	def __init__(self, id, desc, vals, req = False):
		Property.__init__(self, id, desc, req)
		self.vals = vals

	def parse(self, val, obj):
		val = val.lower()
		for i in range(0, len(self.vals)):
			if val == self.vals[i]:
				Property.parse(self, i, obj)
				return
		raise util.CheckError("in %s, %s must be one of %s" %
			(obj.name, id, ", ".join(self.vals)))

	def get_description(self):
		return "one of " + ", ".join(self.vals) + ": " + \
			Property.get_description(self)


class StringProperty(Property):
	"""Simple string property."""

	def __init__(self, id, desc, req = False):
		Property.__init__(self, id, desc, req)


def make(props):
	"""Build a property map."""
	return { prop.id: prop for prop in props }
