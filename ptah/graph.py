"""Module managing graphics."""

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

	def __init__(self, obj, i = None):
		if i == None:
			self.mode = obj.mode
			self.scale = obj.scale
			self.align = obj.align
			self.xshift = obj.horizontal_shift
			self.yshift = obj.vertical_shift
			self.border_style = obj.border_style
			self.border_width = obj.border_width
			self.border_color = obj.border_color
		else:
			self.mode = obj.mode[i]
			self.scale = obj.scale[i]
			self.align = obj.align[i]
			self.xshift = obj.horizontal_shift[i]
			self.yshift = obj.vertical_shift[i]
			self.border_style = obj.border_style[i]
			self.border_width = obj.border_width[i]
			self.border_color = obj.border_color[i]


class TextStyle:

	def __init__(self, obj, i = None):
		if i == None:
			self.text_align = obj.text_align
			self.font_size = obj.font_size
		else:
			self.text_align = obj.text_align[i]
			self.font_size = obj.font_size[i]


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
