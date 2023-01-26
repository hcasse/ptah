"""Basic collection of pages."""

import os
import ptah
from ptah import util
from ptah import props

MINIATURE_BACK = "yellow!50!white"

PROP_NAME = props.StringProperty("name", "name")
PROP_IMAGE = props.ImageProperty("image", "image", req = True)
PROP_IMAGES = props.ImageProperty("image", "image", req = True, multi = True)
PROP_ORIENTATION = props.EnumProperty(
	"orientation", "orientation", ["vertical", "horizontal"])

def add(props, prop):
	props[prop.id] = prop

# Center page
class CenterPage(ptah.Page):

	NAME = "center"
	PROPS = props.make(ptah.PAGE_PROPS + [PROP_NAME, PROP_IMAGE])

	def __init__(self):
		ptah.Page.__init__(self)
		self.image = None

	def get_props(self):
		return CenterPage.PROPS

	def gen(self, drawer):
		drawer.draw_image(
			self.image,
			0, 0,
			drawer.width, drawer.height
		)

	def gen_miniature(drawer):
		drawer.draw_box(
			0, 0,
			drawer.width, drawer.height,
			draw = "black",
			fill = MINIATURE_BACK
		)
		drawer.draw_text(
			0, 0,
			drawer.width, drawer.height,
			"image"
		)

# Duo page
class DuoPage(ptah.Page):

	NAME = "duo"
	PROPS = props.make(ptah.PAGE_PROPS + [
		PROP_NAME,
		PROP_IMAGES,
		PROP_ORIENTATION
	])

	def __init__(self):
		ptah.Page.__init__(self)
		self.image = [ None, None ]
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
		drawer.draw_image(self.image[0], x1, y1, w, h)
		drawer.draw_image(self.image[1], x2, y2, w, h)

	def gen_miniature(drawer):
		h = (drawer.height - 2)/2.
		drawer.draw_box(
			0, 0,
			drawer.width, h,
			draw = "black",
			fill = MINIATURE_BACK
		)
		drawer.draw_text(
			0, 0,
			drawer.width, h,
			"image1"
		)
		drawer.draw_box(
			0, h+2,
			drawer.width, h,
			draw = "black",
			fill = MINIATURE_BACK
		)
		drawer.draw_text(
			0, h+2,
			drawer.width, h,
			"image2"
		)


# Page initialization
def add(cls):
	ptah.PAGE_MAP[cls.NAME] = cls
add(CenterPage)
add(DuoPage)
