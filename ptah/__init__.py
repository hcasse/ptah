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

	def __init__(self, page, name=None):
		Map.__init__(self, page)
		self.box = None
		self.initialized = False
		if name is None:
			self.name = "no name"
		else:
			self.name = name

	def get_location(self):
		return f"{self.name} in {self.get_parent().get_location()}"

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

	def declare(self, drawer):
		"""Called to declare resources used by the frame.
		Default implementation performs property initialization
		with self.STYLE_PROPS."""
		self.init()

	def init(self):
		if not self.initialized:
			self.initialized = True
			self.init_props(self.STYLE_PROPS)

class Image(Frame, graph.Style):
	"""Frame displaying an image."""

	STYLE_PROPS = [
		MODE_PROP,
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
	PROPS = [IMAGE_PROP] + STYLE_PROPS
	MAP = props.make(PROPS)

	def __init__(self, page, required=True, name=None):
		Frame.__init__(self, page, name=name)
		graph.Style.__init__(self)
		self.image = None
		self.required = required

	def check(self, mon):
		self.image = self.get_prop(IMAGE_PROP, direct=True, required=self.required)

	def gen(self, drawer):
		if self.image is not None:
			drawer.draw_image(self.image, self.box, self)

	def declare(self, drawer):
		self.init()
		if self.border_style != BorderStyle.NONE:
			if self.border_color is not None:
				drawer.declare_color(self.border_color)
		if self.shadow != Shadow.NONE:
			if self.shadow_color is not None:
				drawer.declare_color(self.shadow_color)


class Text(Frame, graph.TextStyle):
	"""Frame displaying a text."""

	STYLE_PROPS = [
		TEXT_ALIGN_PROP,
		FONT_SIZE_PROP,
		FONT_PROP
	]
	PROPS = [ TEXT_PROP ] + STYLE_PROPS
	MAP = props.make(PROPS)

	def __init__(self, page, required=False, name=None):
		Frame.__init__(self, page, name=name)
		graph.TextStyle.__init__(self)
		self.text = None
		self.required = required

	def check(self, mon):
		self.text = self.get_prop(TEXT_PROP, direct=True, required=self.required)
		self.init_props(self.STYLE_PROPS)

	def gen(self, drawer):
		if self.text is not None:
			drawer.draw_text(self.text, self.box, self)


class Page(Container, graph.PageStyle):
	"""A page in the created album."""

	STYLE_PROPS = [
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
		BACKGROUND_MODE_PROP,
	]
	PROPS = [
		NAME_PROP,
		Property("type", "Type of page.", lambda prop, val, obj: None)
	] + STYLE_PROPS

	NAME = ""
	MAP = props.make(PROPS)

	def __init__(self, album):
		Container.__init__(self, album)
		graph.PageStyle.__init__(self)
		self.name = "<no name>"
		self.number = None

	def get_location(self):
		return f"{self.name}:{self.number + 1}"

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
		self.map(drawer)
		for frame in self.content:
			frame.gen(drawer)
		pass

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
		for frame in self.content:
			frame.declare(drawer)

	def check(self, mon):
		self.name = self.get_prop(NAME_PROP, default=self.name, direct=True)
		self.init_props(self.STYLE_PROPS)
		for frame in self.get_content():
			frame.check(mon)


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
		try:
			page.name = desc["name"]
		except KeyError:
			pass
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

	FORMAT_PROP = props.Property("format", "page format", type_format)
	PAGES_PROP = props.Property("pages", "list of pages", type_pages)
	TITLE_PROP = props.StringProperty("title", "Album title.")
	AUTHOR_PROP = props.StringProperty("author", "Author name.")
	DATE_PROP = props.StringProperty("date", "Edition date.")
	PATHS_PROP = props.Property("paths", "list of paths to find images", type_paths)
	PROPS = props.make([
		FORMAT_PROP,
		PAGES_PROP,
		TITLE_PROP,
		AUTHOR_PROP,
		DATE_PROP,
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
		PATHS_PROP
	])
	MAP = props.make(PROPS)

	def __init__(self, path):
		Container.__init__(self)
		self.path = path
		self.pages = None
		self.base = os.path.dirname(path)
		self.name = os.path.basename(path)
		self.format = format.A4
		self.title = None
		self.author = None
		self.date = None
		self.background_color = None
		self.background_image = None
		self.paths = None

	def get_location(self):
		return f"album {self.name}"

	def get_props_map(self):
		return self.MAP

	def get_base(self):
		return self.base

	def get_title(self):
		if self.title is None:
			self.title = self.get_prop(self.TITLE_PROP)
			if self.title is None:
				self.title = self.name.splitext()[0]
		return self.title

	def get_author(self):
		if self.author is None:
			self.author = self.get_prop(self.AUTHOR_PROP)
		return self.author

	def get_date(self):
		if self.date is None:
			self.date = self.get_prop(self.DATE_PROP)
		return self.date

	def read(self, mon):
		"""Read the album from the file."""
		try:
			with open(self.path) as file:
				desc = yaml.safe_load(file)
				self.parse(desc, mon)
		except yaml.YAMLError as e:
			raise util.CheckError(str(e))

	def check(self, mon):
		self.pages = self.get_prop(self.PAGES_PROP, direct=True, required=True)
		self.format = self.get_prop(self.FORMAT_PROP, default=self.format, direct=True)
		self.title = self.get_prop(self.TITLE_PROP, default=self.title, direct=True)
		self.author = self.get_prop(self.AUTHOR_PROP, default=self.author, direct=True)
		self.date = self.get_prop(self.DATE_PROP, default=self.date, direct=True)

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
