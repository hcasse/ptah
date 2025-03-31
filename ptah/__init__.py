"""Ptah is a utility to generate photo album. This is the main library."""

from enum import Enum
import os
import os.path
import yaml
from ptah import format
from ptah import props
from ptah.props import Property
from ptah import util
from ptah.graph import Style

def enum_list(cls):
	"""Return a string representing the list of enumerated values."""
	return ", ".join([util.normalize(x.name) for x in cls])

# property management

PROP_OK = 0
PROP_REQ = 1
PROP_INH = 2

class Mode(Enum):
	"""Filling mode for an image."""
	FIT = 0
	STRETCH = 1
	FILL = 2
	TILE = 3	# only for background

class Align(Enum):
	"""Alignments."""
	CENTER = 0
	TOP = 1
	TOP_RIGHT = 2
	RIGHT = 3
	BOTTOM_RIGHT = 4
	BOTTOM = 5
	BOTTOM_LEFT = 6
	LEFT = 7
	TOP_LEFT = 8

class FontSize(Enum):
	"""Enumeration of font sizes."""
	XX_SMALL = 0
	X_SMALL = 1
	SMALL = 2
	MEDIUM = 3
	LARGE = 4
	X_LARGE = 5
	XX_LARGE = 6

class BorderWidth(Enum):
	"""Enumeration of symbolic border widths."""
	THIN = 0
	MEDIUM = 1
	THICK = 2

border_width_type = props.type_union([
	props.type_penum(BorderWidth),
	props.type_length
])

class BorderStyle(Enum):
	"""Enumeration of border styles."""
	NONE = 0
	SOLID = 1
	DOTTED = 2
	DASHED = 3
	DOUBLE = 4
border_style_type = props.type_penum(BorderStyle)

class Shadow(Enum):
	"""Enumeration of shadow types."""
	NONE = 0
	SIMPLE = 1
	FUZZY = 2
shadow_type = props.type_penum(Shadow)


# background properties
BACKGROUND_COLOR_PROP = props.ColorProperty(
	"background-color", "Color for background.", mode = PROP_INH)
BACKGROUND_IMAGE_PROP = props.ImageProperty(
	"background-image", "background image", mode = PROP_INH)
BACKGROUND_MODE_PROP = Property("background-mode",
	"Background image mode.", props.type_penum(Mode))

# image properties
MODE_PROP = Property(
	"mode",
	f"image mode, one of {enum_list(Mode)}.",
	props.type_penum(Mode),
	default = Mode.FIT)
ALIGN_PROP = Property(
	"align",
	f"image alignment, one of {enum_list(Align)}",
	props.type_penum(Align),
	default = Align.CENTER)
IMAGE_PROP = props.ImageProperty("image", "image", mode = PROP_REQ)
NAME_PROP = props.StringProperty("name", "name")
SCALE_PROP = Property(
	"scale",
	"image scale.",
	props.type_float,
	default = 1.)
HORIZONTAL_SHIFT_PROP = Property(
	"horizontal-shift",
	"shift in % of the image width.",
	props.type_length)
VERTICAL_SHIFT_PROP = Property(
	"vertical-shift",
	"shift in % of the image height.",
	props.type_length)

# text properties
TEXT_ALIGN_PROP = Property("text-align", f"Text alignment among {enum_list(Align)}.", props.type_penum(Align))
TEXT_PROP = props.StringProperty("text", "Page text.")
FONT_SIZE_PROP = props.Property("font-size", "font size.", props.type_penum(FontSize))
FONT_PROP = props.Property("font", "font name", props.type_font)

# border properties
BORDER_STYLE = props.Property(
	"border-style",
	"Style for the border.",
	border_style_type,
	default = BorderStyle.NONE
)
BORDER_COLOR = props.Property(
	"border-color",
	"Color for border of an image.",
	props.type_color,
	mode = PROP_INH,
	default = "#000000",
	implies = props.implies_set(BORDER_STYLE, BorderStyle.NONE, BorderStyle.SOLID))
BORDER_WIDTH = props.Property(
	"border-width",
	f"width of border lines: length or one of {enum_list(BorderWidth)}.",
	border_width_type,
	mode = PROP_INH,
	default = BorderWidth.MEDIUM,
	implies = props.implies_set(BORDER_STYLE, BorderStyle.NONE, BorderStyle.SOLID))

# shadow properties
SHADOW_STYLE = props.Property(
	"shadow",
	f"select the shadow type among {enum_list(Shadow)}.",
	shadow_type,
	mode = PROP_INH,
	default = Shadow.NONE)
SHADOW_XOFFSET = props.Property(
	"shadow-xoffset",
	"shadow horizontal offset.",
	props.type_length,
	mode = PROP_INH,
	default = 1.5)
SHADOW_YOFFSET = props.Property(
	"shadow-yoffset",
	"shadow vertical offset.",
	props.type_length,
	mode = PROP_INH,
	default = 1.5)
SHADOW_COLOR = props.Property(
	"shadow-color",
	"shadow color.",
	props.type_color,
	mode = PROP_INH,
	default = "#000000")
SHADOW_OPACITY = props.Property(
	"shadow-opacity",
	"shadow opacity as percent value (100% opaque, 0% transparent).",
	props.type_percent,
	mode = PROP_INH)

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
		VERTICAL_SHIFT_PROP,
		BORDER_STYLE,
		BORDER_WIDTH,
		BORDER_COLOR,
		SHADOW_STYLE,
		SHADOW_XOFFSET,
		SHADOW_YOFFSET,
		SHADOW_OPACITY,
		SHADOW_COLOR
	]

	TEXT_PROPS = [
		TEXT_PROP,
		TEXT_ALIGN_PROP,
		FONT_SIZE_PROP,
		FONT_PROP
	]

	NAME = ""
	PROPS = props.make(PAGE_PROPS)

	def __init__(self):
		util.AttrMap.__init__(self)
		props.Container.__init__(self)
		self.number = None
		self.name = ""
		self.init_page()
		self.image_count = 0
		self.text_count = 0

	def init_page(self):
		"""Initialize the page properties."""
		self.background_color = None
		self.background_image = None
		self.background_mode = Mode.STRETCH

	def init_image(self, n = 1):
		"""Initialize the image count and their properties."""
		self.image_count = n
		for p in Page.IMAGE_PROPS:
			p.init(self, n)

	def init_text(self, n  = 1):
		"""Initialize the text count and their properties."""
		self.text_count = 0
		if n == 1:
			self.text = None
			self.text_align = Align.CENTER
			self.font_size = FontSize.MEDIUM
			self.font = None
		else:
			self.text = [None] * n
			self.text_align =  [Align.CENTER] * n
			self.font_size =  [FontSize.MEDIUM] * n
			self.font = [None] * n

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
		if self.image_count == 1:
			drawer.declare_color(self.border_color)
			drawer.declare_color(self.shadow_color)
		elif self.image_count > 1:
			for c in self.border_color:
				drawer.declare_color(c)
			for c in self.shadow_color:
				drawer.declare_color(c)


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
			raise util.CheckError("page type %s is unknown!" % type)

		# initialize the page
		page.album = album
		page.set_parent(album)
		page.number = len(res)
		res.append(page)
		util.parse_dict(desc, page, page.get_props())

	return res


def type_paths(self, paths, album):
	"""Supports paths of the album."""
	if not hasattr(paths, "__iter__") \
	or not all([isinstance(x, str) for x in paths]):
		raise CheckError("paths should a be a list of paths!")
	return paths


def type_format(self, fmt, album):
	try:
		return format.FORMATS[fmt.upper()]
	except KeyError:
		raise util.CheckError(self, "format %s is unknown" % fmt)


class Album(util.AttrMap, props.Container):
	"""The album itself, mainly an ordered collection of pages."""

	PROPS = props.make([
		props.Property("format", "page format", type_format),
		props.Property("pages", "list of pages", type_pages, mode = PROP_REQ),
		props.StringProperty("title", "Album title."),
		props.StringProperty("author", "Author name."),
		props.StringProperty("date", "Edition date."),
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
		props.Property("paths", "list of paths to find images", type_paths)
	])

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
		self.paths = ['.']
		for p in Page.IMAGE_PROPS:
			p.init(self, 1, is_root = True)

	def get_base(self):
		return self.base

	def add_page(self, page):
		page.album = self
		page.number = len(self.pages)
		self.pages.append(page)

	def read(self, mon):
		"""Read the album from the file."""
		try:
			with open(self.path) as file:
				desc = yaml.safe_load(file)
				util.parse_dict(desc, self, self.PROPS)
			return True
		except yaml.YAMLError as e:
			raise util.CheckError(str(e))

	def find(self, file):
		"""Look for a file in the execution paths.
		Return None if the file cannot be found."""
		if os.path.isabs(file):
			return file
		else:
			for path in self.paths:
				jpath = os.path.join(path, file)
				if os.path.exists(jpath):
					return jpath
			return None


"""Map of page types."""
PAGE_MAP = {}
