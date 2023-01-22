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

	def gen(self, drawer):
		"""Generate the page on the given output file."""
		pass

	def get_props(self):
		"""Get properties for reading the page description."""
		return {}

	def get_packages(self):
		"""Get the packages used by this page."""
		return set()


class Drawer:
	"""Handler for drawing content of a page. Position and sizes are
	expressed in millimeters."""

	def __init__(self, album):
		self.album = album
		self.format = album.format
		self.width = self.format.body_width()
		self.height = self.format.body_height()

	def draw_image(self, path, x, y, w, h):
		pass

	def draw_text(self, text, x, y, w, h):
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

	def get_packages(self):
		return set(["tikz"])

	def gen(self, drawer):
		drawer.draw_image(
			self.image,
			0, 0,
			drawer.width, drawer.height
		)


"""Known pages."""
PAGE_MAP = {
	"center": CenterPage
}
