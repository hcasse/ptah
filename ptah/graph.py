"""Module managing graphics."""

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

	def __init__(self, mode,
		scale = None,
		align = 0,
		xshift = None,
		yshift = None
	):
		self.mode = mode
		self.scale = scale
		self.align = align
		self.xshift = xshift
		self.yshift = yshift
