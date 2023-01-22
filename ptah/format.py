"""Format description. Dimensions are expressed in mm."""

from ptah import util

def select(x, y):
	if x == None:
		return y
	else:
		return x

class Format:

	def __init__(self,
		name, width, height, margin = 10,
		top_margin = None, bottom_margin = None,
		oddside_margin = None, evenside_margin = None,
		column_sep = 5
	):
		self.name = name
		self.width = width
		self.height = height
		self.top_margin = select(top_margin, margin)
		self.bottom_margin = select(bottom_margin, margin)
		self.oddside_margin = select(oddside_margin, margin)
		self.evenside_margin = select(evenside_margin, margin)
		self.column_sep = column_sep

	def landscape(self):
		return Format(
			"%s-landscape" % self.name,
			width = self.height,
			height = self.width,
			margin = self.margin,
			top_margin = self.oddside_margin,
			bottom_margin = self.evenside_margin,
			oddside_margin = self.top_margin,
			evenside_margin = self.bottom_margin,
			column_sep = self.column_sep
		)

	def duplicate(self, name):
		f = Format(
			name, self.width, self.height, self.width, self.margin,
			self.top_margin, self.bottom_margin,
			self.oddsize_margin, self.evenside_margin,
			self.column_sep
		)

	def body_width(self):
		return self.width - self.oddside_margin - self.evenside_margin

	def body_height(self):
		return self.height - self.top_margin - self.bottom_margin
	

A4 = Format("A4", 210, 297,
	top_margin = 19, bottom_margin = 36.7,
	oddside_margin = 19, evenside_margin = 13.2,
	column_sep = 5
)

FORMATS = {
	A4.name: A4
}
DEFAULT = A4
