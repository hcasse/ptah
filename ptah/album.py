#
#	Ptah -- Photo album generator
#	Copyright (C) 2022 Hugues Cassé <hug.casse@gmail.com>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Representation of the album."""

import os
import yaml

from ptah import format
from ptah import graph
from ptah import io
from ptah import util
from ptah.props import StringProperty, Property, Map, Container, make, parse_color
from ptah.gprops import *

NAME_PROP = StringProperty("name", "name")

def check_dict(data, context):
	"""Check if data are a dictionary. Raises an exception if it is not the cas
	in the passed context (implementation of props.Map)."""
	if not isinstance(data, dict):
		raise CheckError(f"{context.get_location()} data should a be a map!")

def is_dict(data):
	"""Check if data is a dictionary."""
	return isinstance(data, dict)

def is_iterable(data):
	"""Test if data is iterable."""
	try:
		return callable(data.__iter__)
	except AttributeError:
		return false

def setup_style(name, obj, mon):
	style = obj.get_album().get_style(name)
	if style is None:
		mon.print_warning(f"unknown style {name} in {obj.get_location()}")
	else:
		style.copy_props(obj, Style.PROPS)

def parse_style(self, data, obj, mon):
	"""Parse a style property."""
	setup_style(str(data), obj, mon)

STYLE_PROP = Property("style", "apply the named style to the current object", parse_style)

def parse_styles(self, data, obj, mon):
	"""Parse a list of styles."""
	if not is_iterable(data):
		mon.print_warning(f"styles must have a list of style names in {obj.get_location()}")
	for item in data:
		setup_style(str(item), obj, mon)

STYLES_PROP = Property("styles", "apply the named styles to the current object (space separated)", parse_styles)


class Frame(Map):
	"""A frame inside a page with content."""

	PROPS = [
		STYLE_PROP,
		STYLES_PROP
	]

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
	PROPS = [IMAGE_PROP] + STYLE_PROPS + Frame.PROPS
	MAP = make(PROPS)

	def __init__(self, page, required=True, name=None):
		Frame.__init__(self, page, name=name)
		graph.Style.__init__(self)
		self.image = None
		self.required = required

	def check(self, mon):
		self.image = self.get_prop(IMAGE_PROP, direct=True)
		if self.image is None:
			self.image = self.get_parent().get_prop(IMAGE_PROP, direct=True)
		if self.image is None:
			mon.print_error(f"image in {self.get_location()} is required!")

	def gen(self, drawer):
		if self.image is not None:
			drawer.draw_image(self.image, self.box, self)

	def declare(self, drawer):
		self.init()
		graph.Style.check(self, None)
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
		TEXT_COLOR_PROP,
		FONT_SIZE_PROP,
		FONT_PROP
	]
	PROPS = [ TEXT_PROP ] + STYLE_PROPS + Frame.PROPS
	MAP = make(PROPS)

	def __init__(self, page, required=False, name=None):
		Frame.__init__(self, page, name=name)
		graph.TextStyle.__init__(self)
		self.text = None
		self.required = required

	def check(self, mon):
		self.text = self.get_prop(TEXT_PROP, direct=True)
		if self.text is None:
			self.text = self.get_parent().get_prop(TEXT_PROP, direct=True, required=self.required)
		self.init_props(self.STYLE_PROPS)

	def gen(self, drawer):
		if self.text is not None:
			drawer.draw_text(self.text, self.box, self)

	def declare(self, drawer):
		self.init()
		if self.text_color is not None:
				drawer.declare_color(self.text_color)


class Page(Container, graph.PageStyle):
	"""A page in the created album."""

	STYLE_PROPS = [
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
		BACKGROUND_MODE_PROP,
	]
	PROPS = [
		NAME_PROP,
		Property("type", "Type of page.", lambda prop, val, obj, mon: None),
		STYLE_PROP,
		STYLES_PROP
	] + STYLE_PROPS

	NAME = ""
	MAP = make(PROPS)

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


def parse_pages(self, pages, album, mon):
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
			page = util.PAGE_MAP[type](album)
		except KeyError:
			mon.print_error(f"page type {type} is unknown! Ignoring it!")
			continue

		# initialize the page
		page.number = len(res)
		try:
			page.name = desc["name"]
		except KeyError:
			pass
		res.append(page)
		page.parse(desc, mon)

	return res


def parse_paths(self, paths, album, mon):
	"""Supports paths of the album."""
	if not hasattr(paths, "__iter__") \
	or not all([isinstance(x, str) for x in paths]):
		mon.print_error("paths should a be a list of paths!")
		return None
	else:
		album.set_paths(paths)
		return paths


def parse_format(self, fmt, album, mon):
	try:
		return format.FORMATS[fmt.upper()]
	except KeyError:
		mon.print_error(f"format {fmt} is unknown! Reverting to A4.")

def parse_default(self, data, album, mon):
	"""Convert the content of default entry."""
	check_dict(data, self)
	album.get_default().parse(data, mon)
	return album.get_default()

def parse_declare_styles(self, content, album, mon):
	if not is_iterable(content):
		mon.print_error("styles at top-level must contain a list of styles!")
	for item in content:
		if not is_dict(item):
			mon.print_error("a style must be a collection of definitions!")
			continue
		try:
			name = str(item["name"])
		except KeyError:
			mon.print_error("a style must have a name!")
			continue
		style = Style(name)
		style.parse(item, io.DEF)
		album.add_style(style)

def parse_colors(self, content, album, mon):
	"""Parse the definition of colors."""
	if not is_dict(content):
		mon.print_error("colors must be a list of color definitions!")
		return
	for (key, val) in content.items():
		pseudo = Property(key, "defined color", parse_color)
		try:
			color = parse_color(pseudo, val, album, mon)
			album.add_color(key, color)
		except util.CheckError as e:
			mon.print_error(f"bad color {key}: {val}: {e}.")
			continue

class Album(Container):
	"""The album itself, mainly an ordered collection of pages."""

	FORMAT_PROP = Property("format", "page format", parse_format)
	PAGES_PROP = Property("pages", "list of pages", parse_pages)
	TITLE_PROP = StringProperty("title", "Album title.")
	AUTHOR_PROP = StringProperty("author", "Author name.")
	DATE_PROP = StringProperty("date", "Edition date.")
	PATHS_PROP = Property("paths", "list of paths to find images", parse_paths)
	DEFAULT_PROP = Property("default", "default properties the rest of the album", parse_default)
	DECLARE_STYLES_PROP = Property("styles", "styles usable in the rest of the album", parse_declare_styles)
	COLORS_PROP = Property("colors", "named colors usable in the rest of the album", parse_colors)
	STYLE_PROPS = [
		BACKGROUND_COLOR_PROP,
		BACKGROUND_IMAGE_PROP,
	]
	PROPS = make([
		FORMAT_PROP,
		PAGES_PROP,
		TITLE_PROP,
		AUTHOR_PROP,
		DATE_PROP,
		PATHS_PROP,
		DEFAULT_PROP,
		DECLARE_STYLES_PROP,
		COLORS_PROP
	], STYLE_PROPS)
	MAP = make(PROPS)

	def __init__(self, path):
		default = Default()
		Container.__init__(self, default)
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
		self.paths = [self.base]
		self.default = default
		self.styles = {}
		self.colors = {}

	def get_album(self):
		return self

	def add_style(self, style):
		"""Add a style to the album."""
		self.styles[style.name] = style

	def get_style(self, name):
		"""Get a style by its name. Return None if not found."""
		try:
			return self.styles[name]
		except KeyError:
			return None

	def add_color(self, name, color):
		"""Declare a named color."""
		self.colors[name] = color

	def get_color(self, name):
		"""Get a color by its name. Return None if not declared."""
		try:
			color = self.colors[name]
		except KeyError:
			color = None
		return color

	def get_default(self):
		"""Get the album default container."""
		return self.default

	def set_paths(self, paths):
		"""Set the paths used to retrieve resources like images."""
		self.paths = [os.path.join(self.base, path) for path in paths]

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
		except (yaml.YAMLError, UnicodeDecodeError) as e:
			raise util.CheckError(str(e))
		except FileNotFoundError:
			raise util.CheckError(f"cannot open {self.path}!")

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


class Default(Container):
	"""Default property container."""

	PROPS = Page.STYLE_PROPS + Image.STYLE_PROPS + Text.STYLE_PROPS
	MAP = make(PROPS)

	def __init__(self):
		Container.__init__(self)

	def get_props_map(self):
		return self.MAP

	def get_location(self):
		return "default"


class Style(Map):
	"""A collection of properties that may be applied to another element like
	page or frames."""

	PROPS = Page.STYLE_PROPS + Image.STYLE_PROPS + Text.STYLE_PROPS
	MAP = make(PROPS, NAME_PROP)

	def __init__(self, name):
		Map.__init__(self)
		self.name = name

	def get_location(self):
		return f"style {self.name}"

	def get_props_map(self):
		return self.MAP

