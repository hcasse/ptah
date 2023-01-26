"""Ptah is a utility to generate photo album. This is the main library."""

import os
import yaml
from ptah import format
from ptah import props
from ptah import util


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

	def declare_color(self, color):
		"""Called to declare a color during the declaration phase."""
		pass


BACKGROUND_COLOR_PROP = props.ColorProperty("background-color", "Color for background.")

PAGE_PROPS = [
	BACKGROUND_COLOR_PROP
]


class Page(util.AttrMap):
	"""A page in the created album."""

	NAME = ""
	PROPS = {}

	def __init__(self):
		util.AttrMap.__init__(self)
		self.number = None
		self.background_color = None

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

	def declare(self, drawer):
		"""Called to declare usd resource in the declaration phase."""
		if self.background_color != None:
			drawer.declare_color(self.background_color)


class PagesProp(props.Property):

	def __init__(self):
		props.Property.__init__(self, "pages", "list of pages", req = True)

	def parse(self, pages, album):
		if not hasattr(pages, "__iter__"):
			raise CheckError("pages should a be a list of pages!")
		res = []
		for desc in pages:

			# get the page type
			try:
				type = desc["type"]
			except KeyError as e:
				type = "center"

			# make the page
			try:
				page = PAGE_MAP[type]()
			except KeyError:
				raise CheckError("page type %s is unknown!" % type)

			# initialize the page
			page.album = album
			page.number = len(res)
			res.append(page)
			util.parse_dict(desc, page, page.get_props())
		return res


class FormatProp(props.Property):

	def __init__(self):
		props.Property.__init__(self, "format", "page format", req = True)

	def parse(self, fmt, album):
		try:
			return format.FORMATS[fmt.upper()]
		except KeyError:
			raise util.CheckError(self, "format %s is unknown" % fmt)


ALBUM_PROPS = props.make([
	FormatProp(),
	PagesProp(),
	props.StringProperty("title", "Album title."),
	props.StringProperty("author", "Author name."),
	props.StringProperty("date", "Edition date."),
	BACKGROUND_COLOR_PROP
])

class Album(util.AttrMap):
	"""The album itself, mainly an ordered collection of pages."""

	def __init__(self, path):
		util.AttrMap.__init__(self)
		self.path = path
		self.pages = []
		self.base = os.path.dirname(path)
		self.format = format.A4
		self.title = "no title"
		self.author = None
		self.date = None
		self.background_color = None

	def get_base(self):
		return self.base

	def add_page(self, page):
		page.album = self
		page.number = len(self.pages)
		self.pages.append(page)

	def read(self, mon):
		try:
			with open(self.path) as file:
				desc = yaml.safe_load(file)
				util.parse_dict(desc, self, ALBUM_PROPS)
			return True
		except yaml.YAMLError as e:
			raise CheckError(str(e))





"""Map of page types."""
PAGE_MAP = {}
