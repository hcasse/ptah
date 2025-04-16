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

"""Module managing graphics."""

from enum import Enum

class Mode(Enum):
	"""Filling mode for an image."""
	FIT = 0
	STRETCH = 1
	FILL = 2
	TILE = 3	# only for background

class Align(Enum):
	"""Alignments."""
	CENTER = 0
	TOP = 1
	TOP_RIGHT = 2
	RIGHT = 3
	BOTTOM_RIGHT = 4
	BOTTOM = 5
	BOTTOM_LEFT = 6
	LEFT = 7
	TOP_LEFT = 8

class FontSize(Enum):
	"""Enumeration of font sizes."""
	XX_SMALL = 0
	X_SMALL = 1
	SMALL = 2
	MEDIUM = 3
	LARGE = 4
	X_LARGE = 5
	XX_LARGE = 6

class BorderWidth(Enum):
	"""Enumeration of symbolic border widths."""
	THIN = 0
	MEDIUM = 1
	THICK = 2

class BorderStyle(Enum):
	"""Enumeration of border styles."""
	NONE = 0
	SOLID = 1
	DOTTED = 2
	DASHED = 3
	DOUBLE = 4

class Shadow(Enum):
	"""Enumeration of shadow types."""
	NONE = 0
	SIMPLE = 1
	FUZZY = 2

class Length:
	"""Represent a length - absolute in mm or proportional in %."""

	def get(self, ref):
		return 0

class AbsLength(Length):
	"""Represents an absolute length in mm."""

	def __init__(self, val):
		self.val = val

	def get(self, ref):
		return self.val

	def __str__(self):
		return str(self.val)

class PropLength(Length):
	"""Represents a length as proportional value between [0, 1]."""

	def __init__(self, val):
		self.val = val

	def get(self, ref):
		return ref * self.val

	def __str__(self):
		return str(self.val) + "%"


class Point:

	def __init__(self, x, y):
		self.x = x
		self.y = y


class Box:

	def __init__(self, x, y, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def copy(self):
		return Box(self.x, self.y, self.w, self.h)

	def centerx(self):
		return  self.x + self.w/2.

	def centery(self):
		return self.y + self.h/2.

	def scale(self, fact):
		self.w = self.w * fact
		self.h = self.h * fact

	def scale_center(self, fact):
		cx, cy = self.centerx(), self.centery()
		self.scale(fact)
		self.x = cx - self.w/2
		self.y = cy - self.h/2

	def align_left(self, x):
		self.x = self.x + (x - self.x - self.w)

	def align_right(self, x):
		self.x = self.x + (x - self.x)

	def align_top(self, y):
		self.y = self.y + (y - self.y - self.h)

	def align_bottom(self, y):
		self.y = self.y + (y - self.y)

	def offsetx(self, rx):
		return rx * w

	def offsety(self, ry):
		return ry * h


class Style:

	def __init__(self):
		self.mode = Mode.FIT
		self.scale = 1.
		self.align = Align.CENTER
		self.horizontal_shift = AbsLength(0)
		self.vertical_shift = AbsLength(0)
		self.border_style = BorderStyle.NONE
		self.border_width = None
		self.border_color = None
		self.shadow = Shadow.NONE
		self.shadow_xoffset = 1.5
		self.shadow_yoffset = 1.5
		self.shadow_color = "#000000"
		self.shadow_opacity = None

	def check(self, mon):
		if self.shadow_opacity is None:
			if self.shadow == Shadow.SIMPLE:
				self.shadow_opacity = .5
			elif self.shadow == Shadow.FUZZY:
				self.shadow_opacity = 1.
		if (self.border_color is not None or self.border_width is not None) \
		and self.border_style is BorderStyle.NONE:
			self.border_style = BorderStyle.SOLID
		if self.border_style is not BorderStyle.NONE:
			if self.border_color is None:
				self.border_color = "#000000"
			if self.border_width is None:
				self.border_width = BorderWidth.MEDIUM


class TextStyle:

	def __init__(self):
		self.text_align = Align.CENTER
		self.font_size = FontSize.MEDIUM
		self.font = None


class PageStyle:
	"""Style for a page."""

	def __init__(self):
		self.background_color = None
		self.background_image = None
		self.background_mode = Mode.FIT


class Drawer:
	"""Handler for drawing content of a page. Position and sizes are
	expressed in millimeters."""

	def __init__(self, album):
		self.album = album
		self.format = album.format
		self.width = self.format.body_width()
		self.height = self.format.body_height()
		self.page_width = self.format.width
		self.page_height = self.format.height
		self.sep = self.format.column_sep

	def draw_image(self, path, box, style):
		"""Draw an image from the given path in the given box with the
		given style."""
		pass

	def draw_text(self, text, box, style):
		pass

	def declare_color(self, color):
		"""Called to declare a color during the declaration phase."""
		pass

	def draw_miniature_image(self, label, box):
		"""Draw image for miniature output."""
		pass

	def draw_miniature_text(self, bel, box):
		"""Draw text for miniature output."""
		pass


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
