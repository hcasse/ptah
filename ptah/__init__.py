"""Ptah is a utility to generate photo album. This is the main library."""

import os
import yaml
from ptah import format
from ptah import props
from ptah import util
from ptah.graph import Style

# property management

PROP_OK = 0
PROP_REQ = 1
PROP_INH = 2

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

FONT_SIZE_XX_SMALL = 0
FONT_SIZE_X_SMALL = 1
FONT_SIZE_SMALL = 2
FONT_SIZE_MEDIUM = 3
FONT_SIZE_LARGE = 4
FONT_SIZE_X_LARGE = 5
FONT_SIZE_XX_LARGE = 6
FONT_SIZE_SMALLER = 7
FONT_SIZE_LARGER = 8

ALIGNMENTS = [
	"center",
	"top",
	"top-right",
	"right",
	"bottom-right",
	"bottom",
	"bottom-left",
	"left",
	"top-left"
]

BACKGROUND_COLOR_PROP = props.ColorProperty(
	"background-color", "Color for background.", mode = PROP_INH)
BACKGROUND_IMAGE_PROP = props.ImageProperty(
	"background-image", "background image", mode = PROP_INH)
BACKGROUND_MODE_PROP = props.EnumProperty("background-mode",
	"Background image mode.", [ "fit", "stretch", "fill" ])
MODE_PROP = props.EnumProperty("mode", "image mode",
	[ "fit", "stretch", "fill" ])
ALIGN_PROP = props.EnumProperty("align", "image alignment", ALIGNMENTS)
IMAGE_PROP = props.ImageProperty("image", "image", mode = PROP_REQ)
NAME_PROP = props.StringProperty("name", "name")
SCALE_PROP = props.FloatProperty("scale", "image scale")
HORIZONTAL_SHIFT_PROP = props.LengthProperty("horizontal-shift",
	"shift in % of the image width")
VERTICAL_SHIFT_PROP = props.LengthProperty("vertical-shift",
	"shift in % of the image height")
TEXT_ALIGN_PROP = props.EnumProperty("text-align", "Text alignment.", ALIGNMENTS)
TEXT_PROP = props.StringProperty("text", "Page text.")
FONT_SIZE_PROP = props.Property("font-size", "font size.", props.type_enum([
	"xx-small", "x-small", "small",
	"medium",
	"large", "x-large", "xx-large",
	"smaller", "larger"
]))

class Page(util.AttrMap, props.Container):
	"""A page in the created album."""

	PAGE_PROPS = [
		NAME_PROP,
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
		BACKGROUND_MODE_PROP
	]

	IMAGE_PROPS = [
		MODE_PROP,
		IMAGE_PROP,
		SCALE_PROP,
		ALIGN_PROP,
		HORIZONTAL_SHIFT_PROP,
		VERTICAL_SHIFT_PROP
	]

	TEXT_PROPS = [
		TEXT_PROP,
		TEXT_ALIGN_PROP,
		FONT_SIZE_PROP
	]

	NAME = ""
	PROPS = props.make(PAGE_PROPS)

	def __init__(self):
		util.AttrMap.__init__(self)
		props.Container.__init__(self)
		self.number = None
		self.name = ""
		self.init_page()

	def init_page(self):
		self.background_color = None
		self.background_image = None
		self.background_mode = MODE_STRETCH

	def init_image(self, n = 1):
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
	
	def init_text(self, n  = 1):
		if n == 1:
			self.text = None
			self.text_align = ALIGN_CENTER
			self.font_size = FONT_SIZE_MEDIUM
		else:
			self.text = [None] * n
			self.text_align =  [ALIGN_CENTER] * n
			self.font_size =  [FONT_SIZE_MEDIUM] * n
			

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


def type_pages(self, pages, album):
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
		page.set_parent(album)
		page.number = len(res)
		res.append(page)
		util.parse_dict(desc, page, page.get_props())

	return res


def type_format(self, fmt, album):
	try:
		return format.FORMATS[fmt.upper()]
	except KeyError:
		raise util.CheckError(self, "format %s is unknown" % fmt)


ALBUM_PROPS = props.make([
	props.Property("format", "page format", type_format),
	props.Property("pages", "list of pages", type_pages, mode = PROP_REQ),
	props.StringProperty("title", "Album title."),
	props.StringProperty("author", "Author name."),
	props.StringProperty("date", "Edition date."),
	BACKGROUND_COLOR_PROP,
	BACKGROUND_IMAGE_PROP
])

class Album(util.AttrMap, props.Container):
	"""The album itself, mainly an ordered collection of pages."""

	def __init__(self, path):
		util.AttrMap.__init__(self)
		props.Container.__init__(self)
		self.name = "album"
		self.path = path
		self.pages = None
		self.base = os.path.dirname(path)
		self.format = format.A4
		self.title = "no title"
		self.author = None
		self.date = None
		self.background_color = None
		self.background_image = None

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
