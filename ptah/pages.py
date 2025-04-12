"""Basic collection of pages."""

import os
import ptah
from ptah.album import Page, Text, Image
from ptah import graph
from ptah import util
from ptah import props
from ptah.graph import *

PROP_ORIENTATION = props.EnumProperty(
	"orientation", "orientation", ["vertical", "horizontal"])
MINIATURE_BACK = "yellow!50!white"


def add(props, prop):
	props[prop.id] = prop


# Center page
class CenterPage(Page):

	NAME = "center"
	INSIDE_PROP = props.BoolProperty("inside", "insert text inside image.")
	PROPS = Page.PROPS + Text.PROPS + Image.PROPS + [INSIDE_PROP]
	MAP = props.make(PROPS)

	def __init__(self, album):
		Page.__init__(self, album)
		self.inside = False
		self.image = Image(self)
		self.text = Text(self)

	def get_props_map(self):
		return self.MAP

	def check(self, mon):
		Page.check(self, mon)
		self.inside = self.get_prop(self.INSIDE_PROP, direct=True, default=self.inside)

	def map(self, drawer):
		if self.text.text is not None and self.inside == False:
			h = drawer.height - 12
		else:
			h = drawer.height
		self.image.map(Box(0, 0, drawer.width, h))
		if self.text.text is not None:
			self.text.map(Box(0, drawer.height - 10, drawer.width, 10))

	def gen_miniature(drawer):
		h = drawer.height - 5
		drawer.draw_miniature_image("image", Box(0, 0, drawer.width, h))
		drawer.draw_miniature_text("text", Box(0, h+2, drawer.width, 3))


# Duo page
class DuoPage(Page):

	NAME = "duo"
	PROPS = Page.PROPS + Image.PROPS + [PROP_ORIENTATION]
	MAP = props.make(PROPS)

	def __init__(self, album):
		Page.__init__(self, album)
		self.orientation = 0
		self.image1 = Image(self, name="image1")
		self.image2 = Image(self, name="image2")

	def get_props_map(self):
		return self.MAP

	def check(self, mon):
		Page.check(self, mon)
		self.orientation = self.get_prop(PROP_ORIENTATION, direct=True, default=self.orientation)

	def map(self, drawer):
		if self.orientation == 0:
			h = (drawer.height - drawer.sep) / 2
			x1 = 0
			y1 = 0
			x2 = 0
			y2 = h + drawer.sep
			w = drawer.width
		else:
			w = (drawer.width - drawer.sep) / 2
			x1 = 0
			y1 = 0
			x2 = w + drawer.sep
			y2 = 0
			h = drawer.height
		self.image1.map(Box(x1, y1, w, h))
		self.image2.map(Box(x2, y2, w, h))

	def gen_miniature(drawer):
		h = (drawer.height - 2)/2.
		drawer.draw_miniature_image("image1", Box(0, 0, drawer.width, h))
		drawer.draw_miniature_image("image2", Box(0, h+2, drawer.width, h))


# Trio page
class TrioPage(Page):

	NAME = "trio"
	PROPS = Page.PROPS + Image.PROPS + [PROP_ORIENTATION]
	MAP = props.make(PROPS)

	def __init__(self, album):
		Page.__init__(self, album)
		self.image1 = Image(self)
		self.image2 = Image(self)
		self.image3 = Image(self)
		self.orientation = 0

	def get_props_map(self):
		return self.MAP

	def check(self, mon):
		Page.check(self, mon)
		self.orientation = self.get_prop(PROP_ORIENTATION, direct=True, default=self.orientation)

	def map(self, drawer):
		x, y = [0] * 3, [0] * 3
		if self.orientation == 0:
			h = (drawer.height - 2*drawer.sep) / 3
			w = drawer.width
			y[1] = h + drawer.sep
			y[2] = 2*h + 2*drawer.sep
		else:
			w = (drawer.width - 2*drawer.sep) / 3
			h = drawer.height
			x[1] = w + drawer.sep
			x[2] = 2*w + 2*drawer.sep
		for i in range(0, 3):
			self.get_item(i).map(Box(x[i], y[i], w, h))
			self.get_item(i).gen(drawer)

	def gen_miniature(drawer):
		w, h = drawer.width, (drawer.height - 4)/3.
		y = 0
		for i in range(0, 3):
			drawer.draw_miniature_image("image%d" % i, Box(0, y, w, h))
			y += h + 2


# Text page
class OnlyTextPage(Page):

	NAME = "only-text"
	PROPS = Page.PROPS + Text.PROPS
	MAP = props.make(PROPS)

	def __init__(self, album):
		Page.__init__(self, album)
		self.pad = graph.AbsLength(10)
		self.text_frame = Text(self)

	def check(self, mon):
		Page.check(self, mon)

	def get_props_map(self):
		return self.MAP

	def map(self, drawer):
		pad = self.pad.get(min(drawer.width, drawer.height))
		self.text_frame.map(Box(pad, pad, drawer.width - 2*pad, drawer.height - 2*pad))

	def gen_miniature(drawer):
		drawer.draw_miniature_text("text",
			Box(1, 1, drawer.width - 2, drawer.height - 2)
		)


# Blank page
class BlankPage(Page):

	NAME = "blank"
	MAP = props.make(Page.PROPS)

	def __init__(self, album):
		Page.__init__(self, album)

	def get_props_map(self):
		return self.MAP


# Title page
class TitlePage(Page):

	NAME = "title"
	MAP = props.make(Page.PROPS, Text.PROPS)

	def __init__(self, album):
		Page.__init__(self, album)
		self.title_left = .15
		self.title_right = .15
		self.title_bot = .4
		self.title = Text(self)
		self.date = Text(self)
		self.author = Text(self)
		self.other_height = 8
		self.interspace = 5

	def get_props_map(self):
		return self.MAP

	def check(self, mon):
		Page.check(self, mon)
		if self.title.text is None:
			self.title.text = self.get_album().get_title()
		if self.author.text is None:
			self.author.text = self.get_album().get_author()
		if self.date.text is None:
			self.date.text = self.get_album().get_date()

	def gen(self, drawer):
		x = drawer.width * self.title_left
		w = drawer.width - x - drawer.width * self.title_right
		h = drawer.height * self.title_bot
		y = 0
		self.title.map(Box(x, y, w, h))
		self.title.gen(drawer)
		y += h + self.interspace
		if self.get_album().date != None:
			self.date.map(Box(x, y, w, self.other_height))
			self.date.gen(drawer)
			y += self.other_height + self.interspace
		if self.get_album().author != None:
			self.author.map(Box(x, y, w, self.other_height))
			self.author.gen(drawer)

	def gen_miniature(drawer):
		ht = drawer.height / 4
		hd = 5
		ha = 5
		w = drawer.width - 6
		y = 3
		drawer.draw_miniature_text("title\\#1", Box(3, 3, w, ht))
		y += ht + 1
		drawer.draw_miniature_text("date\\#2", Box(3, y, w, hd))
		y += hd + 1
		drawer.draw_miniature_text("author\\#3", Box(3, y, w, ha))


# Page initialization

"""Known pages."""
def add(cls):
	util.PAGE_MAP[cls.NAME] = cls
add(TitlePage)
add(CenterPage)
add(DuoPage)
add(OnlyTextPage)
add(BlankPage)
add(TrioPage)
