"""Basic collection of pages."""

import os
import ptah
from ptah import Page
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
	PROPS = props.make(
		Page.PROPS,
		Page.TEXT_PROPS,
		Page.IMAGE_PROPS,
		props.BoolProperty("inside", "insert text inside image.")
	)

	def __init__(self):
		Page.__init__(self)
		self.init_image()
		self.init_text()
		self.inside = False

	def get_props(self):
		return CenterPage.PROPS

	def gen(self, drawer):
		if self.text != None and self.inside == False:
			h = drawer.height - 12
		else:
			h = drawer.height
		drawer.draw_image(
			self.image,
			Box(0, 0, drawer.width, h),
			Style(self)
		)
		if self.text != None:
			drawer.draw_text(
				self.text,
				Box(0, drawer.height - 10, drawer.width, 10),
				TextStyle(self)
			)

	def gen_miniature(drawer):
		h = drawer.height - 5
		drawer.draw_miniature_image("image", Box(0, 0, drawer.width, h))
		drawer.draw_miniature_text("text", Box(0, h+2, drawer.width, 3))


# Duo page
class DuoPage(Page):

	NAME = "duo"
	PROPS = props.make(
		Page.PROPS,
		Page.IMAGE_PROPS,
		PROP_ORIENTATION
	)

	def __init__(self):
		Page.__init__(self)
		self.init_image(2)
		self.orientation = 0

	def get_props(self):
		return DuoPage.PROPS

	def gen(self, drawer):
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
		drawer.draw_image(
			self.image[0],
			Box(x1, y1, w, h),
			Style(self, 0)
		)
		drawer.draw_image(
			self.image[1],
			Box(x2, y2, w, h),
			Style(self, 1)
		)

	def gen_miniature(drawer):
		h = (drawer.height - 2)/2.
		drawer.draw_miniature_image("image1", Box(0, 0, drawer.width, h))
		drawer.draw_miniature_image("image1", Box(0, h+2, drawer.width, h))


# Text page
class OnlyTextPage(Page):

	NAME = "only-text"
	PROPS = props.make(
		Page.PROPS,
		Page.TEXT_PROPS
	)

	def __init__(self):
		Page.__init__(self)
		self.init_text()
		self.pad = graph.AbsLength(10)

	def get_props(self):
		return OnlyTextPage.PROPS

	def gen(self, drawer):
		pad = self.pad.get(min(drawer.width, drawer.height))
		drawer.draw_text(
			self.text,
			Box(pad, pad, drawer.width - 2*pad, drawer.height - 2*pad),
			TextStyle(self)
		)

	def gen_miniature(drawer):
		drawer.draw_miniature_text("text",
			Box(1, 1, drawer.width - 2, drawer.height - 2)
		)
		

# Page initialization
def add(cls):
	ptah.PAGE_MAP[cls.NAME] = cls
add(CenterPage)
add(DuoPage)
add(OnlyTextPage)
