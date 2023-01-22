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
		top_margin = None, oddside_margin = None
	):
		self.name = name
		self.width = width
		self.height = height
		self.top_margin = select(top_margin, margin)
		self.oddside_margin = select(oddside_margin, margin)

	def landscape(self):
		return Format(
			"A4-landscape",
			width = self.height,
			height = self.width,
			margin = self.margin,
			top_margin = self.oddside_margin,
			oddsize_margin = self.top_margin
		)

	def duplicate(self, name):
		f = Format(
			name, self.width, self.height, self.width, self.margin,
			self.top_margin, self.oddsize_margin
		)

	def gen_geometry(self, out, recto):
		"""Generate the geometry generation for the current format."""
		out.write("paperwidth = %smm,\n" % self.width)
		out.write("paperheight = %smm,\n" % self.height)
		out.write("top = %smm,\n" % self.top_margin)
		out.write("left = %smm" % self.oddside_margin)

A4 = Format("A4", 210, 297, top_margin = 19, oddside_margin = 19)

FORMATS = {
	A4.name: A4
}
DEFAULT = A4
