"""Ptah is a utility to generate photo album. This is the main library."""

import os
import yaml
from ptah import format
from ptah import props
from ptah import util
from ptah.graph import Style

MODE_FIT = 0
MODE_STRETCH = 1
MODE_FILL = 2

ALIGN_CENTER = 0
ALIGN_TOP = 1
ALIGN_TOP_RIGHT = 2
ALIGN_RIGHT = 3
ALIGN_BOTTOM_RIGHT = 4
ALIGN_BOTTOM = 5
ALIGN_BOTTOM_LEFT = 6
ALIGN_LEFT = 7
ALIGN_TOP_LEFT = 8

BACKGROUND_COLOR_PROP = props.ColorProperty("background-color", "Color for background.")
MODE_PROP = props.EnumProperty("mode", "image mode",
	[ "fit", "stretch", "fill"  ])
ALIGN_PROP = props.EnumProperty("align", "image alignment",
	[ "center", "top", "top-right", "right", "bottom-right",
	  "bottom", "bottom-left", "left", "top-left"])
IMAGE_PROP = props.ImageProperty("image", "image", req = True)
NAME_PROP = props.StringProperty("name", "name")
SCALE_PROP = props.FloatProperty("scale", "image scale")
HORIZONTAL_SHIFT_PROP = props.FloatProperty("horizontal-shift",
	"shift in % of the image width")
VERTICAL_SHIFT_PROP = props.FloatProperty("vertical-shift",
	"shift in % of the image height")

PAGE_PROPS = [
	BACKGROUND_COLOR_PROP,
	MODE_PROP,
	IMAGE_PROP,
	NAME_PROP,
	SCALE_PROP,
	ALIGN_PROP,
	HORIZONTAL_SHIFT_PROP,
	VERTICAL_SHIFT_PROP
]


class Page(util.AttrMap):
	"""A page in the created album."""

	NAME = ""
	PROPS = {}

	def __init__(self, n = 1):
		util.AttrMap.__init__(self)
		self.number = None
		self.background_color = None
		self.name = ""
		if n == 1:
			self.image = None
			self.mode = MODE_FIT
			self.scale = 1.
			self.align = ALIGN_CENTER
			self.horizontal_shift = None
			self.vertical_shift = None
		else:
			self.image = [None] * n
			self.mode = [MODE_FIT] * n
			self.scale = [1.] * n
			self.align = [ALIGN_CENTER] * n
			self.horizontal_shift = [None] * n
			self.vertical_shift = [None] * n

	def get_style(self, i = -1):
		if i == -1:
			return Style(
				mode = self.mode,
				scale = self.scale,
				align = self.align,
				xshift = self.horizontal_shift,
				yshift = self.vertical_shift)
		else:
			return Style(
				mode = self.mode[i],
				scale = self.scale[i],
				align = self.align[i],
				xshift = self.horizontal_shift[i],
				yshift = self.vertical_shift[i])

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
		self.name = "album"
		self.path = path
		self.pages = None
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
