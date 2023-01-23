"""Basic collection of pages."""

import os
import ptah
from ptah import util
from ptah import props

def not_none(x, msg):
	if x == None:
		raise util.CheckError("msg")

def one_of(val, vals, id):
	val = val.lower()
	for i in range(0, len(vals)):
		if val == vals[i]:
			return i
	raise util.CheckError("%s must be one of %s" % (id, vals))

def check_image(path, page):
	if not os.path.exists(os.path.join(page.album.get_base(), path)):
		raise util.CheckError("no image on path '%s'" % path)

def get_image(path, page):
	check_image(path, page)
	page.image = path

def get_image1(path, page):
	check_image(path, page)
	page.image1 = path

def get_image2(path, page):
	check_image(path, page)
	page.image2 = path

def get_orientation(val, page):
	page.orientation = one_of(
		val,
		["vertical", "horizontal"],
		"orientation")

PROP_NAME = props.StringProperty("name", "name")
PROP_IMAGE = props.ImageProperty("image", "image")
PROP_IMAGE1 = props.ImageProperty("image1", "image")
PROP_IMAGE2 = props.ImageProperty("image2", "image")
PROP_ORIENTATION = props.EnumProperty(
	"orientation", "orientation", ["vertical", "horizontal"])

def add(props, prop):
	props[prop.id] = prop

# Center page
class CenterPage(ptah.Page):

	NAME = "center"
	PROPS = props.make([PROP_NAME, PROP_IMAGE])

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
			fill = "gray"
		)
		drawer.draw_text(
			0, 0,
			drawer.width, drawer.height,
			"image"
		)

# Duo page
class DuoPage(ptah.Page):

	NAME = "duo"
	PROPS = props.make([
		PROP_NAME,
		PROP_IMAGE1,
		PROP_IMAGE2,
		PROP_ORIENTATION
	])

	def __init__(self):
		ptah.Page.__init__(self)
		self.image1 = None
		self.image2 = None
		self.orientation = 0

	def check(self):
		not_none(self.image1, "no image1 provided")
		not_none(self.image2, "no image2 provided")

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
		drawer.draw_image(self.image1, x1, y1, w, h)
		drawer.draw_image(self.image2, x2, y2, w, h)

	def gen_miniature(drawer):
		h = (drawer.height - 2)/2.
		drawer.draw_box(
			0, 0,
			drawer.width, h,
			draw = "black",
			fill = "gray"
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
			fill = "gray"
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
