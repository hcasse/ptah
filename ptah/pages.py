"""Basic collection of pages."""

import os
import ptah
from ptah import util
from ptah import props
from ptah.graph import *

PROP_ORIENTATION = props.EnumProperty(
	"orientation", "orientation", ["vertical", "horizontal"])
TEXT_PROP = props.StringProperty("text", "Page text.")
MINIATURE_BACK = "yellow!50!white"



def add(props, prop):
	props[prop.id] = prop

# Center page
class CenterPage(ptah.Page):

	NAME = "center"
	PROPS = props.make(ptah.PAGE_PROPS + [
		TEXT_PROP,
		ptah.TEXT_ALIGN_PROP
	])

	def __init__(self):
		ptah.Page.__init__(self)
		self.text = None
		self.text_align = ptah.TEXT_ALIGN_CENTER

	def get_props(self):
		return CenterPage.PROPS

	def gen(self, drawer):
		if self.text != None:
			h = drawer.height - 12
		else:
			h = drawer.height
		drawer.draw_image(
			self.image,
			Box(0, 0, drawer.width, h),
			self.get_style()
		)
		if self.text != None:
			drawer.draw_text(
				self.text,
				Box(0, h + 2, drawer.width, 10),
				TextStyle(self)
			)

	def gen_miniature(drawer):
		h = drawer.height - 5
		drawer.draw_miniature_image("image", Box(0, 0, drawer.width, h))
		drawer.draw_miniature_text("text", Box(0, h+2, drawer.width, 3))


# Duo page
class DuoPage(ptah.Page):

	NAME = "duo"
	PROPS = props.make(ptah.PAGE_PROPS + [PROP_ORIENTATION])

	def __init__(self):
		ptah.Page.__init__(self, 2)
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
			self.get_style(0)
		)
		drawer.draw_image(
			self.image[1],
			Box(x2, y2, w, h),
			self.get_style(1)
		)

	def gen_miniature(drawer):
		h = (drawer.height - 2)/2.
		drawer.draw_miniature_image("image1", Box(0, 0, drawer.width, h))
		drawer.draw_miniature_image("image1", Box(0, h+2, drawer.width, h))


# Page initialization
def add(cls):
	ptah.PAGE_MAP[cls.NAME] = cls
add(CenterPage)
add(DuoPage)
