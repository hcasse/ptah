"""Management of properties for pages and album."""

import os
import ptah
from ptah.util import CheckError

class Property:
	"""Property to describe a page or an album."""

	def __init__(self, id, desc, req = False, multi = False):
		self.id = id
		self.pid = id.replace("-", "_")
		self.desc = desc
		self.req = req
		self.multi = multi

	def parse(self, text, obj):
		"""Parse the given text and return the corresponding text.
		Raises CheckError if the text is not valid."""
		return text

	def set(self, val, obj):
		"""Parse the file value and set it, if valid, to the object
		corresponding field. The default implementation performs
		the assignment to the field without test. May raise
		CheckError if the value is not valid."""
		if self.multi:
			raise CheckError("property %s must be indexed #i in %s." %
				(self.id, obj.name))
		obj.__dict__[self.pid] = self.parse(val, obj)

	def is_indexed(self):
		"""Test if the property supports indexes."""
		return self.multi

	def set_indexed(self, i, val, obj):
		"""Same as parse() but with an array. In addition, may raise
		CheckError if the index is too big."""
		if not self.multi:
			raise CheckError("property %s is not indexed in %s." %
				(self.id, obj.name))
		l = obj.__dict__[self.pid]
		if i < 0 or i >= len(l):
			raise CheckError("property %s#%d with bad index in %s." %
				(self.id, i, obj.name))
		l[i] = self.parse(val, obj)

	def check(self, obj):
		"""Check if the property is correctly set in the object."""
		if not self.req:
			return
		if not self.multi:
			if obj.__dict__[self.pid] == None:
				raise CheckError("property %s is required for %s!" %
					(self.id, obj.name))
		else:
			l = obj.__dict__[self.pid]
			for i in range(0, len(l)):
				if l[i] == None:
					raise CheckError("property %s#%d is required for %s!" %
						(self.id, i+1, obj.name))

	def get_description(self):
		"""Get the description of the property."""
		return self.desc


class ImageProperty(Property):
	"""Property to pass an image."""

	def __init__(self, id, desc, req = True, multi = False):
		Property.__init__(self, id, desc, req, multi)

	def parse(self, path, page):
		if not os.path.exists(os.path.join(page.album.get_base(), path)):
			raise CheckError("no image on path '%s' for %s" %
				(path, page.name))
		return path


class EnumProperty(Property):
	"""A value from an enumeration."""

	def __init__(self, id, desc, vals, req = False, multi = False):
		Property.__init__(self, id, desc, req, multi)
		self.vals = vals

	def parse(self, val, obj):
		val = val.lower()
		for i in range(0, len(self.vals)):
			if val == self.vals[i]:
				return i
		raise CheckError("in %s, %s must be one of %s" %
			(obj.name, id, ", ".join(self.vals)))

	def get_description(self):
		return "one of " + ", ".join(self.vals) + ": " + \
			Property.get_description(self)


class StringProperty(Property):
	"""Simple string property."""

	def __init__(self, id, desc, req = False):
		Property.__init__(self, id, desc, req)


HTML_COLORS = {
	"lightsalmon": "#FFA07A",
	"salmon": "#FA8072",
	"darksalmon": "#E9967A",
	"lightcoral": "#F08080",
	"indianred": "#CD5C5C",
	"crimson": "#DC143C",
	"firebrick": "#B22222",
	"red": "#FF0000",
	"darkred": "#8B0000",
	"coral": "#FF7F50",
	"tomato": "#FF6347",
	"orangered": "#FF4500",
	"gold": "#FFD700",
	"orange": "#FFA500",
	"darkorange": "#FF8C00",
	"lightyellow": "#FFFFE0",
	"lemonchiffon": "#FFFACD",
	"lightgoldenrodyellow": "#FAFAD2",
	"papayawhip": "#FFEFD5",
	"moccasin": "#FFE4B5",
	"peachpuff": "#FFDAB9",
	"palegoldenrod": "#EEE8AA",
	"khaki": "#F0E68C",
	"darkkhaki": "#BDB76B",
	"yellow": "#FFFF00",
	"lawngreen": "#7CFC00",
	"chartreuse": "#7FFF00",
	"limegreen": "#32CD32",
	"lime": "#00FF00",
	"forestgreen": "#228B22",
	"green": "#008000",
	"darkgreen": "#006400",
	"greenyellow": "#ADFF2F",
	"yellowgreen": "#9ACD32",
	"springgreen": "#00FF7F",
	"mediumspringgreen": "#00FA9A",
	"lightgreen": "#90EE90",
	"palegreen": "#98FB98",
	"darkseagreen": "#8FBC8F",
	"mediumseagreen": "#3CB371",
	"seagreen": "#2E8B57",
	"olive": "#808000",
	"darkolivegreen": "#556B2F",
	"olivedrab": "#6B8E23",
	"lightcyan": "#E0FFFF",
	"cyan": "#00FFFF",
	"aqua": "#00FFFF",
	"aquamarine": "#7FFFD4",
	"mediumaquamarine": "#66CDAA",
	"paleturquoise": "#AFEEEE",
	"turquoise": "#40E0D0",
	"mediumturquoise": "#48D1CC",
	"darkturquoise": "#00CED1",
	"lightseagreen": "#20B2AA",
	"cadetblue": "#5F9EA0",
	"darkcyan": "#008B8B",
	"teal": "#008080",
	"powderblue": "#B0E0E6",
	"lightblue": "#ADD8E6",
	"lightskyblue": "#87CEFA",
	"skyblue": "#87CEEB",
	"deepskyblue": "#00BFFF",
	"lightsteelblue": "#B0C4DE",
	"dodgerblue": "#1E90FF",
	"cornflowerblue": "#6495ED",
	"steelblue": "#4682B4",
	"royalblue": "#4169E1",
	"blue": "#0000FF",
	"mediumblue": "#0000CD",
	"darkblue": "#00008B",
	"navy": "#000080",
	"midnightblue": "#191970",
	"mediumslateblue": "#7B68EE",
	"slateblue": "#6A5ACD",
	"darkslateblue": "#483D8B",
	"lavender": "#E6E6FA",
	"thistle": "#D8BFD8",
	"plum": "#DDA0DD",
	"violet": "#EE82EE",
	"orchid": "#DA70D6",
	"fuchsia": "#FF00FF",
	"magenta": "#FF00FF",
	"mediumorchid": "#BA55D3",
	"mediumpurple": "#9370DB",
	"blueviolet": "#8A2BE2",
	"darkviolet": "#9400D3",
	"darkorchid": "#9932CC",
	"darkmagenta": "#8B008B",
	"purple": "#800080",
	"indigo": "#4B0082",
	"pink": "#FFC0CB",
	"lightpink": "#FFB6C1",
	"hotpink": "#FF69B4",
	"deeppink": "#FF1493",
	"palevioletred": "#DB7093",
	"mediumvioletred": "#C71585",
	"white": "#FFFFFF",
	"snow": "#FFFAFA",
	"honeydew": "#F0FFF0",
	"mintcream": "#F5FFFA",
	"azure": "#F0FFFF",
	"aliceblue": "#F0F8FF",
	"ghostwhite": "#F8F8FF",
	"whitesmoke": "#F5F5F5",
	"seashell": "#FFF5EE",
	"beige": "#F5F5DC",
	"oldlace": "#FDF5E6",
	"floralwhite": "#FFFAF0",
	"ivory": "#FFFFF0",
	"antiquewhite": "#FAEBD7",
	"linen": "#FAF0E6",
	"lavenderblush": "#FFF0F5",
	"mistyrose": "#FFE4E1",
	"gainsboro": "#DCDCDC",
	"lightgray": "#D3D3D3",
	"silver": "#C0C0C0",
	"darkgray": "#A9A9A9",
	"gray": "#808080",
	"dimgray": "#696969",
	"lightslategray": "#778899",
	"slategray": "#708090",
	"darkslategray": "#2F4F4F",
	"black": "#000000",
	"cornsilk": "#FFF8DC",
	"blanchedalmond": "#FFEBCD",
	"bisque": "#FFE4C4",
	"navajowhite": "#FFDEAD",
	"wheat": "#F5DEB3",
	"burlywood": "#DEB887",
	"tan": "#D2B48C",
	"rosybrown": "#BC8F8F",
	"sandybrown": "#F4A460",
	"goldenrod": "#DAA520",
	"peru": "#CD853F",
	"chocolate": "#D2691E",
	"saddlebrown": "#8B4513",
	"sienna": "#A0522D",
	"brown": "#A52A2A",
	"maroon": "#800000",
}

class ColorProperty(Property):

	def __init__(self, id, desc):
		Property.__init__(self, id, desc)

	def parse(self, col, obj):
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
				return HTML_COLORS[col]
			except KeyError:
				pass
		raise CheckError("%s: bad color in %s!" % (self.id, obj.name))

	def get_description(self):
		return "named color or HTML color \\#RRGGBB."


def make(props):
	"""Build a property map."""
	return { prop.id: prop for prop in props }

"""Known pages."""
PAGE_MAP = {
}
