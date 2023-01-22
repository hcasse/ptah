"""Ptah is a utility to generate photo album. This is the main library."""

import os.path

from ptah import format
from ptah import util
from string import Template

# Common attributes
IMAGE = "image"
MARGIN = "margin"
MARGIN_TOP = "margin-top"
MARGIN_BOTTOM = "margin-bottom"
MARGIN_LEFT = "margin-left"
MARGIN_RIGHT = "margin-right"

class Page(util.AttrMap):
	"""A page in the created album."""

	def __init__(self):
		util.AttrMap.__init__(self)
		self.album = None
		self.number = None

	def check(self):
		"""Function called to check the attributes when the page is loaded.
		Raise CheckError if there is an error."""
		pass

	def gen(self, out):
		"""Generate the page on the given output file."""
		pass

	def get_props(self):
		"""Get properties for reading the page description."""
		return {}


class Album(util.AttrMap):
	"""The album itself, mainly an ordered collection of pages."""

	def __init__(self, path):
		util.AttrMap.__init__(self)
		self.path = path
		self.pages = []
		self.base = os.path.dirname(path)
		self.format = format.A4

	def get_base(self):
		return self.base

	def add_page(self, page):
		page.album = self
		page.number = len(self.pages)
		self.pages.append(page)

	def gen(self):
		"""Generate the latex file. Return the file name."""
		root, ext = os.path.splitext(self.path)
		out_path = root + ".tex"
		with open(out_path, "w") as out:

			# write prolog
			out.write("""
\\documentclass[a4paper]{book}
\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{geometry}
\\usepackage{layout}


\\title{}
\\author{}
\\date{\\today}

\\geometry{
""")

			self.format.gen_geometry(out, True)

			out.write("""
}

\\begin{document}
""")

			# write pages
			first = True
			for page in self.pages:
				if not first:
					first = False
				out.write("\\newpage\n")
				page.gen(out)

			# write epilog
			out.write("""
\\end{document}
""")

			# return output name
			return out_path


def get_image(path, page):
	if not os.path.exists(path):
		raise util.CheckError("no image on path '%s'" % path)
	page.image = path

PAGE_PROPS = {
	"image": get_image
}

class CenterPage(Page):

	def __init__(self):
		Page.__init__(self)
		self.image = None

	def check(self):
		if self.image == None:
			raise util.CheckError("no image provided")

	def get_props(self):
		return PAGE_PROPS

	def gen(self, out):
		out.write("""
\\vfill
\\noindent\\begin{center}
\\includegraphics[
	width=\\textwidth,
	height=\\textheight,
	keepaspectratio
]{%s}\end{center}
\\vfill""" % self.image)


"""Known pages."""
PAGE_MAP = {
	"center": CenterPage
}
