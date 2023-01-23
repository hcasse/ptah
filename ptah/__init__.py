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

	NAME = ""
	PROPS = {}

	def __init__(self):
		util.AttrMap.__init__(self)
		self.number = None

	def check(self):
		"""Function called to check the attributes when the page is loaded.
		Raise CheckError if there is an error."""
		pass

	def gen(self, drawer):
		"""Generate the page on the given output file."""
		pass

	def get_props(self):
		"""Get properties for reading the page description."""
		return {}

	def get_packages(self):
		"""Get the packages used by this page."""
		return set()

	def gen_miniature(drawer):
		"""Called to generate the miniature when the documentation is
		called."""
		pass


class Drawer:
	"""Handler for drawing content of a page. Position and sizes are
	expressed in millimeters."""

	def __init__(self, album):
		self.album = album
		self.format = album.format
		self.width = self.format.body_width()
		self.height = self.format.body_height()
		self.sep = self.format.column_sep

	def draw_image(self, path, x, y, w, h):
		pass

	def draw_text(self, x, y, w, h, text):
		pass


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





"""Known pages."""
PAGE_MAP = {
}
