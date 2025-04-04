"""Ptah is a utility to generate photo album. This is the main library."""

from enum import Enum
import os
import os.path
import yaml
from ptah import format
from ptah import props
from ptah.props import Property, Map, Container, StringProperty
from ptah import util
from ptah.graph import Style, Box
from ptah import io
from ptah.gprops import *

# property management

PROP_OK = 0
PROP_REQ = 1
PROP_INH = 2


NAME_PROP = StringProperty("name", "name")

class Frame(Map):
	"""A frame inside a page with content."""

	def __init__(self, page):
		Map.__init__(self, page)
		self.box = None

	def get_album(self):
		return self.get_page().get_album()

	def get_page(self):
		"""Get the page containing the frame."""
		return self.parent

	def get_props_map(self):
		return self.MAP

	def map(self, box):
		"""Map the frame."""
		self.box = box

	def gen(self, drawer):
		"""Generate the frame on the drawer."""
		pass


class Image(Frame):
	"""Frame displaying an image."""

	PROPS = [
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
	MAP = props.make(PROPS)

	def __init__(self, page, required=True):
		Frame.__init__(self, page)
		self.image = None
		self.required = required

	def check(self, mon):
		self.image = IMAGE_PROP.resolve(self, direct=True, required=self.required)

	def gen(self, drawer):
		if self.image is not None:
			drawer.draw_image(self.image, self.box, Style(self))


class Text(Frame):
	"""Frame displaying a text."""

	PROPS = [
		TEXT_PROP,
		TEXT_ALIGN_PROP,
		FONT_SIZE_PROP,
		FONT_PROP
	]
	MAPS = props.make(PROPS)

	def __init__(self, page, required=False):
		Frame.__init__(self, page)
		self.text = None
		self.required = required

	def check(self, mon):
		self.text = self.get_prop(TEXT_PROP, direct=True, required=self.required)

	def gen(self, drawer):
		if self.text is not None:
			drawer.draw_text(self.text, self.box, TextStyle(self))

	def init_style(self, style):
		style.text_align = self.get_prop(ALIGN_PROP, default=style.text_align)
		style.font_size = self.get_prop(FONT_SIZE_PROP, default=style.font_size)
		style.font = self.get_prop(FONT_PROP, default=style.font)


class Page(Container):
	"""A page in the created album."""

	PROPS = [
		NAME_PROP,
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
		BACKGROUND_MODE_PROP,
		Property("type", "Type of page.", lambda prop, val, obj: None)
	]

	NAME = ""
	MAP = props.make(PROPS)

	def __init__(self, album):
		Container.__init__(self, album)
		self.name = "<no name>"
		self.number = None
		self.image_count = 0
		self.text_count = 0

	def get_location(self):
		return f"{self.name}:{self.number}"

	def get_album(self):
		"""Get the album containing the page."""
		return self.parent

	def get_props_map(self):
		return self.MAP

	def map(self, drawer):
		"""Map the frames inside the page with actual size of the page."""
		pass

	def gen(self, drawer):
		"""Generate the page on the given output file."""
		for frame in self.content:
			self.gen(drawer)

	def get_props(self):
		"""Get properties for reading the page description."""
		return self.props

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
			page = PAGE_MAP[type](album)
		except KeyError:
			raise util.CheckError(f"page type {type} is unknown!")

		# initialize the page
		page.number = len(res)
		res.append(page)
		page.parse(desc, io.DEF)

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


class Album(Container):
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
	MAP = props.make(PROPS)

	def __init__(self, path):
		Container.__init__(self)
		self.path = path
		self.pages = None
		self.base = os.path.dirname(path)
		self.name = os.path.basename(path)
		self.format = format.A4
		self.title = "no title"
		self.author = None
		self.date = None
		self.background_color = None
		self.background_image = None
		self.paths = ['.']
		#for p in Image.PROPS:
		#	p.init(self, 1, is_root = True)

	def get_location(self):
		return f"album {self.name}"

	def get_props_map(self):
		return self.MAP

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
				self.parse(desc, mon)
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

PAGE_MAP = {
}
